"""Estudo Bloco 3 — Quizzes + Forum + Badges."""
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
# 1. MODELS — Quiz, Tentativa, Comentario, Badge, Conquista
# ============================================================
models_extra = '''

class Quiz(Base, UUIDMixin, TimestampMixin):
    """Quiz de um modulo."""
    __tablename__ = "quizzes"

    modulo_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("modulos_curso.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    nota_minima: Mapped[float] = mapped_column("nota_minima", nullable=False, default=7.0)
    tentativas_max: Mapped[int | None] = mapped_column("tentativas_max", nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    modulo = relationship("ModuloCurso", lazy="joined")
    perguntas = relationship(
        "PerguntaQuiz",
        back_populates="quiz",
        cascade="all, delete-orphan",
        order_by="PerguntaQuiz.ordem",
        lazy="selectin",
    )


class PerguntaQuiz(Base, UUIDMixin):
    """Pergunta de multipla escolha."""
    __tablename__ = "perguntas_quiz"

    quiz_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    enunciado: Mapped[str] = mapped_column(Text, nullable=False)
    opcoes: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    resposta_correta: Mapped[int] = mapped_column("resposta_correta", nullable=False)  # indice
    pontuacao: Mapped[float] = mapped_column("pontuacao", nullable=False, default=1.0)

    quiz = relationship("Quiz", back_populates="perguntas")


class TentativaQuiz(Base, UUIDMixin, TimestampMixin):
    """Tentativa do aluno num quiz."""
    __tablename__ = "tentativas_quiz"

    quiz_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    matricula_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("matriculas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    nota: Mapped[float] = mapped_column("nota", nullable=False, default=0.0)
    acertos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    aprovado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    respostas: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON

    quiz = relationship("Quiz", lazy="joined")
    matricula = relationship("Matricula", lazy="joined")


class Comentario(Base, UUIDMixin, TimestampMixin):
    """Comentario/duvida num modulo."""
    __tablename__ = "comentarios"

    modulo_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("modulos_curso.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    pessoa_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pessoas.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    parent_id: Mapped["PGUUID | None"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("comentarios.id", ondelete="CASCADE"),
        nullable=True, index=True,
    )
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    fixado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    pessoa = relationship("Pessoa", lazy="joined")


class Badge(Base, UUIDMixin, TimestampMixin):
    """Badge/conquista definida."""
    __tablename__ = "badges"

    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    codigo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    icone: Mapped[str] = mapped_column(String(10), nullable=False, default="🏅")
    cor: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pontos: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    __table_args__ = (
        UniqueConstraint("igreja_id", "codigo", name="uq_badges_igreja_codigo"),
    )


class Conquista(Base, UUIDMixin, TimestampMixin):
    """Badge conquistado por uma pessoa."""
    __tablename__ = "conquistas"
    __table_args__ = (
        UniqueConstraint("badge_id", "pessoa_id", name="uq_conquistas_badge_pessoa"),
    )

    badge_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("badges.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    pessoa_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pessoas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    badge = relationship("Badge", lazy="joined")
    pessoa = relationship("Pessoa", lazy="joined")
'''


def adicionar_models():
    p = BACKEND / "app" / "modules" / "estudo" / "models.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "class Quiz(" in c:
        print("  [SKIP] models.py ja tem Quiz")
        return
    c = c.rstrip() + models_extra
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] models.py atualizado (+5 tabelas)")


# ============================================================
# 2. SCHEMAS
# ============================================================
schemas_extra = '''

# ============ QUIZ ============

class PerguntaCreate(BaseModel):
    ordem: int = Field(1, ge=1)
    enunciado: str = Field(..., min_length=2)
    opcoes: list[str] = Field(..., min_length=2)
    resposta_correta: int = Field(..., ge=0)
    pontuacao: float = 1.0


class PerguntaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    ordem: int
    enunciado: str
    opcoes: str
    resposta_correta: int
    pontuacao: float


class QuizCreate(BaseModel):
    modulo_id: UUID
    titulo: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    nota_minima: float = 7.0
    tentativas_max: int | None = None
    perguntas: list[PerguntaCreate] = []


class QuizResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    modulo_id: UUID
    titulo: str
    descricao: str | None = None
    nota_minima: float
    tentativas_max: int | None = None
    ativo: bool
    created_at: datetime
    perguntas: list[PerguntaResponse] = []


class ResponderQuiz(BaseModel):
    respostas: dict[str, int]  # pergunta_id -> indice escolhido


class TentativaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    quiz_id: UUID
    matricula_id: UUID
    nota: float
    acertos: int
    total: int
    aprovado: bool
    created_at: datetime


# ============ COMENTARIO ============

class ComentarioCreate(BaseModel):
    texto: str = Field(..., min_length=1)


class ComentarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    modulo_id: UUID
    pessoa_id: UUID
    parent_id: UUID | None = None
    texto: str
    fixado: bool
    created_at: datetime
    pessoa: PessoaResumo | None = None


# ============ BADGE ============

class BadgeCreate(BaseModel):
    codigo: str = Field(..., min_length=2, max_length=50)
    nome: str = Field(..., min_length=2, max_length=100)
    descricao: str | None = None
    icone: str = "🏅"
    cor: str | None = None
    pontos: int = 10


class BadgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    codigo: str
    nome: str
    descricao: str | None = None
    icone: str
    cor: str | None = None
    pontos: int


class ConquistaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    badge_id: UUID
    pessoa_id: UUID
    badge: BadgeResponse | None = None
    created_at: datetime


class DashboardGamificacao(BaseModel):
    total_badges: int
    total_conquistas: int
    ranking: list[dict]
'''


