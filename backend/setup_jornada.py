"""Setup do modulo Jornada / Discipulado (trilhas + etapas + progressos)."""
import argparse, shutil
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).parent.resolve()
PROJETO = BACKEND.parent

parser = argparse.ArgumentParser()
parser.add_argument("--force", action="store_true")
args = parser.parse_args()
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

def escrever(caminho: Path, conteudo: str):
    if caminho.exists():
        if not args.force:
            print(f"  [SKIP] {caminho.relative_to(PROJETO)}")
            return
        backup = caminho.with_suffix(caminho.suffix + f".bak.{STAMP}")
        shutil.copy2(caminho, backup)
        print(f"  [BACKUP] {backup.name}")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(conteudo, encoding="utf-8")
    print(f"  [OK] {caminho.relative_to(PROJETO)}")


# ============================================================
# 1. MODELS
# ============================================================
models_py = '''from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin, UUIDMixin


class Trilha(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "trilhas"

    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default="discipulado", index=True)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    igreja = relationship("Igreja", lazy="joined")
    etapas = relationship(
        "EtapaTrilha",
        back_populates="trilha",
        cascade="all, delete-orphan",
        order_by="EtapaTrilha.ordem",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Trilha {self.nome} ({self.tipo})>"


class EtapaTrilha(Base, UUIDMixin):
    __tablename__ = "etapas_trilha"

    trilha_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("trilhas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    obrigatoria: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    trilha = relationship("Trilha", back_populates="etapas")

    def __repr__(self) -> str:
        return f"<EtapaTrilha {self.ordem}. {self.nome}>"


class Progresso(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "progressos"
    __table_args__ = (
        UniqueConstraint("pessoa_id", "trilha_id", name="uq_progressos_pessoa_trilha"),
    )

    pessoa_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pessoas.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    trilha_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("trilhas.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    responsavel_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="em_andamento", index=True)
    iniciado_em: Mapped[date] = mapped_column(Date, nullable=False)
    concluido_em: Mapped[date | None] = mapped_column(Date, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    pessoa = relationship("Pessoa", lazy="joined")
    trilha = relationship("Trilha", lazy="joined")
    igreja = relationship("Igreja", lazy="joined")
    responsavel = relationship("Usuario", lazy="joined")
    etapas = relationship(
        "ProgressoEtapa",
        back_populates="progresso",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Progresso pessoa={self.pessoa_id} trilha={self.trilha_id} ({self.status})>"


class ProgressoEtapa(Base, UUIDMixin):
    __tablename__ = "progresso_etapas"
    __table_args__ = (
        UniqueConstraint("progresso_id", "etapa_id", name="uq_progresso_etapas"),
    )

    progresso_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("progressos.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    etapa_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("etapas_trilha.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    concluida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    concluida_em: Mapped[date | None] = mapped_column(Date, nullable=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)

    progresso = relationship("Progresso", back_populates="etapas")
    etapa = relationship("EtapaTrilha", lazy="joined")

    def __repr__(self) -> str:
        return f"<ProgressoEtapa etapa={self.etapa_id} concluida={self.concluida}>"
'''

# ============================================================
# 2. SCHEMAS
# ============================================================
schemas_py = '''from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IgrejaResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class PessoaResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class UsuarioResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


# ============ TRILHAS / ETAPAS ============

class EtapaTrilhaCreate(BaseModel):
    ordem: int = Field(..., ge=1)
    nome: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    obrigatoria: bool = True


class EtapaTrilhaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    ordem: int
    nome: str
    descricao: str | None = None
    obrigatoria: bool


class TrilhaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    tipo: str = Field("discipulado", pattern="^(batismo|discipulado|lideranca|outro)$")


class TrilhaCreate(TrilhaBase):
    igreja_id: UUID | None = None
    etapas: list[EtapaTrilhaCreate] = []


class TrilhaUpdate(BaseModel):
    nome: str | None = Field(None, min_length=2, max_length=200)
    descricao: str | None = None
    tipo: str | None = Field(None, pattern="^(batismo|discipulado|lideranca|outro)$")


class TrilhaResponse(TrilhaBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    igreja_id: UUID
    ativa: bool
    created_at: datetime
    updated_at: datetime
    etapas: list[EtapaTrilhaResponse] = []
    total_progressos: int = 0
    total_concluidos: int = 0


# ============ PROGRESSOS ============

class ProgressoCreate(BaseModel):
    pessoa_id: UUID
    trilha_id: UUID
    iniciado_em: date | None = None
    observacoes: str | None = None


class ProgressoEtapaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    etapa_id: UUID
    concluida: bool
    concluida_em: date | None = None
    observacao: str | None = None
    etapa: EtapaTrilhaResponse | None = None


class ProgressoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    pessoa_id: UUID
    trilha_id: UUID
    igreja_id: UUID
    responsavel_id: UUID
    status: str
    iniciado_em: date
    concluido_em: date | None = None
    observacoes: str | None = None
    created_at: datetime
    updated_at: datetime
    pessoa: PessoaResumo | None = None
    trilha: TrilhaResponse | None = None
    responsavel: UsuarioResumo | None = None
    etapas: list[ProgressoEtapaResponse] = []
    total_etapas: int = 0
    etapas_concluidas: int = 0
    progresso_percentual: float = 0.0


class MarcarEtapaRequest(BaseModel):
    concluida: bool = True
    observacao: str | None = None


class DashboardJornada(BaseModel):
    total_trilhas_ativas: int
    total_em_andamento: int
    total_concluidas: int
    concluidas_ultimos_30_dias: int
    pessoas_paradas_30d: int
    trilhas_mais_populares: list[dict]
'''

