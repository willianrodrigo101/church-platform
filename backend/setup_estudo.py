"""Modulo Estudo — Bloco 1: Trilhas, Cursos, Modulos e Conteudos."""
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
# MODELS
# ============================================================
models_py = '''from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin, UUIDMixin


class TrilhaFormacao(Base, UUIDMixin, TimestampMixin):
    """Macro-area de formacao: Fundamentos, Discipulado, Bacharelado, etc."""
    __tablename__ = "trilhas_formacao"

    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    nivel: Mapped[str] = mapped_column(String(30), nullable=False, default="iniciante", index=True)
    icone: Mapped[str | None] = mapped_column(String(10), nullable=True)
    cor: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    igreja = relationship("Igreja", lazy="joined")
    cursos = relationship(
        "Curso",
        back_populates="trilha",
        cascade="all, delete-orphan",
        order_by="Curso.ordem",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<TrilhaFormacao {self.nome} ({self.nivel})>"


class Curso(Base, UUIDMixin, TimestampMixin):
    """Curso dentro de uma trilha: Teologia Sistematica, Grego I, Canto, etc."""
    __tablename__ = "cursos"

    trilha_id: Mapped["PGUUID | None"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("trilhas_formacao.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default="teologia", index=True)
    nivel: Mapped[str] = mapped_column(String(30), nullable=False, default="iniciante", index=True)
    carga_horaria: Mapped[int | None] = mapped_column(Integer, nullable=True)
    imagem_capa: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    obrigatorio: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    trilha = relationship("TrilhaFormacao", back_populates="cursos")
    igreja = relationship("Igreja", lazy="joined")
    modulos = relationship(
        "ModuloCurso",
        back_populates="curso",
        cascade="all, delete-orphan",
        order_by="ModuloCurso.ordem",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Curso {self.nome} ({self.tipo})>"


class ModuloCurso(Base, UUIDMixin, TimestampMixin):
    """Modulo dentro de um curso."""
    __tablename__ = "modulos_curso"

    curso_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("cursos.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    duracao_minutos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    obrigatorio: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    curso = relationship("Curso", back_populates="modulos")
    conteudos = relationship(
        "ConteudoModulo",
        back_populates="modulo",
        cascade="all, delete-orphan",
        order_by="ConteudoModulo.ordem",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ModuloCurso {self.ordem}. {self.titulo}>"


class ConteudoModulo(Base, UUIDMixin, TimestampMixin):
    """Conteudo dentro de um modulo: video, PDF, audio, texto, link, quiz."""
    __tablename__ = "conteudos_modulo"

    modulo_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("modulos_curso.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default="texto", index=True)
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    texto: Mapped[str | None] = mapped_column(Text, nullable=True)
    duracao_minutos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    modulo = relationship("ModuloCurso", back_populates="conteudos")

    def __repr__(self) -> str:
        return f"<ConteudoModulo {self.tipo}: {self.titulo}>"
'''