def adicionar_schemas():
    p = BACKEND / "app" / "modules" / "estudo" / "schemas.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "class QuizCreate" in c:
        print("  [SKIP] schemas.py ja tem Quiz")
        return
    c = c.rstrip() + schemas_extra
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] schemas.py atualizado")


# ============================================================
# 3. REPOSITORY
# ============================================================
repo_extra = '''

class QuizRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados, perguntas):
        import json
        from app.modules.estudo.models import Quiz, PerguntaQuiz
        q = Quiz(**dados)
        self.db.add(q)
        await self.db.flush()
        for p in perguntas:
            opcoes = p.pop("opcoes", [])
            pergunta = PerguntaQuiz(quiz_id=q.id, opcoes=json.dumps(opcoes), **p)
            self.db.add(pergunta)
        await self.db.flush()
        await self.db.refresh(q)
        return q

    async def buscar_por_id(self, obj_id):
        from app.modules.estudo.models import Quiz
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Quiz)
            .options(selectinload(Quiz.perguntas))
            .where(Quiz.id == obj_id)
        )
        r = await self.db.execute(stmt)
        return r.unique().scalar_one_or_none()

    async def listar_por_modulo(self, modulo_id):
        from app.modules.estudo.models import Quiz
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Quiz)
            .options(selectinload(Quiz.perguntas))
            .where(Quiz.modulo_id == modulo_id)
        )
        r = await self.db.execute(stmt)
        return list(r.unique().scalars().all())

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()


class TentativaRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import TentativaQuiz
        t = TentativaQuiz(**dados)
        self.db.add(t)
        await self.db.flush()
        await self.db.refresh(t)
        return t

    async def contar_por_quiz_e_matricula(self, quiz_id, matricula_id):
        from app.modules.estudo.models import TentativaQuiz
        from sqlalchemy import func
        r = await self.db.execute(
            select(func.count(TentativaQuiz.id)).where(
                TentativaQuiz.quiz_id == quiz_id,
                TentativaQuiz.matricula_id == matricula_id,
            )
        )
        return r.scalar_one()

    async def listar_por_quiz(self, quiz_id):
        from app.modules.estudo.models import TentativaQuiz
        r = await self.db.execute(
            select(TentativaQuiz).where(TentativaQuiz.quiz_id == quiz_id)
            .order_by(TentativaQuiz.nota.desc())
        )
        return list(r.scalars().all())


class ComentarioRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import Comentario
        c = Comentario(**dados)
        self.db.add(c)
        await self.db.flush()
        await self.db.refresh(c)
        return c

    async def listar_por_modulo(self, modulo_id):
        from app.modules.estudo.models import Comentario
        r = await self.db.execute(
            select(Comentario).where(Comentario.modulo_id == modulo_id)
            .order_by(Comentario.fixado.desc(), Comentario.created_at.asc())
        )
        return list(r.scalars().all())

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()


class BadgeRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import Badge
        b = Badge(**dados)
        self.db.add(b)
        await self.db.flush()
        await self.db.refresh(b)
        return b

    async def listar(self, igreja_id):
        from app.modules.estudo.models import Badge
        r = await self.db.execute(
            select(Badge).where(Badge.igreja_id == igreja_id).order_by(Badge.pontos.desc())
        )
        return list(r.scalars().all())

    async def buscar_por_id(self, obj_id):
        from app.modules.estudo.models import Badge
        r = await self.db.execute(select(Badge).where(Badge.id == obj_id))
        return r.scalar_one_or_none()

    async def buscar_por_codigo(self, igreja_id, codigo):
        from app.modules.estudo.models import Badge
        r = await self.db.execute(
            select(Badge).where(Badge.igreja_id == igreja_id, Badge.codigo == codigo)
        )
        return r.scalar_one_or_none()

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()


class ConquistaRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import Conquista
        c = Conquista(**dados)
        self.db.add(c)
        await self.db.flush()
        await self.db.refresh(c)
        return c

    async def buscar(self, badge_id, pessoa_id):
        from app.modules.estudo.models import Conquista
        r = await self.db.execute(
            select(Conquista).where(
                Conquista.badge_id == badge_id,
                Conquista.pessoa_id == pessoa_id,
            )
        )
        return r.scalar_one_or_none()

    async def listar_por_pessoa(self, pessoa_id):
        from app.modules.estudo.models import Conquista
        r = await self.db.execute(
            select(Conquista).where(Conquista.pessoa_id == pessoa_id)
            .order_by(Conquista.created_at.desc())
        )
        return list(r.scalars().all())

    async def ranking(self, igreja_id, limit=10):
        from app.modules.estudo.models import Conquista, Badge, Pessoa
        from sqlalchemy import func
        r = await self.db.execute(
            select(Pessoa.nome, func.sum(Badge.pontos).label("total"))
            .join(Conquista, Conquista.pessoa_id == Pessoa.id)
            .join(Badge, Badge.id == Conquista.badge_id)
            .where(Conquista.igreja_id == igreja_id)
            .group_by(Pessoa.nome)
            .order_by(func.sum(Badge.pontos).desc())
            .limit(limit)
        )
        return [{"nome": row[0], "pontos": int(row[1] or 0)} for row in r.all()]
'''


