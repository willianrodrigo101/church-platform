from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.usuarios.models import Usuario


class UsuarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict) -> Usuario:
        usuario = Usuario(**dados)
        self.db.add(usuario)
        await self.db.flush()
        await self.db.refresh(usuario)
        return usuario

    async def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        r = await self.db.execute(select(Usuario).where(Usuario.id == usuario_id))
        return r.scalar_one_or_none()

    async def buscar_por_email(self, email: str) -> Usuario | None:
        r = await self.db.execute(select(Usuario).where(Usuario.email == email))
        return r.scalar_one_or_none()

    async def contar(self) -> int:
        r = await self.db.execute(select(func.count(Usuario.id)))
        return r.scalar_one()

    async def contar_admins_ativos(self) -> int:
        r = await self.db.execute(
            select(func.count(Usuario.id)).where(
                Usuario.role == "admin",
                Usuario.ativo.is_(True),
            )
        )
        return r.scalar_one()

    async def listar(
        self,
        skip: int = 0,
        limit: int = 100,
        role: str | None = None,
        igreja_id: UUID | None = None,
        apenas_ativos: bool = False,
    ) -> list[Usuario]:
        stmt = select(Usuario).order_by(Usuario.nome.asc())
        if role:
            stmt = stmt.where(Usuario.role == role)
        if igreja_id:
            stmt = stmt.where(Usuario.igreja_id == igreja_id)
        if apenas_ativos:
            stmt = stmt.where(Usuario.ativo.is_(True))
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def atualizar(self, usuario: Usuario, dados: dict) -> Usuario:
        for k, v in dados.items():
            if v is not None:
                setattr(usuario, k, v)
        await self.db.flush()
        await self.db.refresh(usuario)
        return usuario

    async def deletar(self, usuario: Usuario) -> None:
        await self.db.delete(usuario)
        await self.db.flush()
