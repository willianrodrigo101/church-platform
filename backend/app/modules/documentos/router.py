from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.connection import get_db
from app.api.dependencies import get_current_user
from app.modules.usuarios.models import Usuario
from .schemas import DocumentoCreate, DocumentoResponse
from .service import DocumentoService

router = APIRouter(prefix="/documentos", tags=["Documentos"])

@router.post("/gerar", response_model=DocumentoResponse)
async def gerar_documento(
    dados: DocumentoCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    service = DocumentoService(db)
    return await service.gerar_documento(dados.model_dump(), user.igreja_id, user.id)