# ============================================================
# 3. REPOSITORY
# ============================================================
repository_py = '''from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

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
        stmt = select(Trilha).order_by(Trilha.nome.asc())
        if igreja_id: stmt = stmt.where(Trilha.igreja_id == igreja_id)
        if tipo: stmt = stmt.where(Trilha.tipo == tipo)
        if apenas_ativas: stmt = stmt.where(Trilha.ativa.is_(True))
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

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
        r = await self.db.execute(select(Progresso).where(Progresso.id == obj_id))
        return r.scalar_one_or_none()

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
        stmt = select(Progresso).order_by(Progresso.created_at.desc())
        if igreja_id: stmt = stmt.where(Progresso.igreja_id == igreja_id)
        if pessoa_id: stmt = stmt.where(Progresso.pessoa_id == pessoa_id)
        if trilha_id: stmt = stmt.where(Progresso.trilha_id == trilha_id)
        if status: stmt = stmt.where(Progresso.status == status)
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

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
'''

# ============================================================
# 4. SERVICE
# ============================================================
service_py = '''from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.handlers import BusinessRuleError, NotFoundError, PermissionDeniedError
from app.modules.igreja.repository import IgrejaRepository
from app.modules.jornada.repository import ProgressoRepository, TrilhaRepository
from app.modules.pessoas.repository import PessoaRepository
from app.modules.usuarios.models import Usuario


class TrilhaService:
    def __init__(self, db: AsyncSession):
        self.repo = TrilhaRepository(db)
        self.prog_repo = ProgressoRepository(db)
        self.igreja_repo = IgrejaRepository(db)
        self.db = db

    async def criar(self, dados: dict, autor: Usuario):
        etapas = dados.pop("etapas", []) or []
        igreja_id = dados.pop("igreja_id", None)

        if autor.role == "admin":
            if not igreja_id:
                if autor.igreja_id:
                    igreja_id = autor.igreja_id
                else:
                    igrejas = await self.igreja_repo.listar(apenas_ativas=True)
                    if not igrejas:
                        raise BusinessRuleError("Nenhuma igreja ativa cadastrada.")
                    igreja_id = igrejas[0].id
        else:
            if not autor.igreja_id:
                raise BusinessRuleError("Usuario sem igreja vinculada.")
            igreja_id = autor.igreja_id

        dados["igreja_id"] = igreja_id

        # Normaliza ordem
        for i, e in enumerate(etapas, start=1):
            e["ordem"] = i

        return await self.repo.criar(dados, etapas)

    async def buscar(self, obj_id: UUID):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Trilha", str(obj_id))
        return obj

    async def listar(self, usuario, skip=0, limit=100, igreja_id=None, tipo=None, apenas_ativas=False):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        trilhas = await self.repo.listar(skip, limit, igreja_id, tipo, apenas_ativas)
        if trilhas:
            ids = [t.id for t in trilhas]
            totais = await self.repo.contar_progressos_por_trilha(ids)
            concluidos = await self.repo.contar_concluidos_por_trilha(ids)
            for t in trilhas:
                t.total_progressos = totais.get(t.id, 0)
                t.total_concluidos = concluidos.get(t.id, 0)
        return trilhas

    async def atualizar(self, obj_id: UUID, dados: dict, usuario: Usuario):
        obj = await self.buscar(obj_id)
        if usuario.role != "admin" and usuario.igreja_id and str(obj.igreja_id) != str(usuario.igreja_id):
            raise PermissionDeniedError("editar trilha de outra igreja")
        return await self.repo.atualizar(obj, dados)

    async def desativar(self, obj_id: UUID, usuario: Usuario):
        obj = await self.buscar(obj_id)
        if not obj.ativa:
            raise BusinessRuleError("Trilha ja esta desativada")
        return await self.repo.atualizar(obj, {"ativa": False})

    async def reativar(self, obj_id: UUID, usuario: Usuario):
        obj = await self.buscar(obj_id)
        if obj.ativa:
            raise BusinessRuleError("Trilha ja esta ativa")
        return await self.repo.atualizar(obj, {"ativa": True})

    async def deletar(self, obj_id: UUID, usuario: Usuario):
        obj = await self.buscar(obj_id)
        total = await self.repo.contar_progressos(obj_id)
        if total > 0:
            raise BusinessRuleError(
                f"Nao e possivel excluir: {total} pessoa(s) fazendo esta trilha. "
                "Desative a trilha em vez de exclui-la."
            )
        await self.repo.deletar(obj)


class ProgressoService:
    def __init__(self, db: AsyncSession):
        self.repo = ProgressoRepository(db)
        self.trilha_repo = TrilhaRepository(db)
        self.pessoa_repo = PessoaRepository(db)
        self.db = db

    async def criar(self, dados: dict, autor: Usuario):
        pessoa_id = dados["pessoa_id"]
        trilha_id = dados["trilha_id"]

        pessoa = await self.pessoa_repo.buscar_por_id(pessoa_id)
        if not pessoa:
            raise BusinessRuleError("Pessoa informada nao existe")
        if not pessoa.ativo:
            raise BusinessRuleError("Pessoa inativa")

        trilha = await self.trilha_repo.buscar_por_id(trilha_id)
        if not trilha:
            raise BusinessRuleError("Trilha informada nao existe")
        if not trilha.ativa:
            raise BusinessRuleError("Trilha desativada. Nao aceita novos progressos.")

        if str(pessoa.igreja_id) != str(trilha.igreja_id):
            raise BusinessRuleError("Pessoa e trilha pertencem a igrejas diferentes")

        existente = await self.repo.buscar_por_pessoa_e_trilha(pessoa_id, trilha_id)
        if existente:
            raise BusinessRuleError("Esta pessoa ja esta fazendo esta trilha")

        # Cria progresso com etapas
        etapas_ids = [e.id for e in trilha.etapas]

        prog_dados = {
            "pessoa_id": pessoa_id,
            "trilha_id": trilha_id,
            "igreja_id": trilha.igreja_id,
            "responsavel_id": autor.id,
            "status": "em_andamento",
            "iniciado_em": dados.get("iniciado_em") or date.today(),
            "observacoes": dados.get("observacoes"),
        }
        return await self.repo.criar(prog_dados, etapas_ids)

    async def buscar(self, obj_id: UUID):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Progresso", str(obj_id))
        return obj

    async def listar(self, usuario, skip=0, limit=100, igreja_id=None, pessoa_id=None, trilha_id=None, status=None):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        return await self.repo.listar(skip, limit, igreja_id, pessoa_id, trilha_id, status)

    async def marcar_etapa(self, progresso_id: UUID, etapa_id: UUID, concluida: bool, observacao, usuario: Usuario):
        prog = await self.buscar(progresso_id)
        if prog.status != "em_andamento":
            raise BusinessRuleError("So e possivel marcar etapas de progressos em andamento")

        pe = await self.repo.buscar_etapa(progresso_id, etapa_id)
        if not pe:
            raise NotFoundError("Etapa do progresso", str(etapa_id))

        dados = {
            "concluida": concluida,
            "concluida_em": date.today() if concluida else None,
        }
        if observacao is not None:
            dados["observacao"] = observacao

        await self.repo.atualizar_etapa(pe, dados)

        # Verifica se pode auto-concluir
        await self._verificar_auto_conclusao(prog)

        return await self.buscar(progresso_id)

    async def _verificar_auto_conclusao(self, prog):
        """Se todas as etapas obrigatorias estao concluidas, conclui automaticamente."""
        # Refresh para pegar etapas atualizadas
        await self.db.refresh(prog)
        obrigatorias = [e for e in prog.trilha.etapas if e.obrigatoria]
        if not obrigatorias:
            return

        progresso_etapas = {pe.etapa_id: pe for pe in prog.etapas}
        todas_ok = all(
            progresso_etapas.get(e.id) and progresso_etapas[e.id].concluida
            for e in obrigatorias
        )
        if todas_ok:
            await self.repo.atualizar(prog, {
                "status": "concluida",
                "concluido_em": date.today(),
            })

    async def concluir(self, obj_id: UUID, usuario: Usuario):
        prog = await self.buscar(obj_id)
        if prog.status == "concluida":
            raise BusinessRuleError("Progresso ja esta concluido")
        return await self.repo.atualizar(prog, {
            "status": "concluida",
            "concluido_em": date.today(),
        })

    async def cancelar(self, obj_id: UUID, usuario: Usuario):
        prog = await self.buscar(obj_id)
        if prog.status == "cancelada":
            raise BusinessRuleError("Progresso ja esta cancelado")
        return await self.repo.atualizar(prog, {"status": "cancelada"})

    async def deletar(self, obj_id: UUID, usuario: Usuario):
        prog = await self.buscar(obj_id)
        await self.repo.deletar(prog)

    async def dashboard(self, usuario, igreja_id=None):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id

        return {
            "total_trilhas_ativas": len(await self.trilha_repo.listar(
                igreja_id=igreja_id, apenas_ativas=True, limit=10000,
            )),
            "total_em_andamento": await self.repo.contar_por_status("em_andamento", igreja_id),
            "total_concluidas": await self.repo.contar_por_status("concluida", igreja_id),
            "concluidas_ultimos_30_dias": await self.repo.contar_concluidas_periodo(30, igreja_id),
            "pessoas_paradas_30d": await self.repo.contar_paradas_30d(30, igreja_id),
            "trilhas_mais_populares": await self.repo.trilhas_populares(igreja_id),
        }

    async def listar_por_pessoa(self, pessoa_id: UUID):
        return await self.repo.listar(pessoa_id=pessoa_id, limit=1000)
'''

