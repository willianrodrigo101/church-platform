from datetime import date, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.cuidado.models import Acompanhamento
from app.modules.pessoas.models import Pessoa


class AcompanhamentoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict) -> Acompanhamento:
        obj = Acompanhamento(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar_por_id(self, obj_id: UUID) -> Acompanhamento | None:
        r = await self.db.execute(select(Acompanhamento).where(Acompanhamento.id == obj_id))
        return r.scalar_one_or_none()

    async def listar(
        self, skip: int = 0, limit: int = 100,
        pessoa_id: UUID | None = None, igreja_id: UUID | None = None,
        tipo: str | None = None, status: str | None = None,
        apenas_ativos: bool = False, apenas_vencidos: bool = False,
        apenas_sigilosos: bool | None = None,
        autor_id: UUID | None = None, incluir_sigilosos: bool = False,
    ) -> list[Acompanhamento]:
        stmt = select(Acompanhamento).order_by(Acompanhamento.data.desc())

        if pessoa_id: stmt = stmt.where(Acompanhamento.pessoa_id == pessoa_id)
        if igreja_id: stmt = stmt.where(Acompanhamento.igreja_id == igreja_id)
        if tipo: stmt = stmt.where(Acompanhamento.tipo == tipo)
        if status: stmt = stmt.where(Acompanhamento.status == status)
        if apenas_ativos: stmt = stmt.where(Acompanhamento.ativo.is_(True))
        if apenas_vencidos:
            hoje = date.today()
            stmt = stmt.where(
                Acompanhamento.data_retorno < hoje,
                Acompanhamento.status.in_(["pendente", "em_andamento"]),
            )

        # Regra de sigilo: se nao pode ver sigilosos, so ve os proprios
        if not incluir_sigilosos:
            stmt = stmt.where(
                (Acompanhamento.sigiloso.is_(False)) |
                (Acompanhamento.responsavel_id == autor_id)
            )

        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def atualizar(self, obj: Acompanhamento, dados: dict) -> Acompanhamento:
        for k, v in dados.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def deletar(self, obj: Acompanhamento) -> None:
        await self.db.delete(obj)
        await self.db.flush()

    # ============ ANALITICOS (DASHBOARD) ============

    async def contar_pendentes(self, igreja_id: UUID | None = None) -> int:
        stmt = select(func.count(Acompanhamento.id)).where(
            Acompanhamento.status.in_(["pendente", "em_andamento"]),
            Acompanhamento.ativo.is_(True),
        )
        if igreja_id: stmt = stmt.where(Acompanhamento.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        return r.scalar_one()

    async def vencidos(self, igreja_id: UUID | None = None) -> list[Acompanhamento]:
        hoje = date.today()
        stmt = (
            select(Acompanhamento)
            .where(
                Acompanhamento.data_retorno < hoje,
                Acompanhamento.status.in_(["pendente", "em_andamento"]),
                Acompanhamento.ativo.is_(True),
            )
            .order_by(Acompanhamento.data_retorno.asc())
            .limit(50)
        )
        if igreja_id: stmt = stmt.where(Acompanhamento.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def retornos_proximos(self, igreja_id: UUID | None = None, dias: int = 7) -> list[Acompanhamento]:
        hoje = date.today()
        limite = hoje + timedelta(days=dias)
        stmt = (
            select(Acompanhamento)
            .where(
                Acompanhamento.data_retorno >= hoje,
                Acompanhamento.data_retorno <= limite,
                Acompanhamento.status.in_(["pendente", "em_andamento"]),
                Acompanhamento.ativo.is_(True),
            )
            .order_by(Acompanhamento.data_retorno.asc())
            .limit(50)
        )
        if igreja_id: stmt = stmt.where(Acompanhamento.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def pessoas_sem_interacao(self, igreja_id: UUID | None = None, dias: int = 30) -> list[dict]:
        limite = datetime.now().astimezone() - timedelta(days=dias)
        stmt = select(Pessoa).where(Pessoa.ativo.is_(True))
        if igreja_id: stmt = stmt.where(Pessoa.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        pessoas = list(r.scalars().all())

        resultado = []
        for p in pessoas:
            r2 = await self.db.execute(
                select(func.max(Acompanhamento.data)).where(
                    Acompanhamento.pessoa_id == p.id,
                    Acompanhamento.ativo.is_(True),
                )
            )
            ultima = r2.scalar_one_or_none()
            if ultima is None or ultima < limite.date():
                dias_sem = (date.today() - ultima).days if ultima else None
                resultado.append({
                    "id": p.id, "nome": p.nome, "email": p.email, "telefone": p.telefone,
                    "ultima_interacao": datetime.combine(ultima, datetime.min.time()) if ultima else None,
                    "dias_sem_interacao": dias_sem,
                })
        resultado.sort(key=lambda x: (x["dias_sem_interacao"] is None, -(x["dias_sem_interacao"] or 0)))
        return resultado[:50]
