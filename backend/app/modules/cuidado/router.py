from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.api.permissions import pode_escrever_em_cuidado
from app.core.database.connection import get_db
from app.core.exceptions.handlers import PermissionDeniedError
from app.modules.cuidado.schemas import (
    AcompanhamentoCreate,
    AcompanhamentoResponse,
    AcompanhamentoUpdate,
    DashboardAlertas,
)
from app.modules.cuidado.service import AcompanhamentoService
from app.modules.usuarios.models import Usuario


router = APIRouter(prefix="/acompanhamentos", tags=["Cuidado Pastoral"])


def _exigir_escrita(usuario: Usuario):
    if not pode_escrever_em_cuidado(usuario):
        raise PermissionDeniedError("Seu perfil nao permite criar ou alterar acompanhamentos.")


@router.get("/dashboard/alertas", response_model=DashboardAlertas)
async def dashboard_alertas(
    igreja_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    service = AcompanhamentoService(db)
    return await service.dashboard(usuario, igreja_id)


@router.post("/", response_model=AcompanhamentoResponse, status_code=status.HTTP_201_CREATED)
async def criar(
    dados: AcompanhamentoCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_escrita(usuario)
    service = AcompanhamentoService(db)
    return await service.criar(dados.model_dump(), usuario)


@router.get("/", response_model=list[AcompanhamentoResponse])
async def listar(
    skip: int = 0, limit: int = 100,
    pessoa_id: UUID | None = None,
    igreja_id: UUID | None = None,
    tipo: str | None = None,
    status_: str | None = None,
    apenas_ativos: bool = False,
    apenas_vencidos: bool = False,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    service = AcompanhamentoService(db)
    return await service.listar(
        usuario, skip, limit, pessoa_id, igreja_id, tipo, status_,
        apenas_ativos, apenas_vencidos,
    )


@router.get("/{obj_id}", response_model=AcompanhamentoResponse)
async def buscar(
    obj_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    service = AcompanhamentoService(db)
    return await service.buscar(obj_id, usuario)


@router.put("/{obj_id}", response_model=AcompanhamentoResponse)
async def atualizar(
    obj_id: UUID,
    dados: AcompanhamentoUpdate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_escrita(usuario)
    service = AcompanhamentoService(db)
    return await service.atualizar(obj_id, dados.model_dump(exclude_unset=True), usuario)


@router.patch("/{obj_id}/concluir", response_model=AcompanhamentoResponse)
async def concluir(
    obj_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_escrita(usuario)
    service = AcompanhamentoService(db)
    return await service.concluir(obj_id, usuario)


@router.patch("/{obj_id}/reabrir", response_model=AcompanhamentoResponse)
async def reabrir(
    obj_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_escrita(usuario)
    service = AcompanhamentoService(db)
    return await service.reabrir(obj_id, usuario)


@router.delete("/{obj_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar(
    obj_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_escrita(usuario)
    service = AcompanhamentoService(db)
    await service.deletar(obj_id, usuario)