# ============================================================
# SCHEMAS
# ============================================================
schemas_py = '''from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConteudoCreate(BaseModel):
    ordem: int = Field(1, ge=1)
    titulo: str = Field(..., min_length=2, max_length=200)
    tipo: str = Field("texto", pattern="^(video|pdf|audio|texto|link|imagem|slides)$")
    url: str | None = None
    texto: str | None = None
    duracao_minutos: int | None = None


class ConteudoResponse(ConteudoCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    ativo: bool
    created_at: datetime


class ModuloCreate(BaseModel):
    ordem: int = Field(1, ge=1)
    titulo: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    duracao_minutos: int | None = None
    obrigatorio: bool = True
    conteudos: list[ConteudoCreate] = []


class ModuloUpdate(BaseModel):
    ordem: int | None = None
    titulo: str | None = Field(None, min_length=2, max_length=200)
    descricao: str | None = None
    duracao_minutos: int | None = None
    obrigatorio: bool | None = None


class ModuloResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    curso_id: UUID
    ordem: int
    titulo: str
    descricao: str | None = None
    duracao_minutos: int | None = None
    obrigatorio: bool
    ativo: bool
    created_at: datetime
    conteudos: list[ConteudoResponse] = []


class CursoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    tipo: str = Field("teologia", pattern="^(teologia|biblico|sistematico|historico|pratico|linguas|artes|ministerial|outro)$")
    nivel: str = Field("iniciante", pattern="^(iniciante|basico|intermediario|avancado|bacharelado)$")
    carga_horaria: int | None = None
    imagem_capa: str | None = None
    obrigatorio: bool = False
    ordem: int = 1


class CursoCreate(CursoBase):
    trilha_id: UUID | None = None
    modulos: list[ModuloCreate] = []


class CursoUpdate(BaseModel):
    nome: str | None = Field(None, min_length=2, max_length=200)
    descricao: str | None = None
    tipo: str | None = None
    nivel: str | None = None
    carga_horaria: int | None = None
    imagem_capa: str | None = None
    obrigatorio: bool | None = None
    ordem: int | None = None
    trilha_id: UUID | None = None


class CursoResponse(CursoBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    igreja_id: UUID
    trilha_id: UUID | None = None
    ativo: bool
    created_at: datetime
    updated_at: datetime
    modulos: list[ModuloResponse] = []


class TrilhaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    nivel: str = Field("iniciante", pattern="^(iniciante|basico|intermediario|avancado|bacharelado)$")
    icone: str | None = None
    cor: str | None = None
    ordem: int = 1


class TrilhaCreate(TrilhaBase):
    igreja_id: UUID | None = None


class TrilhaUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    nivel: str | None = None
    icone: str | None = None
    cor: str | None = None
    ordem: int | None = None


class TrilhaResponse(TrilhaBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    igreja_id: UUID
    ativa: bool
    created_at: datetime
    updated_at: datetime
    cursos: list[CursoResponse] = []


class DashboardEstudo(BaseModel):
    total_trilhas: int
    total_cursos: int
    total_modulos: int
    total_conteudos: int
    cursos_por_tipo: dict[str, int]
    cursos_por_nivel: dict[str, int]
'''

# ============================================================
# REPOSITORY
# ============================================================
repository_py = '''from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.estudo.models import (
    ConteudoModulo,
    Curso,
    ModuloCurso,
    TrilhaFormacao,
)


class TrilhaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict) -> TrilhaFormacao:
        obj = TrilhaFormacao(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar_por_id(self, obj_id: UUID) -> TrilhaFormacao | None:
        stmt = (
            select(TrilhaFormacao)
            .options(selectinload(TrilhaFormacao.cursos))
            .where(TrilhaFormacao.id == obj_id)
        )
        r = await self.db.execute(stmt)
        return r.unique().scalar_one_or_none()

    async def listar(self, skip=0, limit=100, igreja_id=None, nivel=None, apenas_ativas=False):
        stmt = (
            select(TrilhaFormacao)
            .options(selectinload(TrilhaFormacao.cursos))
            .order_by(TrilhaFormacao.ordem.asc(), TrilhaFormacao.nome.asc())
        )
        if igreja_id: stmt = stmt.where(TrilhaFormacao.igreja_id == igreja_id)
        if nivel: stmt = stmt.where(TrilhaFormacao.nivel == nivel)
        if apenas_ativas: stmt = stmt.where(TrilhaFormacao.ativa.is_(True))
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.unique().scalars().all())

    async def atualizar(self, obj, dados):
        for k, v in dados.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()


class CursoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict, modulos: list[dict]) -> Curso:
        curso = Curso(**dados)
        self.db.add(curso)
        await self.db.flush()
        for m in modulos:
            conteudos = m.pop("conteudos", []) or []
            mod = ModuloCurso(curso_id=curso.id, **m)
            self.db.add(mod)
            await self.db.flush()
            for i, c in enumerate(conteudos, start=1):
                c["ordem"] = c.get("ordem") or i
                conteudo = ConteudoModulo(modulo_id=mod.id, **c)
                self.db.add(conteudo)
        await self.db.flush()
        await self.db.refresh(curso)
        return curso

    async def buscar_por_id(self, obj_id: UUID) -> Curso | None:
        stmt = (
            select(Curso)
            .options(
                selectinload(Curso.modulos).selectinload(ModuloCurso.conteudos),
            )
            .where(Curso.id == obj_id)
        )
        r = await self.db.execute(stmt)
        return r.unique().scalar_one_or_none()

    async def listar(
        self, skip=0, limit=100,
        igreja_id=None, trilha_id=None, tipo=None, nivel=None,
        apenas_ativos=False,
    ):
        stmt = (
            select(Curso)
            .options(selectinload(Curso.modulos))
            .order_by(Curso.ordem.asc(), Curso.nome.asc())
        )
        if igreja_id: stmt = stmt.where(Curso.igreja_id == igreja_id)
        if trilha_id: stmt = stmt.where(Curso.trilha_id == trilha_id)
        if tipo: stmt = stmt.where(Curso.tipo == tipo)
        if nivel: stmt = stmt.where(Curso.nivel == nivel)
        if apenas_ativos: stmt = stmt.where(Curso.ativo.is_(True))
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.unique().scalars().all())

    async def atualizar(self, obj, dados):
        for k, v in dados.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()

    async def contar_por_tipo(self, igreja_id=None) -> dict:
        stmt = select(Curso.tipo, func.count(Curso.id)).group_by(Curso.tipo)
        if igreja_id: stmt = stmt.where(Curso.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        return {row[0]: row[1] for row in r.all()}

    async def contar_por_nivel(self, igreja_id=None) -> dict:
        stmt = select(Curso.nivel, func.count(Curso.id)).group_by(Curso.nivel)
        if igreja_id: stmt = stmt.where(Curso.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        return {row[0]: row[1] for row in r.all()}


class ModuloRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict, conteudos: list[dict] | None = None) -> ModuloCurso:
        mod = ModuloCurso(**dados)
        self.db.add(mod)
        await self.db.flush()
        if conteudos:
            for i, c in enumerate(conteudos, start=1):
                c["ordem"] = c.get("ordem") or i
                self.db.add(ConteudoModulo(modulo_id=mod.id, **c))
        await self.db.flush()
        await self.db.refresh(mod)
        return mod

    async def buscar_por_id(self, obj_id: UUID) -> ModuloCurso | None:
        stmt = (
            select(ModuloCurso)
            .options(selectinload(ModuloCurso.conteudos))
            .where(ModuloCurso.id == obj_id)
        )
        r = await self.db.execute(stmt)
        return r.unique().scalar_one_or_none()

    async def listar_por_curso(self, curso_id: UUID):
        stmt = (
            select(ModuloCurso)
            .options(selectinload(ModuloCurso.conteudos))
            .where(ModuloCurso.curso_id == curso_id)
            .order_by(ModuloCurso.ordem.asc())
        )
        r = await self.db.execute(stmt)
        return list(r.unique().scalars().all())

    async def atualizar(self, obj, dados):
        for k, v in dados.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()


class ConteudoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict) -> ConteudoModulo:
        obj = ConteudoModulo(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def listar_por_modulo(self, modulo_id: UUID):
        stmt = select(ConteudoModulo).where(
            ConteudoModulo.modulo_id == modulo_id
        ).order_by(ConteudoModulo.ordem.asc())
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def buscar_por_id(self, obj_id: UUID) -> ConteudoModulo | None:
        r = await self.db.execute(select(ConteudoModulo).where(ConteudoModulo.id == obj_id))
        return r.scalar_one_or_none()

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()
'''

