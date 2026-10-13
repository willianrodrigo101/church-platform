from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UsuarioResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class AnexoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    igreja_id: UUID
    enviado_por: UUID
    entidade_tipo: str
    entidade_id: UUID
    nome_original: str
    nome_arquivo: str
    mime_type: str | None = None
    tamanho_bytes: int
    descricao: str | None = None
    created_at: datetime
    enviado_por_usuario: UsuarioResumo | None = None

    @property
    def url_download(self) -> str:
        return f"/api/v1/anexos/{self.id}/download"
