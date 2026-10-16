from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.api.permissions import pode_escrever_em_eventos
from app.core.database.connection import get_db
from app.core.exceptions.handlers import PermissionDeniedError
from app.modules.eventos.schemas import (
    DashboardEventos,
    EventoCreate,
    EventoResponse,
    EventoUpdate,
    InscricaoCheckin,
    InscricaoCreate,
    InscricaoResponse,
)
from app.modules.eventos.service import EventoService, InscricaoService
from app.modules.usuarios.models import Usuario


router = APIRouter(prefix="/eventos", tags=["Eventos"])


def _exigir_escrita(usuario: Usuario):
    if not pode_escrever_em_eventos(usuario):
        raise PermissionDeniedError("Seu perfil nao permite criar ou alterar eventos.")


# ============ EVENTOS ============

@router.get("/dashboard/proximos", response_model=DashboardEventos)
async def dashboard_proximos(
    igreja_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await EventoService(db).dashboard(usuario, igreja_id)


@router.post("/", response_model=EventoResponse, status_code=status.HTTP_201_CREATED)
async def criar(
    dados: EventoCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_escrita(usuario)
    return await EventoService(db).criar(dados.model_dump(), usuario)


@router.get("/", response_model=list[EventoResponse])
async def listar(
    skip: int = 0, limit: int = 100,
    igreja_id: UUID | None = None,
    tipo: str | None = None,
    apenas_ativos: bool = False,
    data_de: datetime | None = None,
    data_ate: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await EventoService(db).listar(
        usuario, skip, limit, igreja_id, tipo, apenas_ativos, data_de, data_ate,
    )


@router.get("/{evento_id}", response_model=EventoResponse)
async def buscar(
    evento_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await EventoService(db).buscar(evento_id)


@router.put("/{evento_id}", response_model=EventoResponse)
async def atualizar(
    evento_id: UUID,
    dados: EventoUpdate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_escrita(usuario)
    return await EventoService(db).atualizar(evento_id, dados.model_dump(exclude_unset=True), usuario)


@router.patch("/{evento_id}/desativar", response_model=EventoResponse)
async def desativar(
    evento_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_escrita(usuario)
    return await EventoService(db).desativar(evento_id, usuario)


@router.patch("/{evento_id}/reativar", response_model=EventoResponse)
async def reativar(
    evento_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_escrita(usuario)
    return await EventoService(db).reativar(evento_id, usuario)


@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar(
    evento_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_escrita(usuario)
    await EventoService(db).deletar(evento_id, usuario)


# ============ INSCRICOES ============

@router.post("/{evento_id}/inscricoes", response_model=InscricaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_inscricao(
    evento_id: UUID,
    dados: InscricaoCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    # TODO MUNDO se inscreve (inclusive membro)
    return await InscricaoService(db).criar(evento_id, dados.pessoa_id, dados.observacao, usuario)


@router.get("/{evento_id}/inscricoes", response_model=list[InscricaoResponse])
async def listar_inscricoes(
    evento_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await InscricaoService(db).listar_por_evento(evento_id)


@router.patch("/inscricoes/{inscricao_id}/checkin", response_model=InscricaoResponse)
async def checkin(
    inscricao_id: UUID,
    dados: InscricaoCheckin,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_escrita(usuario)
    return await InscricaoService(db).checkin(inscricao_id, dados.status, dados.observacao, usuario)


@router.delete("/inscricoes/{inscricao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_inscricao(
    inscricao_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_escrita(usuario)
    await InscricaoService(db).deletar(inscricao_id, usuario)