# ============================================================
# SERVICE
# ============================================================
service_py = '''from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.handlers import (
    BusinessRuleError,
    NotFoundError,
    PermissionDeniedError,
)
from app.modules.estudo.repository import (
    ConteudoRepository,
    CursoRepository,
    ModuloRepository,
    TrilhaRepository,
)
from app.modules.igreja.repository import IgrejaRepository
from app.modules.usuarios.models import Usuario


class TrilhaService:
    def __init__(self, db: AsyncSession):
        self.repo = TrilhaRepository(db)
        self.igreja_repo = IgrejaRepository(db)
        self.db = db

    async def _resolver_igreja(self, autor: Usuario, igreja_id: UUID | None) -> UUID:
        if autor.role == "admin":
            if igreja_id:
                return igreja_id
            if autor.igreja_id:
                return autor.igreja_id
            igrejas = await self.igreja_repo.listar(apenas_ativas=True)
            if not igrejas:
                raise BusinessRuleError("Nenhuma igreja ativa cadastrada.")
            return igrejas[0].id
        if not autor.igreja_id:
            raise BusinessRuleError("Usuario sem igreja vinculada.")
        return autor.igreja_id

    async def criar(self, dados: dict, autor: Usuario):
        dados["igreja_id"] = await self._resolver_igreja(autor, dados.pop("igreja_id", None))
        return await self.repo.criar(dados)

    async def buscar(self, obj_id: UUID):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Trilha de formacao", str(obj_id))
        return obj

    async def listar(self, usuario, skip=0, limit=100, igreja_id=None, nivel=None, apenas_ativas=False):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        return await self.repo.listar(skip, limit, igreja_id, nivel, apenas_ativas)

    async def atualizar(self, obj_id, dados, usuario):
        obj = await self.buscar(obj_id)
        return await self.repo.atualizar(obj, dados)

    async def desativar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if not obj.ativa:
            raise BusinessRuleError("Trilha ja esta desativada")
        return await self.repo.atualizar(obj, {"ativa": False})

    async def reativar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if obj.ativa:
            raise BusinessRuleError("Trilha ja esta ativa")
        return await self.repo.atualizar(obj, {"ativa": True})

    async def deletar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if obj.cursos:
            raise BusinessRuleError(
                f"Nao e possivel excluir: {len(obj.cursos)} curso(s) vinculado(s). "
                "Desative a trilha em vez de exclui-la."
            )
        await self.repo.deletar(obj)


class CursoService:
    def __init__(self, db: AsyncSession):
        self.repo = CursoRepository(db)
        self.mod_repo = ModuloRepository(db)
        self.trilha_repo = TrilhaRepository(db)
        self.igreja_repo = IgrejaRepository(db)
        self.db = db

    async def _resolver_igreja(self, autor: Usuario, igreja_id: UUID | None) -> UUID:
        if autor.role == "admin":
            if igreja_id:
                return igreja_id
            if autor.igreja_id:
                return autor.igreja_id
            igrejas = await self.igreja_repo.listar(apenas_ativas=True)
            if not igrejas:
                raise BusinessRuleError("Nenhuma igreja ativa cadastrada.")
            return igrejas[0].id
        if not autor.igreja_id:
            raise BusinessRuleError("Usuario sem igreja vinculada.")
        return autor.igreja_id

    async def criar(self, dados: dict, autor: Usuario):
        modulos = dados.pop("modulos", []) or []
        trilha_id = dados.pop("trilha_id", None)

        if trilha_id:
            trilha = await self.trilha_repo.buscar_por_id(trilha_id)
            if not trilha:
                raise BusinessRuleError("Trilha informada nao existe")

        igreja_id = await self._resolver_igreja(autor, None)
        dados["igreja_id"] = igreja_id
        dados["trilha_id"] = trilha_id

        for i, m in enumerate(modulos, start=1):
            m["ordem"] = m.get("ordem") or i

        return await self.repo.criar(dados, modulos)

    async def buscar(self, obj_id: UUID):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Curso", str(obj_id))
        return obj

    async def listar(self, usuario, skip=0, limit=100, igreja_id=None, trilha_id=None, tipo=None, nivel=None, apenas_ativos=False):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        return await self.repo.listar(skip, limit, igreja_id, trilha_id, tipo, nivel, apenas_ativos)

    async def atualizar(self, obj_id, dados, usuario):
        obj = await self.buscar(obj_id)
        return await self.repo.atualizar(obj, dados)

    async def desativar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if not obj.ativo:
            raise BusinessRuleError("Curso ja esta desativado")
        return await self.repo.atualizar(obj, {"ativo": False})

    async def reativar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if obj.ativo:
            raise BusinessRuleError("Curso ja esta ativo")
        return await self.repo.atualizar(obj, {"ativo": True})

    async def deletar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        await self.repo.deletar(obj)

    async def dashboard(self, usuario, igreja_id=None):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id

        trilhas = await self.trilha_repo.listar(igreja_id=igreja_id, limit=1000)
        cursos = await self.repo.listar(igreja_id=igreja_id, limit=10000)

        total_modulos = sum(len(c.modulos) for c in cursos)

        return {
            "total_trilhas": len(trilhas),
            "total_cursos": len(cursos),
            "total_modulos": total_modulos,
            "total_conteudos": 0,  # placeholder — preenchido no service real
            "cursos_por_tipo": await self.repo.contar_por_tipo(igreja_id),
            "cursos_por_nivel": await self.repo.contar_por_nivel(igreja_id),
        }


class ModuloService:
    def __init__(self, db: AsyncSession):
        self.repo = ModuloRepository(db)
        self.curso_repo = CursoRepository(db)
        self.db = db

    async def criar(self, curso_id: UUID, dados: dict, autor: Usuario):
        curso = await self.curso_repo.buscar_por_id(curso_id)
        if not curso:
            raise NotFoundError("Curso", str(curso_id))
        conteudos = dados.pop("conteudos", []) or []
        dados["curso_id"] = curso_id
        return await self.repo.criar(dados, conteudos)

    async def listar_por_curso(self, curso_id: UUID):
        return await self.repo.listar_por_curso(curso_id)

    async def atualizar(self, obj_id, dados, usuario):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Modulo", str(obj_id))
        return await self.repo.atualizar(obj, dados)

    async def deletar(self, obj_id, usuario):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Modulo", str(obj_id))
        await self.repo.deletar(obj)


class ConteudoService:
    def __init__(self, db: AsyncSession):
        self.repo = ConteudoRepository(db)
        self.mod_repo = ModuloRepository(db)
        self.db = db

    async def criar(self, modulo_id: UUID, dados: dict, autor: Usuario):
        mod = await self.mod_repo.buscar_por_id(modulo_id)
        if not mod:
            raise NotFoundError("Modulo", str(modulo_id))
        dados["modulo_id"] = modulo_id
        return await self.repo.criar(dados)

    async def listar_por_modulo(self, modulo_id: UUID):
        return await self.repo.listar_por_modulo(modulo_id)

    async def deletar(self, obj_id, usuario):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Conteudo", str(obj_id))
        await self.repo.deletar(obj)
'''

