from datetime import datetime
from datetime import date
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint, DateTime
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
    icone: Mapped[str] = mapped_column(String(10), nullable=False, default="ðŸ…")
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


class Certificado(Base, UUIDMixin, TimestampMixin):
    """Certificado de conclusao de curso ou trilha."""
    __tablename__ = "certificados"
    __table_args__ = (
        UniqueConstraint("matricula_id", name="uq_certificados_matricula"),
        UniqueConstraint("codigo", name="uq_certificados_codigo"),
    )

    matricula_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("matriculas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    pessoa_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pessoas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    curso_id: Mapped["PGUUID | None"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("cursos.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    codigo: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    carga_horaria: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nota_final: Mapped[float | None] = mapped_column("nota_final", nullable=True)
    emitido_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    url_pdf: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cancelado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    matricula = relationship("Matricula", lazy="joined")
    pessoa = relationship("Pessoa", lazy="joined")
    curso = relationship("Curso", lazy="joined")


class Anotacao(Base, UUIDMixin, TimestampMixin):
    """Anotacoes pessoais do aluno sobre um modulo."""
    __tablename__ = "anotacoes"

    pessoa_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pessoas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    modulo_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("modulos_curso.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    favorito: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    pessoa = relationship("Pessoa", lazy="joined")
    modulo = relationship("ModuloCurso", lazy="joined")


class FerramentaEstudo(Base, UUIDMixin, TimestampMixin):
    """Catalogo curado de ferramentas externas de estudo."""
    __tablename__ = "ferramentas_estudo"

    igreja_id: Mapped["PGUUID | None"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="CASCADE"),
        nullable=True, index=True,
    )
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False, default="outro", index=True)
    icone: Mapped[str] = mapped_column(String(10), nullable=False, default="🔗")
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
