from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IgrejaResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class PessoaResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class UsuarioResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


# ============ TRILHAS / ETAPAS ============

class EtapaTrilhaCreate(BaseModel):
    ordem: int = Field(..., ge=1)
    nome: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    obrigatoria: bool = True


class EtapaTrilhaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    ordem: int
    nome: str
    descricao: str | None = None
    obrigatoria: bool


class TrilhaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    tipo: str = Field("discipulado", pattern="^(batismo|discipulado|lideranca|outro)$")


class TrilhaCreate(TrilhaBase):
    igreja_id: UUID | None = None
    etapas: list[EtapaTrilhaCreate] = []


class TrilhaUpdate(BaseModel):
    nome: str | None = Field(None, min_length=2, max_length=200)
    descricao: str | None = None
    tipo: str | None = Field(None, pattern="^(batismo|discipulado|lideranca|outro)$")


class TrilhaResponse(TrilhaBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    igreja_id: UUID
    ativa: bool
    created_at: datetime
    updated_at: datetime
    etapas: list[EtapaTrilhaResponse] = []
    total_progressos: int = 0
    total_concluidos: int = 0


# ============ PROGRESSOS ============

class ProgressoCreate(BaseModel):
    pessoa_id: UUID
    trilha_id: UUID
    iniciado_em: date | None = None
    observacoes: str | None = None


class ProgressoEtapaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    etapa_id: UUID
    concluida: bool
    concluida_em: date | None = None
    observacao: str | None = None
    etapa: EtapaTrilhaResponse | None = None


class ProgressoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    pessoa_id: UUID
    trilha_id: UUID
    igreja_id: UUID
    responsavel_id: UUID
    status: str
    iniciado_em: date
    concluido_em: date | None = None
    observacoes: str | None = None
    created_at: datetime
    updated_at: datetime
    pessoa: PessoaResumo | None = None
    trilha: TrilhaResponse | None = None
    responsavel: UsuarioResumo | None = None
    etapas: list[ProgressoEtapaResponse] = []
    total_etapas: int = 0
    etapas_concluidas: int = 0
    progresso_percentual: float = 0.0


class MarcarEtapaRequest(BaseModel):
    concluida: bool = True
    observacao: str | None = None


class DashboardJornada(BaseModel):
    total_trilhas_ativas: int
    total_em_andamento: int
    total_concluidas: int
    concluidas_ultimos_30_dias: int
    pessoas_paradas_30d: int
    trilhas_mais_populares: list[dict]