# ============================================================
# ROUTER
# ============================================================
router_py = '''from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database.connection import get_db
from app.modules.estudo.schemas import (
    ConteudoCreate,
    ConteudoResponse,
    CursoCreate,
    CursoResponse,
    CursoUpdate,
    DashboardEstudo,
    ModuloCreate,
    ModuloResponse,
    ModuloUpdate,
    TrilhaCreate,
    TrilhaResponse,
    TrilhaUpdate,
)
from app.modules.estudo.service import (
    ConteudoService,
    CursoService,
    ModuloService,
    TrilhaService,
)
from app.modules.usuarios.models import Usuario


router = APIRouter(prefix="/estudo", tags=["Estudo"])


# ============ DASHBOARD ============

@router.get("/dashboard", response_model=DashboardEstudo)
async def dashboard(
    igreja_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await CursoService(db).dashboard(usuario, igreja_id)


# ============ TRILHAS ============

@router.post("/trilhas/", response_model=TrilhaResponse, status_code=status.HTTP_201_CREATED)
async def criar_trilha(dados: TrilhaCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await TrilhaService(db).criar(dados.model_dump(), usuario)


@router.get("/trilhas/", response_model=list[TrilhaResponse])
async def listar_trilhas(
    skip: int = 0, limit: int = 100,
    igreja_id: UUID | None = None,
    nivel: str | None = None,
    apenas_ativas: bool = False,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TrilhaService(db).listar(usuario, skip, limit, igreja_id, nivel, apenas_ativas)


@router.get("/trilhas/{trilha_id}", response_model=TrilhaResponse)
async def buscar_trilha(trilha_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await TrilhaService(db).buscar(trilha_id)


@router.put("/trilhas/{trilha_id}", response_model=TrilhaResponse)
async def atualizar_trilha(trilha_id: UUID, dados: TrilhaUpdate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await TrilhaService(db).atualizar(trilha_id, dados.model_dump(exclude_unset=True), usuario)


@router.patch("/trilhas/{trilha_id}/desativar", response_model=TrilhaResponse)
async def desativar_trilha(trilha_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await TrilhaService(db).desativar(trilha_id, usuario)


@router.patch("/trilhas/{trilha_id}/reativar", response_model=TrilhaResponse)
async def reativar_trilha(trilha_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await TrilhaService(db).reativar(trilha_id, usuario)


@router.delete("/trilhas/{trilha_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_trilha(trilha_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    await TrilhaService(db).deletar(trilha_id, usuario)


# ============ CURSOS ============

@router.post("/cursos/", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
async def criar_curso(dados: CursoCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await CursoService(db).criar(dados.model_dump(), usuario)


@router.get("/cursos/", response_model=list[CursoResponse])
async def listar_cursos(
    skip: int = 0, limit: int = 100,
    igreja_id: UUID | None = None,
    trilha_id: UUID | None = None,
    tipo: str | None = None,
    nivel: str | None = None,
    apenas_ativos: bool = False,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await CursoService(db).listar(usuario, skip, limit, igreja_id, trilha_id, tipo, nivel, apenas_ativos)


@router.get("/cursos/{curso_id}", response_model=CursoResponse)
async def buscar_curso(curso_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await CursoService(db).buscar(curso_id)


@router.put("/cursos/{curso_id}", response_model=CursoResponse)
async def atualizar_curso(curso_id: UUID, dados: CursoUpdate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await CursoService(db).atualizar(curso_id, dados.model_dump(exclude_unset=True), usuario)


@router.patch("/cursos/{curso_id}/desativar", response_model=CursoResponse)
async def desativar_curso(curso_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await CursoService(db).desativar(curso_id, usuario)


@router.patch("/cursos/{curso_id}/reativar", response_model=CursoResponse)
async def reativar_curso(curso_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await CursoService(db).reativar(curso_id, usuario)


@router.delete("/cursos/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_curso(curso_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    await CursoService(db).deletar(curso_id, usuario)


# ============ MODULOS ============

@router.post("/cursos/{curso_id}/modulos/", response_model=ModuloResponse, status_code=status.HTTP_201_CREATED)
async def criar_modulo(curso_id: UUID, dados: ModuloCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await ModuloService(db).criar(curso_id, dados.model_dump(), usuario)


@router.get("/cursos/{curso_id}/modulos/", response_model=list[ModuloResponse])
async def listar_modulos(curso_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await ModuloService(db).listar_por_curso(curso_id)


@router.put("/modulos/{modulo_id}", response_model=ModuloResponse)
async def atualizar_modulo(modulo_id: UUID, dados: ModuloUpdate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await ModuloService(db).atualizar(modulo_id, dados.model_dump(exclude_unset=True), usuario)


@router.delete("/modulos/{modulo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_modulo(modulo_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    await ModuloService(db).deletar(modulo_id, usuario)


# ============ CONTEUDOS ============

@router.post("/modulos/{modulo_id}/conteudos/", response_model=ConteudoResponse, status_code=status.HTTP_201_CREATED)
async def criar_conteudo(modulo_id: UUID, dados: ConteudoCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await ConteudoService(db).criar(modulo_id, dados.model_dump(), usuario)


@router.get("/modulos/{modulo_id}/conteudos/", response_model=list[ConteudoResponse])
async def listar_conteudos(modulo_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await ConteudoService(db).listar_por_modulo(modulo_id)


@router.delete("/conteudos/{conteudo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_conteudo(conteudo_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    await ConteudoService(db).deletar(conteudo_id, usuario)
'''

