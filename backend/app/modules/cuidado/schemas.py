from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


TIPOS = ["visita", "ligacao", "aconselhamento", "oracao", "outro"]
STATUS = ["pendente", "em_andamento", "concluido", "cancelado"]


class PessoaResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class UsuarioResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class AcompanhamentoBase(BaseModel):
    tipo: str = Field(..., pattern="^(visita|ligacao|aconselhamento|oracao|outro)$")
    titulo: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    data: date
    proximo_passo: str | None = None
    data_retorno: date | None = None
    sigiloso: bool = False


class AcompanhamentoCreate(AcompanhamentoBase):
    pessoa_id: UUID
    status: str = Field("pendente", pattern="^(pendente|em_andamento|concluido|cancelado)$")


class AcompanhamentoUpdate(BaseModel):
    tipo: str | None = Field(None, pattern="^(visita|ligacao|aconselhamento|oracao|outro)$")
    titulo: str | None = Field(None, min_length=2, max_length=200)
    descricao: str | None = None
    data: date | None = None
    proximo_passo: str | None = None
    data_retorno: date | None = None
    status: str | None = Field(None, pattern="^(pendente|em_andamento|concluido|cancelado)$")
    sigiloso: bool | None = None


class AcompanhamentoResponse(AcompanhamentoBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    pessoa_id: UUID
    igreja_id: UUID
    responsavel_id: UUID
    status: str
    ativo: bool
    created_at: datetime
    updated_at: datetime
    pessoa: PessoaResumo | None = None
    responsavel: UsuarioResumo | None = None


class PessoaSemInteracao(BaseModel):
    id: UUID
    nome: str
    email: str | None = None
    telefone: str | None = None
    ultima_interacao: datetime | None = None
    dias_sem_interacao: int | None = None


class AcompanhamentoVencido(BaseModel):
    id: UUID
    titulo: str
    tipo: str
    data_retorno: date
    dias_atraso: int
    pessoa_nome: str
    responsavel_nome: str


class DashboardAlertas(BaseModel):
    total_pessoas: int
    total_ativas: int
    pessoas_sem_interacao: list[PessoaSemInteracao]
    acompanhamentos_pendentes: int
    acompanhamentos_vencidos: list[AcompanhamentoVencido]
    retornos_proximos_7_dias: list[AcompanhamentoVencido]
    dias_sem_interacao: int
