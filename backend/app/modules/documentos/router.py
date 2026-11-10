from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.connection import get_db
from app.api.dependencies import get_current_user
from app.modules.usuarios.models import Usuario
from app.modules.pessoas.repository import PessoaRepository
from .schemas import DocumentoCreate, DocumentoResponse
from .service import DocumentoService
from app.core.exceptions.handlers import BusinessRuleError
from pathlib import Path

router = APIRouter(prefix="/documentos", tags=["Documentos"])

@router.post("/gerar", response_model=DocumentoResponse)
async def gerar_documento(
    dados: DocumentoCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):
    pessoa_repo = PessoaRepository(db)
    pessoa = await pessoa_repo.buscar_por_id(dados.pessoa_id)
    if not pessoa:
        raise BusinessRuleError("Pessoa nao encontrada")
    
    igreja_id = user.igreja_id or pessoa.igreja_id
    if not igreja_id:
        raise BusinessRuleError("Igreja nao definida para gerar o documento")
        
    service = DocumentoService(db)
    return await service.gerar_documento(dados.model_dump(), igreja_id, user.id)

@router.get("/download/{codigo}")
async def baixar_pdf(codigo: str, db: AsyncSession = Depends(get_db)):
    # Aqui ele busca o PDF gerado anteriormente
    from sqlalchemy import select
    from .models import Documento
    r = await db.execute(select(Documento).where(Documento.codigo_validacao == codigo))
    doc = r.scalar_one_or_none()
    if not doc:
        raise BusinessRuleError("Documento nao encontrado")
    
    pdf_path = Path(__file__).parent.parent.parent / "static" / "media" / "docs" / f"doc_{codigo}.pdf"
    if not pdf_path.exists():
        raise BusinessRuleError("Arquivo PDF expirou. Gere novamente.")
        
    return Response(content=pdf_path.read_bytes(), media_type="application/pdf")