"""Modulo Estudo — Bloco 2: Turmas, Matriculas, Progresso, Presencas."""
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
# 1. MODELS — adiciona Turma, Matricula, ProgressoModulo, Presenca
# ============================================================
models_extra = '''

class Turma(Base, UUIDMixin, TimestampMixin):
    """Instancia de um curso: professor, horario, alunos."""
    __tablename__ = "turmas"

    curso_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("cursos.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    professor_id: Mapped["PGUUID | None"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_inicio: Mapped["date | None"] = mapped_column("data_inicio", nullable=True)
    data_fim: Mapped["date | None"] = mapped_column("data_fim", nullable=True)
    horario: Mapped[str | None] = mapped_column(String(100), nullable=True)
    local: Mapped[str | None] = mapped_column(String(200), nullable=True)
    vagas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    modalidade: Mapped[str] = mapped_column(String(20), nullable=False, default="presencial")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="planejada", index=True)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    curso = relationship("Curso", lazy="joined")
    igreja = relationship("Igreja", lazy="joined")
    professor = relationship("Usuario", lazy="joined")
    matriculas = relationship(
        "Matricula",
        back_populates="turma",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Turma {self.nome} ({self.status})>"


class Matricula(Base, UUIDMixin, TimestampMixin):
    """Aluno matriculado em uma turma."""
    __tablename__ = "matriculas"
    __table_args__ = (
        UniqueConstraint("turma_id", "pessoa_id", name="uq_matriculas_turma_pessoa"),
    )

    turma_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("turmas.id", ondelete="CASCADE"),
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

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="matriculado", index=True)
    nota_final: Mapped[float | None] = mapped_column("nota_final", nullable=True)
    progresso_percentual: Mapped[float] = mapped_column("progresso_percentual", nullable=False, default=0.0)
    data_matricula: Mapped["date"] = mapped_column("data_matricula", nullable=False)
    data_conclusao: Mapped["date | None"] = mapped_column("data_conclusao", nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    turma = relationship("Turma", back_populates="matriculas")
    pessoa = relationship("Pessoa", lazy="joined")
    progresso_modulos = relationship(
        "ProgressoModulo",
        back_populates="matricula",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Matricula turma={self.turma_id} pessoa={self.pessoa_id} ({self.status})>"


class ProgressoModulo(Base, UUIDMixin, TimestampMixin):
    """Progresso do aluno em cada modulo."""
    __tablename__ = "progresso_modulos"
    __table_args__ = (
        UniqueConstraint("matricula_id", "modulo_id", name="uq_progresso_modulos"),
    )

    matricula_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("matriculas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    modulo_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("modulos_curso.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    concluido: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    nota: Mapped[float | None] = mapped_column("nota", nullable=True)
    tentativas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    data_conclusao: Mapped["date | None"] = mapped_column("data_conclusao", nullable=True)

    matricula = relationship("Matricula", back_populates="progresso_modulos")
    modulo = relationship("ModuloCurso", lazy="joined")

    def __repr__(self) -> str:
        return f"<ProgressoModulo modulo={self.modulo_id} concluido={self.concluido}>"


class Presenca(Base, UUIDMixin, TimestampMixin):
    """Presenca do aluno em uma aula (modulo)."""
    __tablename__ = "presencas"
    __table_args__ = (
        UniqueConstraint("matricula_id", "modulo_id", "data_aula", name="uq_presencas"),
    )

    matricula_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("matriculas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    modulo_id: Mapped["PGUUID | None"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("modulos_curso.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    data_aula: Mapped["date"] = mapped_column("data_aula", nullable=False, index=True)
    presente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)

    matricula = relationship("Matricula", lazy="joined")

    def __repr__(self) -> str:
        return f"<Presenca matricula={self.matricula_id} data={self.data_aula} presente={self.presente}>"
'''


def adicionar_models():
    p = BACKEND / "app" / "modules" / "estudo" / "models.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe. Rode o setup_estudo.py primeiro.")
        return
    c = p.read_text(encoding="utf-8")
    if "class Turma(" in c:
        print("  [SKIP] models.py ja tem Turma")
        return

    # Ajusta imports no topo
    if "from datetime import date" not in c:
        c = "from datetime import date\n" + c
    if "Integer," not in c:
        c = c.replace(
            "from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint",
            "from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint",
        )

    # Anexa novas classes no final
    c = c.rstrip() + models_extra

    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] models.py atualizado (+4 tabelas)")


