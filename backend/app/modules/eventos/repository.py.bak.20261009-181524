from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.eventos.models import Evento, Inscricao


class EventoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict) -> Evento:
        obj = Evento(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar_por_id(self, obj_id: UUID) -> Evento | None:
        r = await self.db.execute(select(Evento).where(Evento.id == obj_id))
        return r.scalar_one_or_none()

    async def listar(
        self,
        skip: int = 0,
        limit: int = 100,
        igreja_id: UUID | None = None,
        tipo: str | None = None,
        apenas_ativos: bool = False,
        data_de: datetime | None = None,
        data_ate: datetime | None = None,
        apenas_publicos: bool = False,
    ) -> list[Evento]:
        stmt = select(Evento).order_by(Evento.data_inicio.asc())
        if igreja_id:
            stmt = stmt.where(Evento.igreja_id == igreja_id)
        if tipo:
            stmt = stmt.where(Evento.tipo == tipo)
        if apenas_ativos:
            stmt = stmt.where(Evento.ativo.is_(True))
        if apenas_publicos:
            stmt = stmt.where(Evento.publico.is_(True))
        if data_de:
            stmt = stmt.where(Evento.data_inicio >= data_de)
        if data_ate:
            stmt = stmt.where(Evento.data_inicio <= data_ate)
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def atualizar(self, obj: Evento, dados: dict) -> Evento:
        for k, v in dados.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def deletar(self, obj: Evento) -> None:
        await self.db.delete(obj)
        await self.db.flush()

    async def proximos(self, igreja_id=None, dias: int = 7, apenas_publicos: bool = False) -> list[Evento]:
        agora = datetime.now(timezone.utc)
        limite = agora + timedelta(days=dias)
        stmt = (
            select(Evento)
            .where(
                Evento.data_inicio >= agora,
                Evento.data_inicio <= limite,
                Evento.ativo.is_(True),
            )
            .order_by(Evento.data_inicio.asc())
        )
        if igreja_id:
            stmt = stmt.where(Evento.igreja_id == igreja_id)
        if apenas_publicos:
            stmt = stmt.where(Evento.publico.is_(True))
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def contar_inscricoes(self, evento_id: UUID) -> int:
        r = await self.db.execute(
            select(func.count(Inscricao.id)).where(Inscricao.evento_id == evento_id)
        )
        return r.scalar_one()

    async def contar_inscricoes_por_evento(self, evento_ids: list[UUID]) -> dict[UUID, int]:
        if not evento_ids:
            return {}
        r = await self.db.execute(
            select(Inscricao.evento_id, func.count(Inscricao.id))
            .where(Inscricao.evento_id.in_(evento_ids))
            .group_by(Inscricao.evento_id)
        )
        return {row[0]: row[1] for row in r.all()}

    async def contar_presentes_por_evento(self, evento_ids: list[UUID]) -> dict[UUID, int]:
        if not evento_ids:
            return {}
        r = await self.db.execute(
            select(Inscricao.evento_id, func.count(Inscricao.id))
            .where(Inscricao.evento_id.in_(evento_ids), Inscricao.status == "presente")
            .group_by(Inscricao.evento_id)
        )
        return {row[0]: row[1] for row in r.all()}


class InscricaoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict) -> Inscricao:
        obj = Inscricao(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar_por_id(self, obj_id: UUID) -> Inscricao | None:
        r = await self.db.execute(select(Inscricao).where(Inscricao.id == obj_id))
        return r.scalar_one_or_none()

    async def buscar_por_evento_e_pessoa(self, evento_id: UUID, pessoa_id: UUID) -> Inscricao | None:
        r = await self.db.execute(
            select(Inscricao).where(
                Inscricao.evento_id == evento_id,
                Inscricao.pessoa_id == pessoa_id,
            )
        )
        return r.scalar_one_or_none()

    async def listar_por_evento(self, evento_id: UUID) -> list[Inscricao]:
        r = await self.db.execute(
            select(Inscricao).where(Inscricao.evento_id == evento_id).order_by(Inscricao.created_at.asc())
        )
        return list(r.scalars().all())

    async def listar_por_pessoa(self, pessoa_id: UUID, igreja_id: UUID | None = None) -> list[Inscricao]:
        stmt = select(Inscricao).where(Inscricao.pessoa_id == pessoa_id).order_by(Inscricao.created_at.desc())
        if igreja_id:
            stmt = stmt.where(Inscricao.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def atualizar(self, obj: Inscricao, dados: dict) -> Inscricao:
        for k, v in dados.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def deletar(self, obj: Inscricao) -> None:
        await self.db.delete(obj)
        await self.db.flush()
