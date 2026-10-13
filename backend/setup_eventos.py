"""Setup do modulo Eventos (agenda pastoral + inscricoes)."""
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
models_py = '''from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin, UUIDMixin


class Evento(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "eventos"

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

    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default="culto", index=True)
    data_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    data_fim: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    local: Mapped[str | None] = mapped_column(String(200), nullable=True)
    endereco: Mapped[str | None] = mapped_column(Text, nullable=True)
    vagas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    publico: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requer_inscricao: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    igreja = relationship("Igreja", lazy="joined")
    responsavel = relationship("Usuario", lazy="joined")

    def __repr__(self) -> str:
        return f"<Evento {self.titulo} ({self.tipo})>"


class Inscricao(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "inscricoes"
    __table_args__ = (
        UniqueConstraint("evento_id", "pessoa_id", name="uq_inscricoes_evento_pessoa"),
    )

    evento_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("eventos.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    pessoa_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pessoas.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="inscrito", index=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)

    evento = relationship("Evento", lazy="joined")
    pessoa = relationship("Pessoa", lazy="joined")

    def __repr__(self) -> str:
        return f"<Inscricao evento={self.evento_id} pessoa={self.pessoa_id} ({self.status})>"
'''

# ============================================================
# 2. SCHEMAS
# ============================================================
schemas_py = '''from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PessoaResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class UsuarioResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


# ============ EVENTOS ============

class EventoBase(BaseModel):
    titulo: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    tipo: str = Field("culto", pattern="^(culto|reuniao|conferencia|retiro|especial|outro)$")
    data_inicio: datetime
    data_fim: datetime | None = None
    local: str | None = Field(None, max_length=200)
    endereco: str | None = None
    vagas: int | None = Field(None, ge=0)
    publico: bool = True
    requer_inscricao: bool = False


class EventoCreate(EventoBase):
    pass


class EventoUpdate(BaseModel):
    titulo: str | None = Field(None, min_length=2, max_length=200)
    descricao: str | None = None
    tipo: str | None = Field(None, pattern="^(culto|reuniao|conferencia|retiro|especial|outro)$")
    data_inicio: datetime | None = None
    data_fim: datetime | None = None
    local: str | None = None
    endereco: str | None = None
    vagas: int | None = Field(None, ge=0)
    publico: bool | None = None
    requer_inscricao: bool | None = None


class EventoResponse(EventoBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    igreja_id: UUID
    responsavel_id: UUID
    ativo: bool
    created_at: datetime
    updated_at: datetime
    responsavel: UsuarioResumo | None = None
    total_inscritos: int = 0
    total_presentes: int = 0


class EventoProximo(BaseModel):
    id: UUID
    titulo: str
    tipo: str
    data_inicio: datetime
    local: str | None = None
    vagas: int | None = None
    total_inscritos: int = 0
    dias_para_evento: int = 0


class DashboardEventos(BaseModel):
    total_proximos_7d: int
    total_proximos_30d: int
    proximos_eventos: list[EventoProximo]
    proximos: list[EventoProximo]  # alias compativel


# ============ INSCRICOES ============

class InscricaoCreate(BaseModel):
    pessoa_id: UUID
    observacao: str | None = None


class InscricaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    evento_id: UUID
    pessoa_id: UUID
    igreja_id: UUID
    status: str
    observacao: str | None = None
    created_at: datetime
    pessoa: PessoaResumo | None = None


class InscricaoCheckin(BaseModel):
    status: str = Field("presente", pattern="^(inscrito|presente|ausente|cancelado)$")
    observacao: str | None = None
'''

# ============================================================
# 3. REPOSITORY
# ============================================================
repository_py = '''from datetime import date, datetime, timedelta, timezone
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
'''

# ============================================================
# 4. SERVICE
# ============================================================
service_py = '''from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.handlers import BusinessRuleError, NotFoundError, PermissionDeniedError
from app.modules.eventos.repository import EventoRepository, InscricaoRepository
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
        if not autor.igreja_id:
            raise BusinessRuleError("Autor sem igreja vinculada. Vincule-se a uma igreja.")
        dados["igreja_id"] = autor.igreja_id
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
'''