# ============================================================
# 2. SCHEMAS — adiciona novos schemas
# ============================================================
schemas_extra = '''

# ============ TURMAS ============

class TurmaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    horario: str | None = None
    local: str | None = None
    vagas: int | None = None
    modalidade: str = Field("presencial", pattern="^(presencial|online|hibrido)$")


class TurmaCreate(TurmaBase):
    curso_id: UUID
    professor_id: UUID | None = None
    igreja_id: UUID | None = None


class TurmaUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    horario: str | None = None
    local: str | None = None
    vagas: int | None = None
    modalidade: str | None = None
    professor_id: UUID | None = None
    status: str | None = None


class PessoaResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class UsuarioResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class CursoResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str
    nivel: str


class TurmaResponse(TurmaBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    curso_id: UUID
    igreja_id: UUID
    professor_id: UUID | None = None
    status: str
    ativa: bool
    created_at: datetime
    updated_at: datetime
    curso: CursoResumo | None = None
    professor: UsuarioResumo | None = None
    total_matriculas: int = 0


# ============ MATRICULAS ============

class MatriculaCreate(BaseModel):
    pessoa_id: UUID
    observacoes: str | None = None


class MatriculaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    turma_id: UUID
    pessoa_id: UUID
    igreja_id: UUID
    status: str
    nota_final: float | None = None
    progresso_percentual: float
    data_matricula: date
    data_conclusao: date | None = None
    observacoes: str | None = None
    created_at: datetime
    pessoa: PessoaResumo | None = None


# ============ PROGRESSO ============

class ProgressoModuloResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    matricula_id: UUID
    modulo_id: UUID
    concluido: bool
    nota: float | None = None
    tentativas: int
    data_conclusao: date | None = None


class MarcarModuloConcluido(BaseModel):
    concluido: bool = True
    nota: float | None = None


# ============ PRESENCA ============

class PresencaCreate(BaseModel):
    data_aula: date
    modulo_id: UUID | None = None
    presente: bool = True
    observacao: str | None = None


class PresencaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    matricula_id: UUID
    modulo_id: UUID | None = None
    data_aula: date
    presente: bool
    observacao: str | None = None


class ChamadaItem(BaseModel):
    matricula_id: UUID
    pessoa_id: UUID
    nome: str
    presente: bool


class ChamadaRequest(BaseModel):
    data_aula: date
    modulo_id: UUID | None = None
    presencas: list[dict]


# ============ DASHBOARD ============

class DashboardTurmas(BaseModel):
    total_turmas: int
    turmas_ativas: int
    total_matriculas: int
    media_progresso: float
    taxa_presenca: float
'''


def adicionar_schemas():
    p = BACKEND / "app" / "modules" / "estudo" / "schemas.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "class TurmaCreate" in c:
        print("  [SKIP] schemas.py ja tem Turma")
        return

    # Ajusta imports
    if "from datetime import datetime, date" not in c and "from datetime import datetime" in c:
        c = c.replace("from datetime import datetime", "from datetime import date, datetime")

    c = c.rstrip() + schemas_extra

    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] schemas.py atualizado")


