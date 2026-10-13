from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class IgrejaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    sigla: str | None = Field(None, max_length=20)
    cnpj: str | None = Field(None, max_length=18)
    email: EmailStr | None = None
    telefone: str | None = Field(None, max_length=20)
    endereco: str | None = None
    cidade: str | None = Field(None, max_length=100)
    estado: str | None = Field(None, min_length=2, max_length=2)


class IgrejaCreate(IgrejaBase):
    pass


class IgrejaUpdate(BaseModel):
    nome: str | None = Field(None, min_length=2, max_length=200)
    sigla: str | None = None
    email: EmailStr | None = None
    telefone: str | None = None
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = None
    ativa: bool | None = None


class IgrejaResponse(IgrejaBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    ativa: bool
    created_at: datetime
    updated_at: datetime
