from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database.connection import get_db
from app.modules.anexos.schemas import AnexoResponse
from app.modules.anexos.service import AnexoService
from app.modules.usuarios.models import Usuario


router = APIRouter(prefix="/anexos", tags=["Anexos"])


@router.post("/upload", response_model=AnexoResponse, status_code=status.HTTP_201_CREATED)
async def upload_anexo(
    arquivo: UploadFile = File(...),
    entidade_tipo: str = Form(...),
    entidade_id: UUID = Form(...),
    descricao: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    service = AnexoService(db)
    return await service.upload(arquivo, entidade_tipo, entidade_id, descricao, usuario)


@router.get("/", response_model=list[AnexoResponse])
async def listar_anexos(
    entidade_tipo: str | None = None,
    entidade_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    service = AnexoService(db)
    return await service.listar(usuario, entidade_tipo, entidade_id, skip, limit)


@router.get("/{anexo_id}", response_model=AnexoResponse)
async def buscar_anexo(
    anexo_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    service = AnexoService(db)
    return await service.buscar(anexo_id)


@router.get("/{anexo_id}/download")
async def download_anexo(
    anexo_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    service = AnexoService(db)
    anexo = await service.buscar(anexo_id)

    # Verifica igreja
    if usuario.igreja_id and str(anexo.igreja_id) != str(usuario.igreja_id):
        raise HTTPException(status_code=403, detail="Acesso negado")

    caminho = service.caminho_arquivo(anexo)
    if not caminho.exists():
        raise HTTPException(status_code=404, detail="Arquivo nao encontrado no disco")

    return FileResponse(
        path=caminho,
        filename=anexo.nome_original,
        media_type=anexo.mime_type or "application/octet-stream",
    )


@router.delete("/{anexo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_anexo(
    anexo_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    service = AnexoService(db)
    await service.deletar(anexo_id, usuario)
