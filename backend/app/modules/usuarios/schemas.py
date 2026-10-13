from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: "UsuarioResponse"


class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    senha: str = Field(..., min_length=6, max_length=100)
    role: str = Field("membro", pattern="^(admin|pastor|lider|membro)$")
    igreja_id: UUID | None = None


class UsuarioAdminCreate(BaseModel):
    """Criacao via painel admin. Sem senha obrigatoria (gera uma padrao)."""
    nome: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    senha: str = Field(..., min_length=6, max_length=100)
    role: str = Field("membro", pattern="^(admin|pastor|lider|membro)$")
    igreja_id: UUID | None = None


class UsuarioUpdate(BaseModel):
    nome: str | None = Field(None, min_length=2, max_length=200)
    role: str | None = Field(None, pattern="^(admin|pastor|lider|membro)$")
    igreja_id: UUID | None = None


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str
    email: EmailStr
    role: str
    ativo: bool
    igreja_id: UUID | None = None
    created_at: datetime


TokenResponse.model_rebuild()

# ============ RESET DE SENHA ============

class EsqueciSenhaRequest(BaseModel):
    email: EmailStr


class EsqueciSenhaResponse(BaseModel):
    mensagem: str
    token_debug: str | None = None  # apenas em desenvolvimento


class ResetarSenhaRequest(BaseModel):
    token: str = Field(..., min_length=8)
    nova_senha: str = Field(..., min_length=6, max_length=100)


class TrocarSenhaRequest(BaseModel):
    senha_atual: str = Field(..., min_length=6)
    nova_senha: str = Field(..., min_length=6, max_length=100)


class AdminResetarSenhaRequest(BaseModel):
    nova_senha: str = Field(..., min_length=6, max_length=100)