def adicionar_repositorios():
    p = BACKEND / "app" / "modules" / "estudo" / "repository.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "class QuizRepository" in c:
        print("  [SKIP] repository.py ja tem QuizRepository")
        return
    c = c.rstrip() + repo_extra
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        # CORREÇÃO: 'caminho' foi trocado por 'p'
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] repository.py atualizado (+5 repositorios)")


# ============================================================
# 4. SERVICE
# ============================================================
service_extra = '''

class QuizService:
    def __init__(self, db):
        self.db = db
        self.repo = QuizRepository(db)
        self.tent_repo = TentativaRepository(db)
        self.mod_repo = ModuloRepository(db)

    async def criar(self, dados, autor):
        modulo_id = dados.get("modulo_id")
        mod = await self.mod_repo.buscar_por_id(modulo_id)
        if not mod:
            raise NotFoundError("Modulo", str(modulo_id))
        perguntas = dados.pop("perguntas", []) or []
        # Valida indice da resposta
        for i, p in enumerate(perguntas):
            if p.get("resposta_correta", 0) >= len(p.get("opcoes", [])):
                raise BusinessRuleError(f"Pergunta {i+1}: indice da resposta invalido")
        q = await self.repo.criar(dados, perguntas)
        return await self.repo.buscar_por_id(q.id)

    async def buscar(self, obj_id):
        q = await self.repo.buscar_por_id(obj_id)
        if not q:
            raise NotFoundError("Quiz", str(obj_id))
        return q

    async def listar_por_modulo(self, modulo_id):
        return await self.repo.listar_por_modulo(modulo_id)

    async def responder(self, quiz_id, matricula_id, respostas, usuario):
        import json
        quiz = await self.buscar(quiz_id)
        if not quiz.ativo:
            raise BusinessRuleError("Quiz desativado")

        # Verifica tentativas
        tentativas = await self.tent_repo.contar_por_quiz_e_matricula(quiz_id, matricula_id)
        if quiz.tentativas_max is not None and tentativas >= quiz.tentativas_max:
            raise BusinessRuleError(f"Limite de {quiz.tentativas_max} tentativas atingido")

        acertos = 0
        total = len(quiz.perguntas)
        for p in quiz.perguntas:
            resp = respostas.get(str(p.id))
            if resp is not None and int(resp) == p.resposta_correta:
                acertos += 1

        nota = round((acertos / total) * 10, 1) if total > 0 else 0.0
        aprovado = nota >= quiz.nota_minima

        t = await self.tent_repo.criar({
            "quiz_id": quiz_id,
            "matricula_id": matricula_id,
            "nota": nota,
            "acertos": acertos,
            "total": total,
            "aprovado": aprovado,
            "respostas": json.dumps(respostas),
        })

        # Atualiza progresso do modulo
        from app.modules.estudo.repository import ProgressoModuloRepository
        prog_repo = ProgressoModuloRepository(self.db)
        prog = await prog_repo.buscar_por_matricula_e_modulo(matricula_id, quiz.modulo_id)
        if prog:
            await prog_repo.atualizar(prog, {
                "concluido": aprovado,
                "nota": nota,
                "tentativas": (prog.tentativas or 0) + 1,
            })

        return t

    async def deletar(self, obj_id, usuario):
        q = await self.buscar(obj_id)
        await self.repo.deletar(q)


class ComentarioService:
    def __init__(self, db):
        self.db = db
        self.repo = ComentarioRepository(db)

    async def criar(self, modulo_id, texto, pessoa_id, parent_id=None, autor=None):
        return await self.repo.criar({
            "modulo_id": modulo_id,
            "pessoa_id": pessoa_id,
            "texto": texto,
            "parent_id": parent_id,
        })

    async def listar_por_modulo(self, modulo_id):
        return await self.repo.listar_por_modulo(modulo_id)

    async def deletar(self, obj_id, usuario):
        from app.modules.estudo.models import Comentario
        from sqlalchemy import select
        r = await self.db.execute(select(Comentario).where(Comentario.id == obj_id))
        c = r.scalar_one_or_none()
        if not c:
            raise NotFoundError("Comentario", str(obj_id))
        await self.repo.deletar(c)


class BadgeService:
    def __init__(self, db):
        self.db = db
        self.repo = BadgeRepository(db)
        self.conq_repo = ConquistaRepository(db)
        self.igreja_repo = IgrejaRepository(db)

    async def _resolver_igreja(self, autor):
        if autor.igreja_id:
            return autor.igreja_id
        igrejas = await self.igreja_repo.listar(apenas_ativas=True)
        if not igrejas:
            raise BusinessRuleError("Nenhuma igreja ativa cadastrada.")
        return igrejas[0].id

    async def criar(self, dados, autor):
        igreja_id = await self._resolver_igreja(autor)
        existente = await self.repo.buscar_por_codigo(igreja_id, dados["codigo"])
        if existente:
            raise BusinessRuleError(f"Ja existe badge com codigo '{dados['codigo']}'")
        dados["igreja_id"] = igreja_id
        return await self.repo.criar(dados)

    async def listar(self, autor):
        igreja_id = await self._resolver_igreja(autor)
        return await self.repo.listar(igreja_id)

    async def conceder(self, badge_id, pessoa_id, autor):
        badge = await self.repo.buscar_por_id(badge_id)
        if not badge:
            raise NotFoundError("Badge", str(badge_id))
        existente = await self.conq_repo.buscar(badge_id, pessoa_id)
        if existente:
            raise BusinessRuleError("Pessoa ja possui este badge")
        return await self.conq_repo.criar({
            "badge_id": badge_id,
            "pessoa_id": pessoa_id,
            "igreja_id": badge.igreja_id,
        })

    async def listar_conquistas_pessoa(self, pessoa_id):
        return await self.conq_repo.listar_por_pessoa(pessoa_id)

    async def ranking(self, autor, limit=10):
        igreja_id = await self._resolver_igreja(autor)
        return await self.conq_repo.ranking(igreja_id, limit)

    async def dashboard(self, autor):
        igreja_id = await self._resolver_igreja(autor)
        badges = await self.repo.listar(igreja_id)
        ranking = await self.conq_repo.ranking(igreja_id)
        return {
            "total_badges": len(badges),
            "total_conquistas": sum(1 for _ in ranking),  # simplificado
            "ranking": ranking,
        }
'''


