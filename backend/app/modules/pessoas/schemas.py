from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PessoaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    cpf: str | None = Field(None, max_length=14)
    email: EmailStr | None = None
    telefone: str | None = Field(None, max_length=20)
    data_nascimento: date | None = None
    endereco: str | None = None
    cidade: str | None = Field(None, max_length=100)
    estado: str | None = Field(None, min_length=2, max_length=2)
    batizado: bool = False
    membro: bool = True
    observacoes: str | None = None
    foto_url: str | None = Field(None, max_length=500)


class PessoaCreate(PessoaBase):
    igreja_id: UUID | None = None


class PessoaUpdate(BaseModel):
    nome: str | None = Field(None, min_length=2, max_length=200)
    cpf: str | None = None
    email: EmailStr | None = None
    telefone: str | None = None
    data_nascimento: date | None = None
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = None
    batizado: bool | None = None
    membro: bool | None = None
    observacoes: str | None = None
    foto_url: str | None = Field(None, max_length=500)


class IgrejaResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str
    sigla: str | None = None


class PessoaResponse(PessoaBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    igreja_id: UUID
    igreja: IgrejaResumo
    ativo: bool
    created_at: datetime
    updated_at: datetime

class AcompanhamentoResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tipo: str
    titulo: str
    data: date
    status: str
    sigiloso: bool
    responsavel_nome: str | None = None


class PessoaCompleta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str
    cpf: str | None = None
    email: str | None = None
    telefone: str | None = None
    data_nascimento: date | None = None
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = None
    batizado: bool
    membro: bool
    observacoes: str | None = None
    foto_url: str | None = None
    ativo: bool
    created_at: datetime
    updated_at: datetime
    igreja: IgrejaResumo | None = None
    total_acompanhamentos: int = 0
    ultima_interacao: datetime | None = None
    acompanhamentos: list[AcompanhamentoResumo] = []

class Aniversariante(BaseModel):
    id: UUID
    nome: str
    data_nascimento: date
    idade: int
    dias_ate: int          # negativo = passou; 0 = hoje; positivo = futuro
    telefone: str | None = None
    email: str | None = None
    igreja_nome: str | None = None
    foto_url: str | None = None


class AniversariantesResumo(BaseModel):
    hoje: list[Aniversariante]
    proximos_7_dias: list[Aniversariante]
    ultimos_7_dias: list[Aniversariante]
    total_hoje: int
    total_semana: int