# ============================================================
# 3. REPOSITORY — adiciona TurmaRepository, MatriculaRepository, etc.
# ============================================================
repo_extra = '''

class TurmaRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import Turma
        obj = Turma(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar_por_id(self, obj_id):
        from app.modules.estudo.models import Turma
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Turma)
            .options(selectinload(Turma.matriculas))
            .where(Turma.id == obj_id)
        )
        r = await self.db.execute(stmt)
        return r.unique().scalar_one_or_none()

    async def listar(self, skip=0, limit=100, igreja_id=None, curso_id=None, status=None, apenas_ativas=False):
        from app.modules.estudo.models import Turma
        stmt = select(Turma).order_by(Turma.created_at.desc())
        if igreja_id: stmt = stmt.where(Turma.igreja_id == igreja_id)
        if curso_id: stmt = stmt.where(Turma.curso_id == curso_id)
        if status: stmt = stmt.where(Turma.status == status)
        if apenas_ativas: stmt = stmt.where(Turma.ativa.is_(True))
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

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

    async def contar_matriculas(self, turma_id):
        from app.modules.estudo.models import Matricula
        from sqlalchemy import func
        r = await self.db.execute(
            select(func.count(Matricula.id)).where(Matricula.turma_id == turma_id)
        )
        return r.scalar_one()


class MatriculaRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import Matricula
        obj = Matricula(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar_por_id(self, obj_id):
        from app.modules.estudo.models import Matricula
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Matricula)
            .options(selectinload(Matricula.progresso_modulos))
            .where(Matricula.id == obj_id)
        )
        r = await self.db.execute(stmt)
        return r.unique().scalar_one_or_none()

    async def buscar_por_turma_e_pessoa(self, turma_id, pessoa_id):
        from app.modules.estudo.models import Matricula
        r = await self.db.execute(
            select(Matricula).where(
                Matricula.turma_id == turma_id,
                Matricula.pessoa_id == pessoa_id,
            )
        )
        return r.scalar_one_or_none()

    async def listar_por_turma(self, turma_id):
        from app.modules.estudo.models import Matricula
        r = await self.db.execute(
            select(Matricula).where(Matricula.turma_id == turma_id).order_by(Matricula.created_at.asc())
        )
        return list(r.scalars().all())

    async def listar_por_pessoa(self, pessoa_id, igreja_id=None):
        from app.modules.estudo.models import Matricula
        stmt = select(Matricula).where(Matricula.pessoa_id == pessoa_id).order_by(Matricula.created_at.desc())
        if igreja_id: stmt = stmt.where(Matricula.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

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


class ProgressoModuloRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import ProgressoModulo
        obj = ProgressoModulo(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar_por_matricula_e_modulo(self, matricula_id, modulo_id):
        from app.modules.estudo.models import ProgressoModulo
        r = await self.db.execute(
            select(ProgressoModulo).where(
                ProgressoModulo.matricula_id == matricula_id,
                ProgressoModulo.modulo_id == modulo_id,
            )
        )
        return r.scalar_one_or_none()

    async def listar_por_matricula(self, matricula_id):
        from app.modules.estudo.models import ProgressoModulo
        r = await self.db.execute(
            select(ProgressoModulo).where(ProgressoModulo.matricula_id == matricula_id)
        )
        return list(r.scalars().all())

    async def atualizar(self, obj, dados):
        for k, v in dados.items():
            setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


class PresencaRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import Presenca
        obj = Presenca(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar(self, matricula_id, modulo_id, data_aula):
        from app.modules.estudo.models import Presenca
        stmt = select(Presenca).where(
            Presenca.matricula_id == matricula_id,
            Presenca.data_aula == data_aula,
        )
        if modulo_id:
            stmt = stmt.where(Presenca.modulo_id == modulo_id)
        else:
            stmt = stmt.where(Presenca.modulo_id.is_(None))
        r = await self.db.execute(stmt)
        return r.scalar_one_or_none()

    async def listar_por_matricula(self, matricula_id):
        from app.modules.estudo.models import Presenca
        r = await self.db.execute(
            select(Presenca).where(Presenca.matricula_id == matricula_id).order_by(Presenca.data_aula.asc())
        )
        return list(r.scalars().all())

    async def contar_presentes(self, turma_id):
        from app.modules.estudo.models import Presenca, Matricula
        from sqlalchemy import func
        r = await self.db.execute(
            select(func.count(Presenca.id))
            .join(Matricula, Matricula.id == Presenca.matricula_id)
            .where(Matricula.turma_id == turma_id, Presenca.presente.is_(True))
        )
        return r.scalar_one()

    async def contar_total(self, turma_id):
        from app.modules.estudo.models import Presenca, Matricula
        from sqlalchemy import func
        r = await self.db.execute(
            select(func.count(Presenca.id))
            .join(Matricula, Matricula.id == Presenca.matricula_id)
            .where(Matricula.turma_id == turma_id)
        )
        return r.scalar_one()
'''


def adicionar_repositorios():
    p = BACKEND / "app" / "modules" / "estudo" / "repository.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "class TurmaRepository" in c:
        print("  [SKIP] repository.py ja tem TurmaRepository")
        return
    c = c.rstrip() + repo_extra
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] repository.py atualizado (+4 repositorios)")


