from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database.base import Base, TimestampMixin, UUIDMixin


class Igreja(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "igrejas"

    nome: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    sigla: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cnpj: Mapped[str | None] = mapped_column(String(18), nullable=True, unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    endereco: Mapped[str | None] = mapped_column(Text, nullable=True)
    cidade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estado: Mapped[str | None] = mapped_column(String(2), nullable=True)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
