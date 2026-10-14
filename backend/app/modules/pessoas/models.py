from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin, UUIDMixin


class Pessoa(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "pessoas"
    __table_args__ = (
        UniqueConstraint("igreja_id", "cpf", name="uq_pessoas_igreja_cpf"),
    )

    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    nome: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    cpf: Mapped[str | None] = mapped_column(String(14), nullable=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    data_nascimento: Mapped[date | None] = mapped_column(Date, nullable=True)

    endereco: Mapped[str | None] = mapped_column(Text, nullable=True)
    cidade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estado: Mapped[str | None] = mapped_column(String(2), nullable=True)

    batizado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    membro: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    foto_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    igreja = relationship("Igreja", lazy="joined")

    def __repr__(self) -> str:
        return f"<Pessoa {self.nome}>"