# ============================================================
# 5. ROUTER
# ============================================================
router_py = '''from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database.connection import get_db
from app.modules.eventos.schemas import (
    DashboardEventos,
    EventoCreate,
    EventoResponse,
    EventoUpdate,
    InscricaoCheckin,
    InscricaoCreate,
    InscricaoResponse,
)
from app.modules.eventos.service import EventoService, InscricaoService
from app.modules.usuarios.models import Usuario


router = APIRouter(prefix="/eventos", tags=["Eventos"])


# ============ EVENTOS ============

@router.get("/dashboard/proximos", response_model=DashboardEventos)
async def dashboard_proximos(
    igreja_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await EventoService(db).dashboard(usuario, igreja_id)


@router.post("/", response_model=EventoResponse, status_code=status.HTTP_201_CREATED)
async def criar(
    dados: EventoCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await EventoService(db).criar(dados.model_dump(), usuario)


@router.get("/", response_model=list[EventoResponse])
async def listar(
    skip: int = 0, limit: int = 100,
    igreja_id: UUID | None = None,
    tipo: str | None = None,
    apenas_ativos: bool = False,
    data_de: datetime | None = None,
    data_ate: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await EventoService(db).listar(
        usuario, skip, limit, igreja_id, tipo, apenas_ativos, data_de, data_ate,
    )


@router.get("/{evento_id}", response_model=EventoResponse)
async def buscar(
    evento_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await EventoService(db).buscar(evento_id)


@router.put("/{evento_id}", response_model=EventoResponse)
async def atualizar(
    evento_id: UUID,
    dados: EventoUpdate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await EventoService(db).atualizar(evento_id, dados.model_dump(exclude_unset=True), usuario)


@router.patch("/{evento_id}/desativar", response_model=EventoResponse)
async def desativar(
    evento_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await EventoService(db).desativar(evento_id, usuario)


@router.patch("/{evento_id}/reativar", response_model=EventoResponse)
async def reativar(
    evento_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await EventoService(db).reativar(evento_id, usuario)


@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar(
    evento_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    await EventoService(db).deletar(evento_id, usuario)


# ============ INSCRICOES ============

@router.post("/{evento_id}/inscricoes", response_model=InscricaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_inscricao(
    evento_id: UUID,
    dados: InscricaoCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await InscricaoService(db).criar(evento_id, dados.pessoa_id, dados.observacao, usuario)


@router.get("/{evento_id}/inscricoes", response_model=list[InscricaoResponse])
async def listar_inscricoes(
    evento_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await InscricaoService(db).listar_por_evento(evento_id)


@router.patch("/inscricoes/{inscricao_id}/checkin", response_model=InscricaoResponse)
async def checkin(
    inscricao_id: UUID,
    dados: InscricaoCheckin,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await InscricaoService(db).checkin(inscricao_id, dados.status, dados.observacao, usuario)


@router.delete("/inscricoes/{inscricao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_inscricao(
    inscricao_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    await InscricaoService(db).deletar(inscricao_id, usuario)
'''

# ============================================================
# 6. __init__
# ============================================================
init_py = '''from app.modules.eventos.models import Evento, Inscricao

__all__ = ["Evento", "Inscricao"]
'''

# ============================================================
# 7. API ROUTER ATUALIZADO
# ============================================================
api_router_py = '''from fastapi import APIRouter

from app.modules.cuidado.router import router as cuidado_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.eventos.router import router as eventos_router
from app.modules.igreja.router import router as igreja_router
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
'''


def atualizar_env_alembic():
    p = BACKEND / "migrations" / "env.py"
    if not p.exists():
        print(f"  [SKIP] env.py nao encontrado")
        return
    c = p.read_text(encoding="utf-8")
    if "eventos" in c:
        print("  [SKIP] env.py ja importa eventos")
        return
    linha_base = "from app.modules.oracao import models  # noqa: F401"
    linha_nova = "from app.modules.eventos import models  # noqa: F401"
    if linha_base not in c:
        print("  [AVISO] nao achei import de oracao em env.py. Adicione manualmente:")
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

print("Criando modulo eventos...")
escrever(BACKEND / "app" / "modules" / "eventos" / "models.py", models_py)
escrever(BACKEND / "app" / "modules" / "eventos" / "schemas.py", schemas_py)
escrever(BACKEND / "app" / "modules" / "eventos" / "repository.py", repository_py)
escrever(BACKEND / "app" / "modules" / "eventos" / "service.py", service_py)
escrever(BACKEND / "app" / "modules" / "eventos" / "router.py", router_py)
escrever(BACKEND / "app" / "modules" / "eventos" / "__init__.py", init_py)

print()
print("Atualizando API router...")
escrever(BACKEND / "app" / "api" / "router.py", api_router_py)

print()
print("Atualizando migrations/env.py...")
atualizar_env_alembic()

print()
print("=" * 60)
print("PRONTO! Agora rode:")
print("  alembic revision --autogenerate -m 'criar tabelas eventos e inscricoes'")
print("  alembic upgrade head")
print("=" * 60)