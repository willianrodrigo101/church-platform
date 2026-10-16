from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.handlers import BusinessRuleError, NotFoundError, PermissionDeniedError
from app.modules.cuidado.repository import AcompanhamentoRepository
from app.modules.pessoas.repository import PessoaRepository
from app.modules.usuarios.models import Usuario

DIAS_SEM_INTERACAO = 30


class AcompanhamentoService:
    def __init__(self, db: AsyncSession):
        self.repo = AcompanhamentoRepository(db)
        self.pessoa_repo = PessoaRepository(db)
        self.db = db

    def _pode_ver(self, obj, usuario: Usuario) -> bool:
        # Membro nunca ve acompanhamentos
        if usuario.role == "membro":
            return False
        if not obj.sigiloso:
            return True
        if usuario.role == "admin":
            return True
        return str(obj.responsavel_id) == str(usuario.id)

    def _pode_editar(self, obj, usuario: Usuario) -> bool:
        # Membro nunca edita acompanhamentos
        if usuario.role == "membro":
            return False
        if usuario.role == "admin":
            return True
        return str(obj.responsavel_id) == str(usuario.id)

    async def criar(self, dados: dict, autor: Usuario):
        pessoa = await self.pessoa_repo.buscar_por_id(dados["pessoa_id"])
        if not pessoa:
            raise BusinessRuleError("Pessoa informada nao existe")
        if not pessoa.ativo:
            raise BusinessRuleError("Nao e possivel criar acompanhamento para pessoa inativa")

        dados["igreja_id"] = pessoa.igreja_id
        dados["responsavel_id"] = autor.id
        return await self.repo.criar(dados)

    async def buscar(self, obj_id: UUID, usuario: Usuario):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Acompanhamento", str(obj_id))
        if not self._pode_ver(obj, usuario):
            raise PermissionDeniedError("ver acompanhamento sigiloso de outro responsavel")
        return obj

    async def listar(self, usuario: Usuario, skip: int = 0, limit: int = 100,
                     pessoa_id=None, igreja_id=None, tipo=None, status=None,
                     apenas_ativos=False, apenas_vencidos=False):
        incluir_sigilosos = usuario.role == "admin"
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        return await self.repo.listar(
            skip, limit, pessoa_id, igreja_id, tipo, status,
            apenas_ativos, apenas_vencidos,
            autor_id=usuario.id, incluir_sigilosos=incluir_sigilosos,
            usuario=usuario,
        )

    async def atualizar(self, obj_id: UUID, dados: dict, usuario: Usuario):
        obj = await self.buscar(obj_id, usuario)
        if not self._pode_editar(obj, usuario):
            raise PermissionDeniedError("editar acompanhamento de outro responsavel")
        if dados.get("status") == "concluido":
            from datetime import datetime
            obj.concluido_em = datetime.now()
        return await self.repo.atualizar(obj, dados)

    async def concluir(self, obj_id: UUID, usuario: Usuario):
        obj = await self.buscar(obj_id, usuario)
        if not self._pode_editar(obj, usuario):
            raise PermissionDeniedError("concluir acompanhamento de outro responsavel")
        if obj.status == "concluido":
            raise BusinessRuleError("Acompanhamento ja esta concluido")
        return await self.repo.atualizar(obj, {"status": "concluido"})

    async def reabrir(self, obj_id: UUID, usuario: Usuario):
        obj = await self.buscar(obj_id, usuario)
        if not self._pode_editar(obj, usuario):
            raise PermissionDeniedError("reabrir acompanhamento de outro responsavel")
        if obj.status != "concluido":
            raise BusinessRuleError("Apenas acompanhamentos concluidos podem ser reabertos")
        return await self.repo.atualizar(obj, {"status": "pendente"})

    async def deletar(self, obj_id: UUID, usuario: Usuario):
        obj = await self.buscar(obj_id, usuario)
        if not self._pode_editar(obj, usuario):
            raise PermissionDeniedError("excluir acompanhamento de outro responsavel")
        await self.repo.deletar(obj)

    async def dashboard(self, usuario: Usuario, igreja_id=None):
        from app.modules.pessoas.repository import PessoaRepository
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id

        repo_pessoa = PessoaRepository(self.db)
        pessoas = await repo_pessoa.listar(apenas_ativos=True, igreja_id=igreja_id, limit=10000)

        sem_interacao = await self.repo.pessoas_sem_interacao(igreja_id=igreja_id, dias=DIAS_SEM_INTERACAO)
        pendentes = await self.repo.contar_pendentes(igreja_id=igreja_id)
        vencidos = await self.repo.vencidos(igreja_id=igreja_id)
        proximos = await self.repo.retornos_proximos(igreja_id=igreja_id, dias=7)

        return {
            "total_pessoas": len(pessoas),
            "total_ativas": len([p for p in pessoas if p.ativo]),
            "pessoas_sem_interacao": sem_interacao,
            "acompanhamentos_pendentes": pendentes,
            "acompanhamentos_vencidos": [
                {
                    "id": v.id, "titulo": v.titulo, "tipo": v.tipo,
                    "data_retorno": v.data_retorno,
                    "dias_atraso": (date.today() - v.data_retorno).days,
                    "pessoa_nome": v.pessoa.nome if v.pessoa else "?",
                    "responsavel_nome": v.responsavel.nome if v.responsavel else "?",
                }
                for v in vencidos
            ],
            "retornos_proximos_7_dias": [
                {
                    "id": v.id, "titulo": v.titulo, "tipo": v.tipo,
                    "data_retorno": v.data_retorno,
                    "dias_atraso": 0,
                    "pessoa_nome": v.pessoa.nome if v.pessoa else "?",
                    "responsavel_nome": v.responsavel.nome if v.responsavel else "?",
                }
                for v in proximos
            ],
            "dias_sem_interacao": DIAS_SEM_INTERACAO,
        }