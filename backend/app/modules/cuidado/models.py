from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin, UUIDMixin


class Acompanhamento(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "acompanhamentos"

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
    responsavel_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default="visita", index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    data: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    proximo_passo: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_retorno: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pendente", index=True)
    sigiloso: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    pessoa = relationship("Pessoa", lazy="joined")
    igreja = relationship("Igreja", lazy="joined")
    responsavel = relationship("Usuario", lazy="joined")

    def __repr__(self) -> str:
        return f"<Acompanhamento {self.tipo} - {self.titulo}>"