# ============================================================
# 4. SERVICE — adiciona TurmaService, MatriculaService, etc.
# ============================================================
service_extra = '''

class TurmaService:
    def __init__(self, db):
        self.db = db
        self.repo = TurmaRepository(db)
        self.curso_repo = CursoRepository(db)
        self.igreja_repo = IgrejaRepository(db)

    async def _resolver_igreja(self, autor, igreja_id=None):
        if autor.role == "admin":
            if igreja_id: return igreja_id
            if autor.igreja_id: return autor.igreja_id
            igrejas = await self.igreja_repo.listar(apenas_ativas=True)
            if not igrejas:
                raise BusinessRuleError("Nenhuma igreja ativa cadastrada.")
            return igrejas[0].id
        if not autor.igreja_id:
            raise BusinessRuleError("Usuario sem igreja vinculada.")
        return autor.igreja_id

    async def criar(self, dados, autor):
        curso_id = dados.get("curso_id")
        curso = await self.curso_repo.buscar_por_id(curso_id)
        if not curso:
            raise BusinessRuleError("Curso informado nao existe")
        dados["igreja_id"] = await self._resolver_igreja(autor, dados.pop("igreja_id", None))
        return await self.repo.criar(dados)

    async def buscar(self, obj_id):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Turma", str(obj_id))
        return obj

    async def listar(self, usuario, skip=0, limit=100, igreja_id=None, curso_id=None, status=None, apenas_ativas=False):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        turmas = await self.repo.listar(skip, limit, igreja_id, curso_id, status, apenas_ativas)
        for t in turmas:
            t.total_matriculas = await self.repo.contar_matriculas(t.id)
        return turmas

    async def atualizar(self, obj_id, dados, usuario):
        obj = await self.buscar(obj_id)
        return await self.repo.atualizar(obj, dados)

    async def iniciar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if obj.status == "em_andamento":
            raise BusinessRuleError("Turma ja esta em andamento")
        return await self.repo.atualizar(obj, {"status": "em_andamento"})

    async def concluir(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if obj.status == "concluida":
            raise BusinessRuleError("Turma ja esta concluida")
        return await self.repo.atualizar(obj, {"status": "concluida"})

    async def deletar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if obj.matriculas:
            raise BusinessRuleError(
                f"Nao e possivel excluir: {len(obj.matriculas)} matricula(s) vinculada(s)."
            )
        await self.repo.deletar(obj)

    async def dashboard(self, usuario, igreja_id=None):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        turmas = await self.repo.listar(igreja_id=igreja_id, limit=10000)
        ativas = [t for t in turmas if t.ativa]
        total_matriculas = sum(await self.repo.contar_matriculas(t.id) for t in turmas)

        return {
            "total_turmas": len(turmas),
            "turmas_ativas": len(ativas),
            "total_matriculas": total_matriculas,
            "media_progresso": 0.0,
            "taxa_presenca": 0.0,
        }


class MatriculaService:
    def __init__(self, db):
        self.db = db
        self.repo = MatriculaRepository(db)
        self.turma_repo = TurmaRepository(db)
        self.pessoa_repo = PessoaRepository(db)
        self.prog_repo = ProgressoModuloRepository(db)
        self.mod_repo = ModuloRepository(db)

    async def criar(self, turma_id, dados, autor):
        turma = await self.turma_repo.buscar_por_id(turma_id)
        if not turma:
            raise NotFoundError("Turma", str(turma_id))
        if turma.status == "concluida":
            raise BusinessRuleError("Turma ja concluida. Nao aceita novas matriculas.")

        pessoa = await self.pessoa_repo.buscar_por_id(dados["pessoa_id"])
        if not pessoa:
            raise BusinessRuleError("Pessoa nao existe")
        if not pessoa.ativo:
            raise BusinessRuleError("Pessoa inativa")

        if turma.vagas is not None:
            total = await self.turma_repo.contar_matriculas(turma_id)
            if total >= turma.vagas:
                raise BusinessRuleError("Turma lotada")

        existente = await self.repo.buscar_por_turma_e_pessoa(turma_id, dados["pessoa_id"])
        if existente:
            raise BusinessRuleError("Pessoa ja esta matriculada nesta turma")

        from datetime import date as date_cls
        dados_mat = {
            "turma_id": turma_id,
            "pessoa_id": dados["pessoa_id"],
            "igreja_id": turma.igreja_id,
            "data_matricula": date_cls.today(),
            "observacoes": dados.get("observacoes"),
            "status": "matriculado",
        }
        mat = await self.repo.criar(dados_mat)

        # Cria progresso para cada modulo do curso
        curso = await self.curso_repo_buscar(turma.curso_id)
        if curso:
            modulos = await self.mod_repo.listar_por_curso(curso.id)
            for m in modulos:
                await self.prog_repo.criar({
                    "matricula_id": mat.id,
                    "modulo_id": m.id,
                    "concluido": False,
                    "tentativas": 0,
                })
        return mat

    async def curso_repo_buscar(self, curso_id):
        # Helper — usa o repository do curso
        from app.modules.estudo.repository import CursoRepository
        return await CursoRepository(self.db).buscar_por_id(curso_id)

    async def buscar(self, obj_id):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Matricula", str(obj_id))
        return obj

    async def listar_por_turma(self, turma_id):
        return await self.repo.listar_por_turma(turma_id)

    async def listar_por_pessoa(self, pessoa_id, usuario):
        igreja_id = usuario.igreja_id
        return await self.repo.listar_por_pessoa(pessoa_id, igreja_id)

    async def marcar_modulo(self, matricula_id, modulo_id, concluido, nota, usuario):
        mat = await self.buscar(matricula_id)
        if mat.status not in ("matriculado", "em_andamento"):
            raise BusinessRuleError("Matricula nao esta ativa")

        prog = await self.prog_repo.buscar_por_matricula_e_modulo(matricula_id, modulo_id)
        if not prog:
            raise NotFoundError("Progresso do modulo", str(modulo_id))

        from datetime import date as date_cls
        dados = {
            "concluido": concluido,
            "data_conclusao": date_cls.today() if concluido else None,
        }
        if nota is not None:
            dados["nota"] = nota
        dados["tentativas"] = (prog.tentativas or 0) + 1

        await self.prog_repo.atualizar(prog, dados)

        # Recalcula progresso percentual
        todos = await self.prog_repo.listar_por_matricula(matricula_id)
        if todos:
            concluidos = sum(1 for p in todos if p.concluido)
            pct = round((concluidos / len(todos)) * 100, 1)
            await self.repo.atualizar(mat, {"progresso_percentual": pct})

        return await self.buscar(matricula_id)

    async def aprovar(self, matricula_id, usuario):
        mat = await self.buscar(matricula_id)
        from datetime import date as date_cls
        return await self.repo.atualizar(mat, {
            "status": "aprovado",
            "data_conclusao": date_cls.today(),
        })

    async def desistir(self, matricula_id, usuario):
        mat = await self.buscar(matricula_id)
        return await self.repo.atualizar(mat, {"status": "desistente"})

    async def deletar(self, matricula_id, usuario):
        mat = await self.buscar(matricula_id)
        await self.repo.deletar(mat)


class PresencaService:
    def __init__(self, db):
        self.db = db
        self.repo = PresencaRepository(db)
        self.mat_repo = MatriculaRepository(db)
        self.turma_repo = TurmaRepository(db)

    async def buscar(self, obj_id):
        from app.modules.estudo.models import Presenca
        r = await self.db.execute(select(Presenca).where(Presenca.id == obj_id))
        return r.scalar_one_or_none()

    async def criar(self, matricula_id, dados, usuario):
        mat = await self.mat_repo.buscar_por_id(matricula_id)
        if not mat:
            raise NotFoundError("Matricula", str(matricula_id))

        existente = await self.repo.buscar(matricula_id, dados.get("modulo_id"), dados["data_aula"])
        if existente:
            from app.modules.estudo.models import Presenca
            for k, v in dados.items():
                setattr(existente, k, v)
            await self.db.flush()
            await self.db.refresh(existente)
            return existente

        dados["matricula_id"] = matricula_id
        return await self.repo.criar(dados)

    async def chamada(self, turma_id, data_aula, modulo_id, presencas, usuario):
        turma = await self.turma_repo.buscar_por_id(turma_id)
        if not turma:
            raise NotFoundError("Turma", str(turma_id))

        resultados = []
        for item in presencas:
            mat_id = item.get("matricula_id")
            presente = item.get("presente", False)
            if not mat_id:
                continue
            r = await self.criar(mat_id, {
                "data_aula": data_aula,
                "modulo_id": modulo_id,
                "presente": presente,
            }, usuario)
            resultados.append(r)
        return resultados

    async def listar_por_matricula(self, matricula_id):
        return await self.repo.listar_por_matricula(matricula_id)

    async def deletar(self, obj_id, usuario):
        from app.modules.estudo.models import Presenca
        r = await self.db.execute(select(Presenca).where(Presenca.id == obj_id))
        obj = r.scalar_one_or_none()
        if not obj:
            raise NotFoundError("Presenca", str(obj_id))
        await self.db.delete(obj)
        await self.db.flush()
'''


