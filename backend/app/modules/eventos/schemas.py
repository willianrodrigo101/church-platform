from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PessoaResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class UsuarioResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


# ============ EVENTOS ============

class EventoBase(BaseModel):
    titulo: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    tipo: str = Field("culto", pattern="^(culto|reuniao|conferencia|retiro|especial|outro)$")
    data_inicio: datetime
    data_fim: datetime | None = None
    local: str | None = Field(None, max_length=200)
    endereco: str | None = None
    vagas: int | None = Field(None, ge=0)
    publico: bool = True
    requer_inscricao: bool = False


class EventoCreate(EventoBase):
    igreja_id: UUID | None = None


class EventoUpdate(BaseModel):
    titulo: str | None = Field(None, min_length=2, max_length=200)
    descricao: str | None = None
    tipo: str | None = Field(None, pattern="^(culto|reuniao|conferencia|retiro|especial|outro)$")
    data_inicio: datetime | None = None
    data_fim: datetime | None = None
    local: str | None = None
    endereco: str | None = None
    vagas: int | None = Field(None, ge=0)
    publico: bool | None = None
    requer_inscricao: bool | None = None


class EventoResponse(EventoBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    igreja_id: UUID
    responsavel_id: UUID
    ativo: bool
    created_at: datetime
    updated_at: datetime
    responsavel: UsuarioResumo | None = None
    total_inscritos: int = 0
    total_presentes: int = 0


class EventoProximo(BaseModel):
    id: UUID
    titulo: str
    tipo: str
    data_inicio: datetime
    local: str | None = None
    vagas: int | None = None
    total_inscritos: int = 0
    dias_para_evento: int = 0


class DashboardEventos(BaseModel):
    total_proximos_7d: int
    total_proximos_30d: int
    proximos_eventos: list[EventoProximo]
    proximos: list[EventoProximo]  # alias compatível


# ============ INSCRICOES ============

class InscricaoCreate(BaseModel):
    pessoa_id: UUID
    observacao: str | None = None


class InscricaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    evento_id: UUID
    pessoa_id: UUID
    igreja_id: UUID
    status: str
    observacao: str | None = None
    created_at: datetime
    pessoa: PessoaResumo | None = None


class InscricaoCheckin(BaseModel):
    status: str = Field("presente", pattern="^(inscrito|presente|ausente|cancelado)$")
    observacao: str | None = None