from datetime import date

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