def adicionar_services():
    p = BACKEND / "app" / "modules" / "estudo" / "service.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "class TurmaService" in c:
        print("  [SKIP] service.py ja tem TurmaService")
        return

    # Atualiza imports no topo
    if "from app.modules.estudo.repository import (" not in c:
        novo_import = """from app.modules.estudo.repository import (
    ConteudoRepository,
    CursoRepository,
    MatriculaRepository,
    ModuloRepository,
    PresencaRepository,
    ProgressoModuloRepository,
    TrilhaRepository,
    TurmaRepository,
)
"""
        c = c.replace(
            "from app.modules.estudo.repository import (\n    ConteudoRepository,\n    CursoRepository,\n    ModuloRepository,\n    TrilhaRepository,\n)",
            novo_import.strip(),
        )

    if "from app.modules.pessoas.repository import PessoaRepository" not in c:
        c = c.replace(
            "from app.modules.igreja.repository import IgrejaRepository",
            "from app.modules.igreja.repository import IgrejaRepository\nfrom app.modules.pessoas.repository import PessoaRepository",
        )

    if "from sqlalchemy import select" not in c:
        c = "from sqlalchemy import select\n" + c

    c = c.rstrip() + service_extra

    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] service.py atualizado (+3 services)")


# ============================================================
# 5. ROUTER — adiciona endpoints
# ============================================================
router_extra = '''

# ============ TURMAS ============

@router.get("/turmas/dashboard", response_model=DashboardTurmas)
async def dashboard_turmas(
    igreja_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TurmaService(db).dashboard(usuario, igreja_id)


@router.post("/turmas/", response_model=TurmaResponse, status_code=status.HTTP_201_CREATED)
async def criar_turma(dados: TurmaCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await TurmaService(db).criar(dados.model_dump(), usuario)


@router.get("/turmas/", response_model=list[TurmaResponse])
async def listar_turmas(
    skip: int = 0, limit: int = 100,
    igreja_id: UUID | None = None,
    curso_id: UUID | None = None,
    status_: str | None = None,
    apenas_ativas: bool = False,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TurmaService(db).listar(usuario, skip, limit, igreja_id, curso_id, status_, apenas_ativas)


@router.get("/turmas/{turma_id}", response_model=TurmaResponse)
async def buscar_turma(turma_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await TurmaService(db).buscar(turma_id)


@router.put("/turmas/{turma_id}", response_model=TurmaResponse)
async def atualizar_turma(turma_id: UUID, dados: TurmaUpdate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await TurmaService(db).atualizar(turma_id, dados.model_dump(exclude_unset=True), usuario)


@router.patch("/turmas/{turma_id}/iniciar", response_model=TurmaResponse)
async def iniciar_turma(turma_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await TurmaService(db).iniciar(turma_id, usuario)


@router.patch("/turmas/{turma_id}/concluir", response_model=TurmaResponse)
async def concluir_turma(turma_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await TurmaService(db).concluir(turma_id, usuario)


@router.delete("/turmas/{turma_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_turma(turma_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    await TurmaService(db).deletar(turma_id, usuario)


# ============ MATRICULAS ============

@router.post("/turmas/{turma_id}/matriculas/", response_model=MatriculaResponse, status_code=status.HTTP_201_CREATED)
async def criar_matricula(turma_id: UUID, dados: MatriculaCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await MatriculaService(db).criar(turma_id, dados.model_dump(), usuario)


@router.get("/turmas/{turma_id}/matriculas/", response_model=list[MatriculaResponse])
async def listar_matriculas_turma(turma_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await MatriculaService(db).listar_por_turma(turma_id)


@router.get("/pessoas/{pessoa_id}/matriculas/", response_model=list[MatriculaResponse])
async def listar_matriculas_pessoa(pessoa_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await MatriculaService(db).listar_por_pessoa(pessoa_id, usuario)


@router.get("/matriculas/{matricula_id}", response_model=MatriculaResponse)
async def buscar_matricula(matricula_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await MatriculaService(db).buscar(matricula_id)


@router.patch("/matriculas/{matricula_id}/modulos/{modulo_id}", response_model=MatriculaResponse)
async def marcar_modulo_concluido(
    matricula_id: UUID,
    modulo_id: UUID,
    dados: MarcarModuloConcluido,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await MatriculaService(db).marcar_modulo(matricula_id, modulo_id, dados.concluido, dados.nota, usuario)


@router.patch("/matriculas/{matricula_id}/aprovar", response_model=MatriculaResponse)
async def aprovar_matricula(matricula_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await MatriculaService(db).aprovar(matricula_id, usuario)


@router.patch("/matriculas/{matricula_id}/desistir", response_model=MatriculaResponse)
async def desistir_matricula(matricula_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await MatriculaService(db).desistir(matricula_id, usuario)


@router.delete("/matriculas/{matricula_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_matricula(matricula_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    await MatriculaService(db).deletar(matricula_id, usuario)


# ============ PRESENCAS ============

@router.post("/matriculas/{matricula_id}/presencas/", response_model=PresencaResponse, status_code=status.HTTP_201_CREATED)
async def criar_presenca(matricula_id: UUID, dados: PresencaCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await PresencaService(db).criar(matricula_id, dados.model_dump(), usuario)


@router.get("/matriculas/{matricula_id}/presencas/", response_model=list[PresencaResponse])
async def listar_presencas(matricula_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await PresencaService(db).listar_por_matricula(matricula_id)


@router.post("/turmas/{turma_id}/chamada")
async def fazer_chamada(turma_id: UUID, dados: ChamadaRequest, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await PresencaService(db).chamada(turma_id, dados.data_aula, dados.modulo_id, dados.presencas, usuario)


@router.delete("/presencas/{presenca_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_presenca(presenca_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    await PresencaService(db).deletar(presenca_id, usuario)
'''


