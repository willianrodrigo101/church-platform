from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.handlers import BusinessRuleError, NotFoundError, PermissionDeniedError
from app.modules.oracao.repository import PedidoRepository
from app.modules.pessoas.repository import PessoaRepository
from app.modules.usuarios.models import Usuario

DIAS_SEM_RESPOSTA = 30


class PedidoService:
    def __init__(self, db: AsyncSession):
        self.repo = PedidoRepository(db)
        self.pessoa_repo = PessoaRepository(db)
        self.db = db

    def _pode_ver(self, obj, usuario):
        if not obj.sigiloso: return True
        if usuario.role == "admin": return True
        return str(obj.responsavel_id) == str(usuario.id)

    def _pode_editar(self, obj, usuario):
        if usuario.role == "admin": return True
        return str(obj.responsavel_id) == str(usuario.id)

    async def criar(self, dados: dict, autor: Usuario):
        pessoa_id = dados.get("pessoa_id")
        igreja_id = None

        if pessoa_id:
            pessoa = await self.pessoa_repo.buscar_por_id(pessoa_id)
            if not pessoa:
                raise BusinessRuleError("Pessoa informada nao existe")
            if not pessoa.ativo:
                raise BusinessRuleError("Nao e possivel criar pedido para pessoa inativa")
            igreja_id = pessoa.igreja_id
        else:
            # Sem pessoa -> igreja do autor (obrigatorio)
            if not autor.igreja_id:
                raise BusinessRuleError("Autor sem igreja vinculada. Informe uma pessoa.")
            igreja_id = autor.igreja_id

        dados["igreja_id"] = igreja_id
        dados["responsavel_id"] = autor.id
        return await self.repo.criar(dados)

    async def buscar(self, obj_id: UUID, usuario: Usuario):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Pedido de Oracao", str(obj_id))
        if not self._pode_ver(obj, usuario):
            raise PermissionDeniedError("ver pedido sigiloso")
        return obj

    async def listar(self, usuario, skip=0, limit=100,
                     pessoa_id=None, igreja_id=None, categoria=None, status=None,
                     apenas_ativos=False, apenas_sigilosos=None):
        incluir_sigilosos = usuario.role == "admin"
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        return await self.repo.listar(
            skip, limit, pessoa_id, igreja_id, categoria, status,
            apenas_ativos, apenas_sigilosos,
            autor_id=usuario.id, incluir_sigilosos=incluir_sigilosos,
        )

    async def atualizar(self, obj_id: UUID, dados: dict, usuario):
        obj = await self.buscar(obj_id, usuario)
        if not self._pode_editar(obj, usuario):
            raise PermissionDeniedError("editar pedido sigiloso de outro responsavel")
        return await self.repo.atualizar(obj, dados)

    async def marcar_atendido(self, obj_id: UUID, testemunho, data_resposta, usuario):
        obj = await self.buscar(obj_id, usuario)
        if not self._pode_editar(obj, usuario):
            raise PermissionDeniedError("editar pedido sigiloso de outro responsavel")
        if obj.status == "atendido":
            raise BusinessRuleError("Pedido ja esta marcado como atendido")
        dados = {
            "status": "atendido",
            "data_resposta": data_resposta or date.today(),
        }
        if testemunho:
            dados["testemunho"] = testemunho
        return await self.repo.atualizar(obj, dados)

    async def reabrir(self, obj_id: UUID, usuario):
        obj = await self.buscar(obj_id, usuario)
        if not self._pode_editar(obj, usuario):
            raise PermissionDeniedError("reabrir pedido sigiloso de outro responsavel")
        if obj.status != "atendido":
            raise BusinessRuleError("Apenas pedidos atendidos podem ser reabertos")
        return await self.repo.atualizar(obj, {"status": "aberto", "data_resposta": None})

    async def deletar(self, obj_id: UUID, usuario):
        obj = await self.buscar(obj_id, usuario)
        if not self._pode_editar(obj, usuario):
            raise PermissionDeniedError("excluir pedido sigiloso de outro responsavel")
        await self.repo.deletar(obj)

    async def dashboard(self, usuario, igreja_id=None):
        incluir = usuario.role == "admin"
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id

        total = await self.repo.contar(igreja_id, usuario.id, incluir)
        abertos = await self.repo.contar_por_status("aberto", igreja_id, usuario.id, incluir)
        em_oracao = await self.repo.contar_por_status("em_oracao", igreja_id, usuario.id, incluir)
        atendidos = await self.repo.contar_por_status("atendido", igreja_id, usuario.id, incluir)
        por_categoria = await self.repo.por_categoria(igreja_id, usuario.id, incluir)
        sem_resposta = await self.repo.sem_resposta(igreja_id, usuario.id, incluir, DIAS_SEM_RESPOSTA)

        return {
            "total": total,
            "abertos": abertos,
            "em_oracao": em_oracao,
            "atendidos": atendidos,
            "sem_resposta_30d": [
                {
                    "id": p.id, "titulo": p.titulo, "categoria": p.categoria,
                    "data_pedido": p.data_pedido,
                    "dias_aberto": (date.today() - p.data_pedido).days,
                    "pessoa_nome": p.pessoa.nome if p.pessoa else None,
                    "responsavel_nome": p.responsavel.nome if p.responsavel else "?",
                }
                for p in sem_resposta
            ],
            "por_categoria": por_categoria,
        }
