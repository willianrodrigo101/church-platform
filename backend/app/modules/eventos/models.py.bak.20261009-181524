from datetime import datetime

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
