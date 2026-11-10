from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class DocumentoCreate(BaseModel):
    pessoa_id: UUID
    tipo: str
    titulo: str
    conteudo: str | None = None

class DocumentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    igreja_id: UUID
    pessoa_id: UUID
    tipo: str
    titulo: str
    codigo_validacao: str
    pdf_url: str | None
    created_at: datetime
    pessoa_nome: str | None = None
