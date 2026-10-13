from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database.connection import get_db
from app.core.exceptions.handlers import PermissionDeniedError
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import (
    AdminResetarSenhaRequest,
    EsqueciSenhaRequest,
    EsqueciSenhaResponse,
    LoginRequest,
    ResetarSenhaRequest,
    TokenResponse,
    TrocarSenhaRequest,
    UsuarioAdminCreate,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)
from app.modules.usuarios.service import UsuarioService


router = APIRouter(prefix="/auth", tags=["Autenticacao"])


def apenas_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.role != "admin":
        raise PermissionDeniedError("acesso restrito a administradores")
    return usuario


# ============ PUBLICO ============

@router.post("/setup", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def setup_inicial(dados: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    return await UsuarioService(db).setup_inicial(dados.model_dump())


@router.post("/login", response_model=TokenResponse)
async def login(dados: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await UsuarioService(db).autenticar(dados.email, dados.senha)


@router.post("/esqueci-senha", response_model=EsqueciSenhaResponse)
async def esqueci_senha(dados: EsqueciSenhaRequest, db: AsyncSession = Depends(get_db)):
    return await UsuarioService(db).esqueci_senha(dados.email)


@router.post("/resetar-senha")
async def resetar_senha(dados: ResetarSenhaRequest, db: AsyncSession = Depends(get_db)):
    return await UsuarioService(db).resetar_com_token(dados.token, dados.nova_senha)


# ============ AUTENTICADO ============

@router.get("/me", response_model=UsuarioResponse)
async def me(usuario: Usuario = Depends(get_current_user)):
    return usuario


@router.put("/me/senha")
async def trocar_minha_senha(
    dados: TrocarSenhaRequest,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await UsuarioService(db).trocar_propria_senha(
        usuario, dados.senha_atual, dados.nova_senha,
    )


# ============ APENAS ADMIN ============

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register(
    dados: UsuarioAdminCreate,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    return await UsuarioService(db).criar(dados.model_dump())


@router.get("/usuarios", response_model=list[UsuarioResponse])
async def listar_usuarios(
    skip: int = 0, limit: int = 100,
    role: str | None = None, igreja_id: UUID | None = None,
    apenas_ativos: bool = False,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    return await UsuarioService(db).listar(skip, limit, role, igreja_id, apenas_ativos)


@router.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def buscar_usuario(
    usuario_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    return await UsuarioService(db).buscar(usuario_id)


@router.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def atualizar_usuario(
    usuario_id: UUID, dados: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    return await UsuarioService(db).atualizar(usuario_id, dados.model_dump(exclude_unset=True), editor=admin)


@router.patch("/usuarios/{usuario_id}/desativar", response_model=UsuarioResponse)
async def desativar_usuario(
    usuario_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    return await UsuarioService(db).desativar(usuario_id, editor=admin)


@router.patch("/usuarios/{usuario_id}/reativar", response_model=UsuarioResponse)
async def reativar_usuario(
    usuario_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    return await UsuarioService(db).reativar(usuario_id)


@router.put("/usuarios/{usuario_id}/resetar-senha")
async def admin_resetar_senha(
    usuario_id: UUID, dados: AdminResetarSenhaRequest,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    return await UsuarioService(db).admin_resetar_senha(usuario_id, dados.nova_senha, editor=admin)


@router.delete("/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_usuario(
    usuario_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    await UsuarioService(db).deletar(usuario_id, editor=admin)
