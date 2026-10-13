from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin, UUIDMixin


class Anexo(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "anexos"

    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    enviado_por: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    entidade_tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    entidade_id: Mapped["PGUUID"] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)

    nome_original: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tamanho_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    igreja = relationship("Igreja", lazy="joined")
    enviado_por_usuario = relationship("Usuario", lazy="joined")

    def __repr__(self) -> str:
        return f"<Anexo {self.nome_original} ({self.entidade_tipo})>"