def adicionar_router():
    p = BACKEND / "app" / "modules" / "estudo" / "router.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "/turmas/" in c:
        print("  [SKIP] router.py ja tem turmas")
        return

    # Atualiza imports
    novo_import_schemas = """from app.modules.estudo.schemas import (
    ChamadaRequest,
    ConteudoCreate,
    ConteudoResponse,
    CursoCreate,
    CursoResponse,
    CursoUpdate,
    DashboardEstudo,
    DashboardTurmas,
    MarcarModuloConcluido,
    MatriculaCreate,
    MatriculaResponse,
    ModuloCreate,
    ModuloResponse,
    ModuloUpdate,
    PresencaCreate,
    PresencaResponse,
    TrilhaCreate,
    TrilhaResponse,
    TrilhaUpdate,
    TurmaCreate,
    TurmaResponse,
    TurmaUpdate,
)"""

    import re
    c = re.sub(
        r"from app\.modules\.estudo\.schemas import \([^)]+\)",
        novo_import_schemas,
        c,
        count=1,
    )

    novo_import_services = """from app.modules.estudo.service import (
    ConteudoService,
    CursoService,
    MatriculaService,
    ModuloService,
    PresencaService,
    TrilhaService,
    TurmaService,
)"""

    c = re.sub(
        r"from app\.modules\.estudo\.service import \([^)]+\)",
        novo_import_services,
        c,
        count=1,
    )

    c = c.rstrip() + router_extra

    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] router.py atualizado (+20 endpoints)")


print(f"Backend: {BACKEND}")
print()
print("Bloco 2 — Turmas + Matriculas + Progresso + Presencas")
print()
adicionar_models()
adicionar_schemas()
adicionar_repositorios()
adicionar_services()
adicionar_router()

print()
print("=" * 60)
print("PRONTO! Agora rode:")
print("  alembic revision --autogenerate -m 'estudo bloco 2'")
print("  alembic upgrade head")
print("=" * 60)