# ============================================================
# 5. ROUTER
# ============================================================
router_py = '''from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database.connection import get_db
from app.modules.jornada.schemas import (
    DashboardJornada,
    MarcarEtapaRequest,
    ProgressoCreate,
    ProgressoResponse,
    TrilhaCreate,
    TrilhaResponse,
    TrilhaUpdate,
)
from app.modules.jornada.service import ProgressoService, TrilhaService
from app.modules.usuarios.models import Usuario


router = APIRouter(prefix="/jornada", tags=["Jornada"])


# ============ DASHBOARD ============

@router.get("/dashboard", response_model=DashboardJornada)
async def dashboard(
    igreja_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ProgressoService(db).dashboard(usuario, igreja_id)


# ============ TRILHAS ============

@router.post("/trilhas/", response_model=TrilhaResponse, status_code=status.HTTP_201_CREATED)
async def criar_trilha(
    dados: TrilhaCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TrilhaService(db).criar(dados.model_dump(), usuario)


@router.get("/trilhas/", response_model=list[TrilhaResponse])
async def listar_trilhas(
    skip: int = 0, limit: int = 100,
    igreja_id: UUID | None = None,
    tipo: str | None = None,
    apenas_ativas: bool = False,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TrilhaService(db).listar(usuario, skip, limit, igreja_id, tipo, apenas_ativas)


@router.get("/trilhas/{trilha_id}", response_model=TrilhaResponse)
async def buscar_trilha(
    trilha_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TrilhaService(db).buscar(trilha_id)


@router.put("/trilhas/{trilha_id}", response_model=TrilhaResponse)
async def atualizar_trilha(
    trilha_id: UUID,
    dados: TrilhaUpdate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TrilhaService(db).atualizar(trilha_id, dados.model_dump(exclude_unset=True), usuario)


@router.patch("/trilhas/{trilha_id}/desativar", response_model=TrilhaResponse)
async def desativar_trilha(
    trilha_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TrilhaService(db).desativar(trilha_id, usuario)


@router.patch("/trilhas/{trilha_id}/reativar", response_model=TrilhaResponse)
async def reativar_trilha(
    trilha_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TrilhaService(db).reativar(trilha_id, usuario)


@router.delete("/trilhas/{trilha_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_trilha(
    trilha_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    await TrilhaService(db).deletar(trilha_id, usuario)


# ============ PROGRESSOS ============

@router.post("/progressos/", response_model=ProgressoResponse, status_code=status.HTTP_201_CREATED)
async def criar_progresso(
    dados: ProgressoCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ProgressoService(db).criar(dados.model_dump(), usuario)


@router.get("/progressos/", response_model=list[ProgressoResponse])
async def listar_progressos(
    skip: int = 0, limit: int = 100,
    igreja_id: UUID | None = None,
    pessoa_id: UUID | None = None,
    trilha_id: UUID | None = None,
    status_: str | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ProgressoService(db).listar(
        usuario, skip, limit, igreja_id, pessoa_id, trilha_id, status_,
    )


@router.get("/progressos/{progresso_id}", response_model=ProgressoResponse)
async def buscar_progresso(
    progresso_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ProgressoService(db).buscar(progresso_id)


@router.patch("/progressos/{progresso_id}/etapas/{etapa_id}", response_model=ProgressoResponse)
async def marcar_etapa(
    progresso_id: UUID,
    etapa_id: UUID,
    dados: MarcarEtapaRequest,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ProgressoService(db).marcar_etapa(
        progresso_id, etapa_id, dados.concluida, dados.observacao, usuario,
    )


@router.patch("/progressos/{progresso_id}/concluir", response_model=ProgressoResponse)
async def concluir_progresso(
    progresso_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ProgressoService(db).concluir(progresso_id, usuario)


@router.patch("/progressos/{progresso_id}/cancelar", response_model=ProgressoResponse)
async def cancelar_progresso(
    progresso_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ProgressoService(db).cancelar(progresso_id, usuario)


@router.delete("/progressos/{progresso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_progresso(
    progresso_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    await ProgressoService(db).deletar(progresso_id, usuario)
'''

