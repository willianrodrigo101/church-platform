from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.connection import get_db
from app.api.dependencies import get_current_user
from app.modules.usuarios.models import Usuario
from app.modules.pessoas.repository import PessoaRepository
from .schemas import DocumentoCreate, DocumentoResponse
from .service import DocumentoService
from app.core.exceptions.handlers import BusinessRuleError

router = APIRouter(prefix="/documentos", tags=["Documentos"])

@router.post("/gerar", response_model=DocumentoResponse)
async def gerar_documento(
    dados: DocumentoCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    # Busca a pessoa para pegar a igreja dela
    pessoa_repo = PessoaRepository(db)
    pessoa = await pessoa_repo.buscar_por_id(dados.pessoa_id)
    if not pessoa:
        raise BusinessRuleError("Pessoa nao encontrada")
    
    # Define a igreja: usa a do usuário logado, ou a da pessoa
    igreja_id = user.igreja_id or pessoa.igreja_id
    if not igreja_id:
        raise BusinessRuleError("Igreja nao definida para gerar o documento")
        
    service = DocumentoService(db)
    return await service.gerar_documento(dados.model_dump(), igreja_id, user.id)