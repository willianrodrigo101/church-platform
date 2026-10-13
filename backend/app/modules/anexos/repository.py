from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.anexos.models import Anexo


class AnexoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict) -> Anexo:
        obj = Anexo(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar_por_id(self, obj_id: UUID) -> Anexo | None:
        r = await self.db.execute(select(Anexo).where(Anexo.id == obj_id))
        return r.scalar_one_or_none()

    async def listar(
        self,
        entidade_tipo: str | None = None,
        entidade_id: UUID | None = None,
        igreja_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Anexo]:
        stmt = select(Anexo).order_by(Anexo.created_at.desc())
        if entidade_tipo:
            stmt = stmt.where(Anexo.entidade_tipo == entidade_tipo)
        if entidade_id:
            stmt = stmt.where(Anexo.entidade_id == entidade_id)
        if igreja_id:
            stmt = stmt.where(Anexo.igreja_id == igreja_id)
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def deletar(self, obj: Anexo) -> None:
        await self.db.delete(obj)
        await self.db.flush()
