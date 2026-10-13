from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin, UUIDMixin


class PedidoOracao(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "pedidos_oracao"

    pessoa_id: Mapped["PGUUID | None"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pessoas.id", ondelete="RESTRICT"),
        nullable=True, index=True,
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

    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    categoria: Mapped[str] = mapped_column(String(30), nullable=False, default="outro", index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="aberto", index=True)
    sigiloso: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    data_pedido: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    data_resposta: Mapped[date | None] = mapped_column(Date, nullable=True)
    testemunho: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    pessoa = relationship("Pessoa", lazy="joined")
    igreja = relationship("Igreja", lazy="joined")
    responsavel = relationship("Usuario", lazy="joined")

    def __repr__(self) -> str:
        return f"<PedidoOracao {self.titulo} ({self.status})>"
