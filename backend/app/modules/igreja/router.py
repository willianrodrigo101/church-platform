from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.connection import get_db
from app.modules.igreja.schemas import IgrejaCreate, IgrejaUpdate, IgrejaResponse
from app.modules.igreja.service import IgrejaService


router = APIRouter(prefix="/igrejas", tags=["Igrejas"])


@router.post("/", response_model=IgrejaResponse, status_code=status.HTTP_201_CREATED)
async def criar_igreja(
    dados: IgrejaCreate,
    db: AsyncSession = Depends(get_db),
):
    service = IgrejaService(db)
    return await service.criar(dados.model_dump())


@router.get("/", response_model=list[IgrejaResponse])
async def listar_igrejas(
    skip: int = 0,
    limit: int = 100,
    apenas_ativas: bool = False,
    db: AsyncSession = Depends(get_db),
):
    service = IgrejaService(db)
    return await service.listar(skip, limit, apenas_ativas)


@router.get("/{igreja_id}", response_model=IgrejaResponse)
async def buscar_igreja(
    igreja_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = IgrejaService(db)
    return await service.buscar(igreja_id)


@router.put("/{igreja_id}", response_model=IgrejaResponse)
async def atualizar_igreja(
    igreja_id: UUID,
    dados: IgrejaUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = IgrejaService(db)
    return await service.atualizar(igreja_id, dados.model_dump(exclude_unset=True))


@router.patch("/{igreja_id}/desativar", response_model=IgrejaResponse)
async def desativar_igreja(
    igreja_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = IgrejaService(db)
    return await service.desativar(igreja_id)


@router.patch("/{igreja_id}/reativar", response_model=IgrejaResponse)
async def reativar_igreja(
    igreja_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = IgrejaService(db)
    return await service.reativar(igreja_id)


@router.delete("/{igreja_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_igreja(
    igreja_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = IgrejaService(db)
    await service.deletar_com_protecao(igreja_id)
