from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database.connection import get_db
from app.modules.oracao.schemas import (
    DashboardOracao,
    MarcarAtendido,
    PedidoCreate,
    PedidoResponse,
    PedidoUpdate,
)
from app.modules.oracao.service import PedidoService
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/oracoes", tags=["Oracao"])


@router.get("/dashboard/alertas", response_model=DashboardOracao)
async def dashboard(igreja_id: UUID | None = None,
                    db: AsyncSession = Depends(get_db),
                    usuario: Usuario = Depends(get_current_user)):
    return await PedidoService(db).dashboard(usuario, igreja_id)


@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
async def criar(dados: PedidoCreate,
                db: AsyncSession = Depends(get_db),
                usuario: Usuario = Depends(get_current_user)):
    return await PedidoService(db).criar(dados.model_dump(), usuario)


@router.get("/", response_model=list[PedidoResponse])
async def listar(
    skip: int = 0, limit: int = 100,
    pessoa_id: UUID | None = None, igreja_id: UUID | None = None,
    categoria: str | None = None, status_: str | None = None,
    apenas_ativos: bool = False, apenas_sigilosos: bool | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await PedidoService(db).listar(
        usuario, skip, limit, pessoa_id, igreja_id, categoria, status_,
        apenas_ativos, apenas_sigilosos,
    )


@router.get("/{obj_id}", response_model=PedidoResponse)
async def buscar(obj_id: UUID, db: AsyncSession = Depends(get_db),
                 usuario: Usuario = Depends(get_current_user)):
    return await PedidoService(db).buscar(obj_id, usuario)


@router.put("/{obj_id}", response_model=PedidoResponse)
async def atualizar(obj_id: UUID, dados: PedidoUpdate,
                    db: AsyncSession = Depends(get_db),
                    usuario: Usuario = Depends(get_current_user)):
    return await PedidoService(db).atualizar(obj_id, dados.model_dump(exclude_unset=True), usuario)


@router.patch("/{obj_id}/marcar-atendido", response_model=PedidoResponse)
async def marcar_atendido(obj_id: UUID, dados: MarcarAtendido,
                          db: AsyncSession = Depends(get_db),
                          usuario: Usuario = Depends(get_current_user)):
    return await PedidoService(db).marcar_atendido(
        obj_id, dados.testemunho, dados.data_resposta, usuario,
    )


@router.patch("/{obj_id}/reabrir", response_model=PedidoResponse)
async def reabrir(obj_id: UUID, db: AsyncSession = Depends(get_db),
                  usuario: Usuario = Depends(get_current_user)):
    return await PedidoService(db).reabrir(obj_id, usuario)


@router.delete("/{obj_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar(obj_id: UUID, db: AsyncSession = Depends(get_db),
                  usuario: Usuario = Depends(get_current_user)):
    await PedidoService(db).deletar(obj_id, usuario)
