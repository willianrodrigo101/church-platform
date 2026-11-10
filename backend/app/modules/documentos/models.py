from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database.base import Base, TimestampMixin, UUIDMixin

class Documento(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "documentos"

    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("igrejas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    pessoa_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("pessoas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    tipo: Mapped[str] = mapped_column(String(50), nullable=False) # ex: recomendacao, desligamento, batismo
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    conteudo: Mapped[str | None] = mapped_column(Text, nullable=True)
    codigo_validacao: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    pdf_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    igreja = relationship("Igreja", lazy="joined")
    pessoa = relationship("Pessoa", lazy="joined")

    def __repr__(self) -> str:
        return f"<Documento {self.tipo} - {self.pessoa.nome}>"
