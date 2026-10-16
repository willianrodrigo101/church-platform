from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.permissions import filtrar_oracoes_por_role
from app.modules.oracao.models import PedidoOracao


class PedidoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict) -> PedidoOracao:
        obj = PedidoOracao(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar_por_id(self, obj_id: UUID) -> PedidoOracao | None:
        r = await self.db.execute(select(PedidoOracao).where(PedidoOracao.id == obj_id))
        return r.scalar_one_or_none()

    async def listar(
        self, skip=0, limit=100,
        pessoa_id=None, igreja_id=None, categoria=None, status=None,
        apenas_ativos=False, apenas_sigilosos=None,
        autor_id=None, incluir_sigilosos=False,
        usuario=None,
    ) -> list[PedidoOracao]:
        stmt = select(PedidoOracao).order_by(PedidoOracao.data_pedido.desc())
        if pessoa_id: stmt = stmt.where(PedidoOracao.pessoa_id == pessoa_id)
        if igreja_id: stmt = stmt.where(PedidoOracao.igreja_id == igreja_id)
        if categoria: stmt = stmt.where(PedidoOracao.categoria == categoria)
        if status: stmt = stmt.where(PedidoOracao.status == status)
        if apenas_ativos: stmt = stmt.where(PedidoOracao.ativo.is_(True))
        if apenas_sigilosos is True: stmt = stmt.where(PedidoOracao.sigiloso.is_(True))
        elif apenas_sigilosos is False: stmt = stmt.where(PedidoOracao.sigiloso.is_(False))

        # Filtro de role (membro so ve publicas + as proprias)
        if usuario is not None:
            stmt = filtrar_oracoes_por_role(stmt, PedidoOracao, usuario)

        if not incluir_sigilosos:
            stmt = stmt.where(
                (PedidoOracao.sigiloso.is_(False)) |
                (PedidoOracao.responsavel_id == autor_id)
            )
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def atualizar(self, obj: PedidoOracao, dados: dict) -> PedidoOracao:
        for k, v in dados.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def deletar(self, obj: PedidoOracao) -> None:
        await self.db.delete(obj)
        await self.db.flush()

    # ============ ANALITICOS ============

    async def contar(self, igreja_id=None, autor_id=None, incluir_sigilosos=False) -> int:
        stmt = select(func.count(PedidoOracao.id)).where(PedidoOracao.ativo.is_(True))
        if igreja_id: stmt = stmt.where(PedidoOracao.igreja_id == igreja_id)
        if not incluir_sigilosos:
            stmt = stmt.where(
                (PedidoOracao.sigiloso.is_(False)) |
                (PedidoOracao.responsavel_id == autor_id)
            )
        r = await self.db.execute(stmt)
        return r.scalar_one()

    async def contar_por_status(self, status: str, igreja_id=None, autor_id=None, incluir_sigilosos=False) -> int:
        stmt = select(func.count(PedidoOracao.id)).where(
            PedidoOracao.ativo.is_(True), PedidoOracao.status == status,
        )
        if igreja_id: stmt = stmt.where(PedidoOracao.igreja_id == igreja_id)
        if not incluir_sigilosos:
            stmt = stmt.where(
                (PedidoOracao.sigiloso.is_(False)) |
                (PedidoOracao.responsavel_id == autor_id)
            )
        r = await self.db.execute(stmt)
        return r.scalar_one()

    async def por_categoria(self, igreja_id=None, autor_id=None, incluir_sigilosos=False) -> dict:
        stmt = (
            select(PedidoOracao.categoria, func.count(PedidoOracao.id))
            .where(PedidoOracao.ativo.is_(True))
            .group_by(PedidoOracao.categoria)
        )
        if igreja_id: stmt = stmt.where(PedidoOracao.igreja_id == igreja_id)
        if not incluir_sigilosos:
            stmt = stmt.where(
                (PedidoOracao.sigiloso.is_(False)) |
                (PedidoOracao.responsavel_id == autor_id)
            )
        r = await self.db.execute(stmt)
        return {row[0]: row[1] for row in r.all()}

    async def sem_resposta(self, igreja_id=None, autor_id=None, incluir_sigilosos=False, dias=30) -> list[PedidoOracao]:
        limite = date.today() - timedelta(days=dias)
        stmt = (
            select(PedidoOracao)
            .where(
                PedidoOracao.ativo.is_(True),
                PedidoOracao.data_pedido < limite,
                PedidoOracao.status.in_(["aberto", "em_oracao"]),
            )
            .order_by(PedidoOracao.data_pedido.asc())
            .limit(50)
        )
        if igreja_id: stmt = stmt.where(PedidoOracao.igreja_id == igreja_id)
        if not incluir_sigilosos:
            stmt = stmt.where(
                (PedidoOracao.sigiloso.is_(False)) |
                (PedidoOracao.responsavel_id == autor_id)
            )
        r = await self.db.execute(stmt)
        return list(r.scalars().all())