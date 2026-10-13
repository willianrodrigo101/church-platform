from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.jornada.models import (
    EtapaTrilha,
    Progresso,
    ProgressoEtapa,
    Trilha,
)


class TrilhaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict, etapas: list[dict]) -> Trilha:
        trilha = Trilha(**dados)
        self.db.add(trilha)
        await self.db.flush()
        for e in etapas:
            etapa = EtapaTrilha(trilha_id=trilha.id, **e)
            self.db.add(etapa)
        await self.db.flush()
        await self.db.refresh(trilha)
        return trilha

    async def buscar_por_id(self, obj_id: UUID) -> Trilha | None:
        r = await self.db.execute(select(Trilha).where(Trilha.id == obj_id))
        return r.scalar_one_or_none()

    async def listar(
        self, skip=0, limit=100,
        igreja_id=None, tipo=None, apenas_ativas=False,
    ) -> list[Trilha]:
        stmt = (
            select(Trilha)
            .options(selectinload(Trilha.etapas))
            .order_by(Trilha.nome.asc())
        )
        if igreja_id: stmt = stmt.where(Trilha.igreja_id == igreja_id)
        if tipo: stmt = stmt.where(Trilha.tipo == tipo)
        if apenas_ativas: stmt = stmt.where(Trilha.ativa.is_(True))
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.unique().scalars().all())

    async def atualizar(self, obj: Trilha, dados: dict) -> Trilha:
        for k, v in dados.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def deletar(self, obj: Trilha) -> None:
        await self.db.delete(obj)
        await self.db.flush()

    async def contar_progressos(self, trilha_id: UUID) -> int:
        r = await self.db.execute(
            select(func.count(Progresso.id)).where(Progresso.trilha_id == trilha_id)
        )
        return r.scalar_one()

    async def contar_progressos_por_trilha(self, trilha_ids: list[UUID]) -> dict[UUID, int]:
        if not trilha_ids:
            return {}
        r = await self.db.execute(
            select(Progresso.trilha_id, func.count(Progresso.id))
            .where(Progresso.trilha_id.in_(trilha_ids))
            .group_by(Progresso.trilha_id)
        )
        return {row[0]: row[1] for row in r.all()}

    async def contar_concluidos_por_trilha(self, trilha_ids: list[UUID]) -> dict[UUID, int]:
        if not trilha_ids:
            return {}
        r = await self.db.execute(
            select(Progresso.trilha_id, func.count(Progresso.id))
            .where(Progresso.trilha_id.in_(trilha_ids), Progresso.status == "concluida")
            .group_by(Progresso.trilha_id)
        )
        return {row[0]: row[1] for row in r.all()}


class ProgressoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict, etapas_ids: list[UUID]) -> Progresso:
        prog = Progresso(**dados)
        self.db.add(prog)
        await self.db.flush()
        for etapa_id in etapas_ids:
            pe = ProgressoEtapa(progresso_id=prog.id, etapa_id=etapa_id, concluida=False)
            self.db.add(pe)
        await self.db.flush()
        await self.db.refresh(prog)
        return prog

    async def buscar_por_id(self, obj_id: UUID) -> Progresso | None:
        stmt = (
            select(Progresso)
            .options(
                selectinload(Progresso.etapas).selectinload(ProgressoEtapa.etapa),
                selectinload(Progresso.trilha).selectinload(Trilha.etapas),
            )
            .where(Progresso.id == obj_id)
        )
        r = await self.db.execute(stmt)
        return r.unique().scalar_one_or_none()

    async def buscar_por_pessoa_e_trilha(self, pessoa_id: UUID, trilha_id: UUID) -> Progresso | None:
        r = await self.db.execute(
            select(Progresso).where(
                Progresso.pessoa_id == pessoa_id,
                Progresso.trilha_id == trilha_id,
            )
        )
        return r.scalar_one_or_none()

    async def buscar_etapa(self, progresso_id: UUID, etapa_id: UUID) -> ProgressoEtapa | None:
        r = await self.db.execute(
            select(ProgressoEtapa).where(
                ProgressoEtapa.progresso_id == progresso_id,
                ProgressoEtapa.etapa_id == etapa_id,
            )
        )
        return r.scalar_one_or_none()

    async def listar(
        self, skip=0, limit=100,
        igreja_id=None, pessoa_id=None, trilha_id=None, status=None,
    ) -> list[Progresso]:
        stmt = (
            select(Progresso)
            .options(
                selectinload(Progresso.etapas).selectinload(ProgressoEtapa.etapa),
                selectinload(Progresso.trilha).selectinload(Trilha.etapas),
            )
            .order_by(Progresso.created_at.desc())
        )
        if igreja_id: stmt = stmt.where(Progresso.igreja_id == igreja_id)
        if pessoa_id: stmt = stmt.where(Progresso.pessoa_id == pessoa_id)
        if trilha_id: stmt = stmt.where(Progresso.trilha_id == trilha_id)
        if status: stmt = stmt.where(Progresso.status == status)
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.unique().scalars().all())

    async def atualizar(self, obj: Progresso, dados: dict) -> Progresso:
        for k, v in dados.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def atualizar_etapa(self, pe: ProgressoEtapa, dados: dict) -> ProgressoEtapa:
        for k, v in dados.items():
            setattr(pe, k, v)
        await self.db.flush()
        await self.db.refresh(pe)
        return pe

    async def deletar(self, obj: Progresso) -> None:
        await self.db.delete(obj)
        await self.db.flush()

    async def contar_por_status(self, status: str, igreja_id=None) -> int:
        stmt = select(func.count(Progresso.id)).where(Progresso.status == status)
        if igreja_id: stmt = stmt.where(Progresso.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        return r.scalar_one()

    async def contar_concluidas_periodo(self, dias: int = 30, igreja_id=None) -> int:
        limite = date.today() - timedelta(days=dias)
        stmt = select(func.count(Progresso.id)).where(
            Progresso.status == "concluida",
            Progresso.concluido_em >= limite,
        )
        if igreja_id: stmt = stmt.where(Progresso.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        return r.scalar_one()

    async def contar_paradas_30d(self, dias: int = 30, igreja_id=None) -> int:
        limite = datetime.now(timezone.utc) - timedelta(days=dias)
        stmt = select(func.count(Progresso.id)).where(
            Progresso.status == "em_andamento",
            Progresso.updated_at < limite,
        )
        if igreja_id: stmt = stmt.where(Progresso.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        return r.scalar_one()

    async def trilhas_populares(self, igreja_id=None, limit: int = 5) -> list[dict]:
        stmt = (
            select(Trilha.nome, func.count(Progresso.id))
            .join(Progresso, Progresso.trilha_id == Trilha.id)
            .group_by(Trilha.nome)
            .order_by(func.count(Progresso.id).desc())
            .limit(limit)
        )
        if igreja_id: stmt = stmt.where(Trilha.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        return [{"trilha": row[0], "total": row[1]} for row in r.all()]