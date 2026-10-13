from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database.connection import get_db
from app.modules.jornada.schemas import (
    DashboardJornada,
    MarcarEtapaRequest,
    ProgressoCreate,
    ProgressoResponse,
    TrilhaCreate,
    TrilhaResponse,
    TrilhaUpdate,
)
from app.modules.jornada.service import ProgressoService, TrilhaService
from app.modules.usuarios.models import Usuario


router = APIRouter(prefix="/jornada", tags=["Jornada"])


# ============ DASHBOARD ============

@router.get("/dashboard", response_model=DashboardJornada)
async def dashboard(
    igreja_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ProgressoService(db).dashboard(usuario, igreja_id)


# ============ TRILHAS ============

@router.post("/trilhas/", response_model=TrilhaResponse, status_code=status.HTTP_201_CREATED)
async def criar_trilha(
    dados: TrilhaCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TrilhaService(db).criar(dados.model_dump(), usuario)


@router.get("/trilhas/", response_model=list[TrilhaResponse])
async def listar_trilhas(
    skip: int = 0, limit: int = 100,
    igreja_id: UUID | None = None,
    tipo: str | None = None,
    apenas_ativas: bool = False,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TrilhaService(db).listar(usuario, skip, limit, igreja_id, tipo, apenas_ativas)


@router.get("/trilhas/{trilha_id}", response_model=TrilhaResponse)
async def buscar_trilha(
    trilha_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TrilhaService(db).buscar(trilha_id)


@router.put("/trilhas/{trilha_id}", response_model=TrilhaResponse)
async def atualizar_trilha(
    trilha_id: UUID,
    dados: TrilhaUpdate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TrilhaService(db).atualizar(trilha_id, dados.model_dump(exclude_unset=True), usuario)


@router.patch("/trilhas/{trilha_id}/desativar", response_model=TrilhaResponse)
async def desativar_trilha(
    trilha_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TrilhaService(db).desativar(trilha_id, usuario)


@router.patch("/trilhas/{trilha_id}/reativar", response_model=TrilhaResponse)
async def reativar_trilha(
    trilha_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TrilhaService(db).reativar(trilha_id, usuario)


@router.delete("/trilhas/{trilha_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_trilha(
    trilha_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    await TrilhaService(db).deletar(trilha_id, usuario)


# ============ PROGRESSOS ============

@router.post("/progressos/", response_model=ProgressoResponse, status_code=status.HTTP_201_CREATED)
async def criar_progresso(
    dados: ProgressoCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ProgressoService(db).criar(dados.model_dump(), usuario)


@router.get("/progressos/", response_model=list[ProgressoResponse])
async def listar_progressos(
    skip: int = 0, limit: int = 100,
    igreja_id: UUID | None = None,
    pessoa_id: UUID | None = None,
    trilha_id: UUID | None = None,
    status_: str | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ProgressoService(db).listar(
        usuario, skip, limit, igreja_id, pessoa_id, trilha_id, status_,
    )


@router.get("/progressos/{progresso_id}", response_model=ProgressoResponse)
async def buscar_progresso(
    progresso_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ProgressoService(db).buscar(progresso_id)


@router.patch("/progressos/{progresso_id}/etapas/{etapa_id}", response_model=ProgressoResponse)
async def marcar_etapa(
    progresso_id: UUID,
    etapa_id: UUID,
    dados: MarcarEtapaRequest,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ProgressoService(db).marcar_etapa(
        progresso_id, etapa_id, dados.concluida, dados.observacao, usuario,
    )


@router.patch("/progressos/{progresso_id}/concluir", response_model=ProgressoResponse)
async def concluir_progresso(
    progresso_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ProgressoService(db).concluir(progresso_id, usuario)


@router.patch("/progressos/{progresso_id}/cancelar", response_model=ProgressoResponse)
async def cancelar_progresso(
    progresso_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ProgressoService(db).cancelar(progresso_id, usuario)


@router.delete("/progressos/{progresso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_progresso(
    progresso_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    await ProgressoService(db).deletar(progresso_id, usuario)