def adicionar_services():
    p = BACKEND / "app" / "modules" / "estudo" / "service.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "class QuizService" in c:
        print("  [SKIP] service.py ja tem QuizService")
        return

    # Adiciona imports que faltam
    if "from app.modules.estudo.repository import" in c:
        c = c.replace(
            "from app.modules.estudo.repository import (\n    ConteudoRepository,\n    CursoRepository,\n    MatriculaRepository,\n    ModuloRepository,\n    PresencaRepository,\n    ProgressoModuloRepository,\n    TrilhaRepository,\n    TurmaRepository,\n)",
            "from app.modules.estudo.repository import (\n    BadgeRepository,\n    ComentarioRepository,\n    ConteudoRepository,\n    ConquistaRepository,\n    CursoRepository,\n    MatriculaRepository,\n    ModuloRepository,\n    PresencaRepository,\n    ProgressoModuloRepository,\n    QuizRepository,\n    TentativaRepository,\n    TrilhaRepository,\n    TurmaRepository,\n)",
        )

    c = c.rstrip() + service_extra

    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] service.py atualizado (+3 services)")


# ============================================================
# 5. ROUTER
# ============================================================
router_extra = '''

# ============ QUIZZES ============

@router.post("/quizzes/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def criar_quiz(dados: QuizCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await QuizService(db).criar(dados.model_dump(), usuario)


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
async def buscar_quiz(quiz_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await QuizService(db).buscar(quiz_id)


@router.get("/modulos/{modulo_id}/quizzes/", response_model=list[QuizResponse])
async def listar_quizzes_modulo(modulo_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await QuizService(db).listar_por_modulo(modulo_id)


@router.post("/quizzes/{quiz_id}/responder", response_model=TentativaResponse)
async def responder_quiz(
    quiz_id: UUID,
    dados: ResponderQuiz,
    matricula_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await QuizService(db).responder(quiz_id, matricula_id, dados.respostas, usuario)


@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_quiz(quiz_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    await QuizService(db).deletar(quiz_id, usuario)


# ============ COMENTARIOS ============

@router.post("/modulos/{modulo_id}/comentarios/", response_model=ComentarioResponse, status_code=status.HTTP_201_CREATED)
async def criar_comentario(
    modulo_id: UUID,
    dados: ComentarioCreate,
    pessoa_id: UUID,
    parent_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ComentarioService(db).criar(modulo_id, dados.texto, pessoa_id, parent_id, usuario)


@router.get("/modulos/{modulo_id}/comentarios/", response_model=list[ComentarioResponse])
async def listar_comentarios(modulo_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await ComentarioService(db).listar_por_modulo(modulo_id)


@router.delete("/comentarios/{comentario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_comentario(comentario_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    await ComentarioService(db).deletar(comentario_id, usuario)


# ============ BADGES ============

@router.post("/badges/", response_model=BadgeResponse, status_code=status.HTTP_201_CREATED)
async def criar_badge(dados: BadgeCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await BadgeService(db).criar(dados.model_dump(), usuario)


@router.get("/badges/", response_model=list[BadgeResponse])
async def listar_badges(db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await BadgeService(db).listar(usuario)


@router.post("/badges/{badge_id}/conceder", response_model=ConquistaResponse, status_code=status.HTTP_201_CREATED)
async def conceder_badge(
    badge_id: UUID,
    pessoa_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await BadgeService(db).conceder(badge_id, pessoa_id, usuario)


@router.get("/pessoas/{pessoa_id}/conquistas/", response_model=list[ConquistaResponse])
async def listar_conquistas(pessoa_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await BadgeService(db).listar_conquistas_pessoa(pessoa_id)


@router.get("/gamificacao/dashboard", response_model=DashboardGamificacao)
async def dashboard_gamificacao(db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await BadgeService(db).dashboard(usuario)
'''


