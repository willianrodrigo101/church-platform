from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.igreja.models import Igreja


class IgrejaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict) -> Igreja:
        igreja = Igreja(**dados)
        self.db.add(igreja)
        await self.db.flush()
        await self.db.refresh(igreja)
        return igreja

    async def buscar_por_id(self, igreja_id: UUID) -> Igreja | None:
        result = await self.db.execute(
            select(Igreja).where(Igreja.id == igreja_id)
        )
        return result.scalar_one_or_none()

    async def listar(
        self,
        skip: int = 0,
        limit: int = 100,
        apenas_ativas: bool = False,
    ) -> list[Igreja]:
        stmt = select(Igreja).order_by(Igreja.nome.asc())

        if apenas_ativas:
            stmt = stmt.where(Igreja.ativa.is_(True))

        stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def atualizar(self, igreja: Igreja, dados: dict) -> Igreja:
        for k, v in dados.items():
            if v is not None:
                setattr(igreja, k, v)
        await self.db.flush()
        await self.db.refresh(igreja)
        return igreja

    async def deletar(self, igreja: Igreja) -> None:
        await self.db.delete(igreja)
        await self.db.flush()
