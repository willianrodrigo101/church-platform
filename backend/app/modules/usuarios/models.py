from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin, UUIDMixin


class Usuario(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "usuarios"

    igreja_id: Mapped["PGUUID | None"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="membro")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    igreja = relationship("Igreja", lazy="joined")

    def __repr__(self) -> str:
        return f"<Usuario {self.email} ({self.role})>"


class TokenResetSenha(Base, UUIDMixin):
    __tablename__ = "tokens_reset_senha"

    usuario_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    usado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )

    usuario = relationship("Usuario", lazy="joined")

    def __repr__(self) -> str:
        return f"<TokenResetSenha user={self.usuario_id} usado={self.usado}>"