def adicionar_router():
    p = BACKEND / "app" / "modules" / "estudo" / "router.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "/quizzes/" in c:
        print("  [SKIP] router.py ja tem quizzes")
        return

    # Adiciona imports
    import re
    novo_import_schemas = """from app.modules.estudo.schemas import (
    BadgeCreate,
    BadgeResponse,
    ChamadaRequest,
    ComentarioCreate,
    ComentarioResponse,
    ConteudoCreate,
    ConteudoResponse,
    ConquistaResponse,
    CursoCreate,
    CursoResponse,
    CursoUpdate,
    DashboardEstudo,
    DashboardGamificacao,
    DashboardTurmas,
    MarcarModuloConcluido,
    MatriculaCreate,
    MatriculaResponse,
    ModuloCreate,
    ModuloResponse,
    ModuloUpdate,
    PresencaCreate,
    PresencaResponse,
    QuizCreate,
    QuizResponse,
    ResponderQuiz,
    TentativaResponse,
    TrilhaCreate,
    TrilhaResponse,
    TrilhaUpdate,
    TurmaCreate,
    TurmaResponse,
    TurmaUpdate,
)"""

    c = re.sub(
        r"from app\.modules\.estudo\.schemas import \([^)]+\)",
        novo_import_schemas,
        c,
        count=1,
    )

    novo_import_services = """from app.modules.estudo.service import (
    BadgeService,
    ComentarioService,
    ConteudoService,
    CursoService,
    MatriculaService,
    ModuloService,
    PresencaService,
    QuizService,
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
    print(f"  [OK] router.py atualizado (+13 endpoints)")


print(f"Backend: {BACKEND}")
print()
print("Estudo Bloco 3 — Quizzes + Forum + Badges")
print()

adicionar_models()
adicionar_schemas()
adicionar_repositorios()
adicionar_services()
adicionar_router()

print()
print("=" * 60)
print("PRONTO! Agora rode:")
print("  alembic revision --autogenerate -m 'estudo bloco 3'")
print("  alembic upgrade head")
print("=" * 60)