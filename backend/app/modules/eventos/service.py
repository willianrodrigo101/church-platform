from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.handlers import BusinessRuleError, NotFoundError, PermissionDeniedError
from app.modules.eventos.repository import EventoRepository, InscricaoRepository
from app.modules.igreja.repository import IgrejaRepository
from app.modules.pessoas.repository import PessoaRepository
from app.modules.usuarios.models import Usuario

STATUS_VALIDOS = {"inscrito", "presente", "ausente", "cancelado"}


class EventoService:
    def __init__(self, db: AsyncSession):
        self.repo = EventoRepository(db)
        self.insc_repo = InscricaoRepository(db)
        self.pessoa_repo = PessoaRepository(db)
        self.db = db

    async def criar(self, dados: dict, autor: Usuario):
        igreja_id = dados.get("igreja_id")

        # Admin global pode escolher qualquer igreja
        # (ou usar a do usuario se tiver; senao pega a primeira ativa)
        if autor.role == "admin":
            if not igreja_id:
                if autor.igreja_id:
                    igreja_id = autor.igreja_id
                else:
                    igrejas = await IgrejaRepository(self.db).listar(apenas_ativas=True)
                    if not igrejas:
                        raise BusinessRuleError("Nenhuma igreja ativa cadastrada. Cadastre uma igreja antes.")
                    igreja_id = igrejas[0].id
        else:
            if not autor.igreja_id:
                raise BusinessRuleError("Usuario sem igreja vinculada. Vincule-se a uma igreja.")
            igreja_id = autor.igreja_id

        dados["igreja_id"] = igreja_id
        dados["responsavel_id"] = autor.id
        return await self.repo.criar(dados)

    async def buscar(self, obj_id: UUID):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Evento", str(obj_id))
        return obj

    async def listar(
        self, usuario, skip=0, limit=100,
        igreja_id=None, tipo=None, apenas_ativos=False,
        data_de=None, data_ate=None,
    ):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        return await self.repo.listar(
            skip, limit, igreja_id, tipo, apenas_ativos, data_de, data_ate,
        )

    async def atualizar(self, obj_id: UUID, dados: dict, usuario: Usuario):
        obj = await self.buscar(obj_id)
        if usuario.role != "admin" and str(obj.responsavel_id) != str(usuario.id):
            raise PermissionDeniedError("editar evento de outro responsavel")
        return await self.repo.atualizar(obj, dados)

    async def desativar(self, obj_id: UUID, usuario: Usuario):
        obj = await self.buscar(obj_id)
        if usuario.role != "admin" and str(obj.responsavel_id) != str(usuario.id):
            raise PermissionDeniedError("desativar evento de outro responsavel")
        if not obj.ativo:
            raise BusinessRuleError("Evento ja esta desativado")
        return await self.repo.atualizar(obj, {"ativo": False})

    async def reativar(self, obj_id: UUID, usuario: Usuario):
        obj = await self.buscar(obj_id)
        if obj.ativo:
            raise BusinessRuleError("Evento ja esta ativo")
        return await self.repo.atualizar(obj, {"ativo": True})

    async def deletar(self, obj_id: UUID, usuario: Usuario):
        obj = await self.buscar(obj_id)
        if usuario.role != "admin" and str(obj.responsavel_id) != str(usuario.id):
            raise PermissionDeniedError("excluir evento de outro responsavel")
        total = await self.repo.contar_inscricoes(obj_id)
        if total > 0:
            raise BusinessRuleError(
                f"Nao e possivel excluir: {total} inscricao(oes) vinculada(s) a este evento. "
                "Desative o evento em vez de exclui-lo."
            )
        await self.repo.deletar(obj)

    async def dashboard(self, usuario, igreja_id=None):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id

        proximos_7 = await self.repo.proximos(igreja_id=igreja_id, dias=7)
        proximos_30 = await self.repo.proximos(igreja_id=igreja_id, dias=30)

        ids_7 = [e.id for e in proximos_7]
        contagens = await self.repo.contar_inscricoes_por_evento(ids_7)

        agora = datetime.now(timezone.utc)
        itens = [
            {
                "id": e.id,
                "titulo": e.titulo,
                "tipo": e.tipo,
                "data_inicio": e.data_inicio,
                "local": e.local,
                "vagas": e.vagas,
                "total_inscritos": contagens.get(e.id, 0),
                "dias_para_evento": max(0, (e.data_inicio - agora).days),
            }
            for e in proximos_7
        ]

        return {
            "total_proximos_7d": len(proximos_7),
            "total_proximos_30d": len(proximos_30),
            "proximos_eventos": itens,
            "proximos": itens,
        }


class InscricaoService:
    def __init__(self, db: AsyncSession):
        self.repo = InscricaoRepository(db)
        self.evento_repo = EventoRepository(db)
        self.pessoa_repo = PessoaRepository(db)
        self.db = db

    async def criar(self, evento_id: UUID, pessoa_id: UUID, observacao, usuario: Usuario):
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise NotFoundError("Evento", str(evento_id))
        if not evento.ativo:
            raise BusinessRuleError("Evento desativado. Nao aceita novas inscricoes.")

        pessoa = await self.pessoa_repo.buscar_por_id(pessoa_id)
        if not pessoa:
            raise BusinessRuleError("Pessoa informada nao existe")
        if not pessoa.ativo:
            raise BusinessRuleError("Pessoa inativa")

        if str(pessoa.igreja_id) != str(evento.igreja_id):
            raise BusinessRuleError("Pessoa e evento pertencem a igrejas diferentes")

        existente = await self.repo.buscar_por_evento_e_pessoa(evento_id, pessoa_id)
        if existente:
            raise BusinessRuleError("Esta pessoa ja esta inscrita neste evento")

        if evento.vagas is not None:
            total = await self.evento_repo.contar_inscricoes(evento_id)
            if total >= evento.vagas:
                raise BusinessRuleError("Evento lotado. Nao ha mais vagas.")

        dados = {
            "evento_id": evento_id,
            "pessoa_id": pessoa_id,
            "igreja_id": evento.igreja_id,
            "observacao": observacao,
        }
        return await self.repo.criar(dados)

    async def listar_por_evento(self, evento_id: UUID):
        evento = await self.evento_repo.buscar_por_id(evento_id)
        if not evento:
            raise NotFoundError("Evento", str(evento_id))
        return await self.repo.listar_por_evento(evento_id)

    async def listar_por_pessoa(self, pessoa_id: UUID):
        return await self.repo.listar_por_pessoa(pessoa_id)

    async def checkin(self, inscricao_id: UUID, status: str, observacao, usuario: Usuario):
        obj = await self.repo.buscar_por_id(inscricao_id)
        if not obj:
            raise NotFoundError("Inscricao", str(inscricao_id))
        if status not in STATUS_VALIDOS:
            raise BusinessRuleError(f"Status invalido: {status}")
        dados = {"status": status}
        if observacao:
            dados["observacao"] = observacao
        return await self.repo.atualizar(obj, dados)

    async def deletar(self, inscricao_id: UUID, usuario: Usuario):
        obj = await self.repo.buscar_por_id(inscricao_id)
        if not obj:
            raise NotFoundError("Inscricao", str(inscricao_id))
        await self.repo.deletar(obj)