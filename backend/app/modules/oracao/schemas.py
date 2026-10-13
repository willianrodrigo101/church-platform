from datetime import date, datetime
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


class PedidoBase(BaseModel):
    titulo: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    categoria: str = Field("outro", pattern="^(saude|familia|financeiro|espiritual|trabalho|outro)$")
    sigiloso: bool = False
    data_pedido: date


class PedidoCreate(PedidoBase):
    pessoa_id: UUID | None = None
    status: str = Field("aberto", pattern="^(aberto|em_oracao|atendido|arquivado)$")


class PedidoUpdate(BaseModel):
    titulo: str | None = Field(None, min_length=2, max_length=200)
    descricao: str | None = None
    categoria: str | None = Field(None, pattern="^(saude|familia|financeiro|espiritual|trabalho|outro)$")
    status: str | None = Field(None, pattern="^(aberto|em_oracao|atendido|arquivado)$")
    sigiloso: bool | None = None
    data_pedido: date | None = None
    data_resposta: date | None = None
    testemunho: str | None = None


class MarcarAtendido(BaseModel):
    testemunho: str | None = None
    data_resposta: date | None = None


class PedidoResponse(PedidoBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    pessoa_id: UUID | None = None
    igreja_id: UUID
    responsavel_id: UUID
    status: str
    data_resposta: date | None = None
    testemunho: str | None = None
    ativo: bool
    created_at: datetime
    updated_at: datetime
    pessoa: PessoaResumo | None = None
    responsavel: UsuarioResumo | None = None


class PedidoAlerta(BaseModel):
    id: UUID
    titulo: str
    categoria: str
    data_pedido: date
    dias_aberto: int
    pessoa_nome: str | None = None
    responsavel_nome: str


class DashboardOracao(BaseModel):
    total: int
    abertos: int
    em_oracao: int
    atendidos: int
    sem_resposta_30d: list[PedidoAlerta]
    por_categoria: dict[str, int]