# ============================================================
# 6. __init__
# ============================================================
init_py = '''from app.modules.jornada.models import (
    EtapaTrilha,
    Progresso,
    ProgressoEtapa,
    Trilha,
)

__all__ = ["Trilha", "EtapaTrilha", "Progresso", "ProgressoEtapa"]
'''

# ============================================================
# 7. API ROUTER ATUALIZADO
# ============================================================
api_router_py = '''from fastapi import APIRouter

from app.modules.cuidado.router import router as cuidado_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.eventos.router import router as eventos_router
from app.modules.igreja.router import router as igreja_router
from app.modules.jornada.router import router as jornada_router
from app.modules.notificacoes.router import router as notificacoes_router
from app.modules.oracao.router import router as oracao_router
from app.modules.pessoas.router import router as pessoa_router
from app.modules.usuarios.router import router as auth_router

api_router = APIRouter()
api_router.include_router(dashboard_router)
api_router.include_router(notificacoes_router)
api_router.include_router(auth_router)
api_router.include_router(igreja_router)
api_router.include_router(pessoa_router)
api_router.include_router(cuidado_router)
api_router.include_router(oracao_router)
api_router.include_router(eventos_router)
api_router.include_router(jornada_router)
'''


def atualizar_env_alembic():
    p = BACKEND / "migrations" / "env.py"
    if not p.exists():
        print(f"  [SKIP] env.py nao encontrado")
        return
    c = p.read_text(encoding="utf-8")
    if "jornada" in c:
        print("  [SKIP] env.py ja importa jornada")
        return
    linha_base = "from app.modules.eventos import models  # noqa: F401"
    linha_nova = "from app.modules.jornada import models  # noqa: F401"
    if linha_base not in c:
        print("  [AVISO] nao achei import de eventos em env.py. Adicione manualmente:")
        print(f"        {linha_nova}")
        return
    c = c.replace(linha_base, f"{linha_base}\n{linha_nova}")
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] env.py atualizado")


print(f"Backend: {BACKEND}")
print()

print("Criando modulo jornada...")
escrever(BACKEND / "app" / "modules" / "jornada" / "models.py", models_py)
escrever(BACKEND / "app" / "modules" / "jornada" / "schemas.py", schemas_py)
escrever(BACKEND / "app" / "modules" / "jornada" / "repository.py", repository_py)
escrever(BACKEND / "app" / "modules" / "jornada" / "service.py", service_py)
escrever(BACKEND / "app" / "modules" / "jornada" / "router.py", router_py)
escrever(BACKEND / "app" / "modules" / "jornada" / "__init__.py", init_py)

print()
print("Atualizando API router...")
escrever(BACKEND / "app" / "api" / "router.py", api_router_py)

print()
print("Atualizando migrations/env.py...")
atualizar_env_alembic()

print()
print("=" * 60)
print("PRONTO! Agora rode:")
print("  alembic revision --autogenerate -m 'criar tabelas jornada'")
print("  alembic upgrade head")
print("=" * 60)