# ============================================================
# __init__
# ============================================================
init_py = '''from app.modules.estudo.models import (
    ConteudoModulo,
    Curso,
    ModuloCurso,
    TrilhaFormacao,
)

__all__ = ["TrilhaFormacao", "Curso", "ModuloCurso", "ConteudoModulo"]
'''

# ============================================================
# API ROUTER ATUALIZADO
# ============================================================
api_router_py = '''from fastapi import APIRouter

from app.modules.anexos.router import router as anexos_router
from app.modules.cuidado.router import router as cuidado_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.estudo.router import router as estudo_router
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
api_router.include_router(anexos_router)
api_router.include_router(estudo_router)
'''


def atualizar_env_alembic():
    p = BACKEND / "migrations" / "env.py"
    if not p.exists():
        print(f"  [SKIP] env.py nao encontrado")
        return
    c = p.read_text(encoding="utf-8")
    if "from app.modules.estudo import models" in c:
        print("  [SKIP] env.py ja importa estudo")
        return
    linha_base = "from app.modules.anexos import models  # noqa: F401"
    linha_nova = "from app.modules.estudo import models  # noqa: F401"
    if linha_base not in c:
        print("  [AVISO] nao achei import de anexos em env.py. Adicione manualmente:")
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

print("Criando modulo estudo (Bloco 1)...")
escrever(BACKEND / "app" / "modules" / "estudo" / "models.py", models_py)
escrever(BACKEND / "app" / "modules" / "estudo" / "schemas.py", schemas_py)
escrever(BACKEND / "app" / "modules" / "estudo" / "repository.py", repository_py)
escrever(BACKEND / "app" / "modules" / "estudo" / "service.py", service_py)
escrever(BACKEND / "app" / "modules" / "estudo" / "router.py", router_py)
escrever(BACKEND / "app" / "modules" / "estudo" / "__init__.py", init_py)

print()
print("Atualizando API router...")
escrever(BACKEND / "app" / "api" / "router.py", api_router_py)

print()
print("Atualizando migrations/env.py...")
atualizar_env_alembic()

print()
print("=" * 60)
print("PRONTO! Agora rode:")
print("  alembic revision --autogenerate -m 'criar tabelas estudo bloco 1'")
print("  alembic upgrade head")
print("=" * 60)