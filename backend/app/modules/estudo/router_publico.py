"""Rotas publicas — validacao de certificado."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.connection import get_db
from app.modules.estudo.schemas import CertificadoValidacao
from app.modules.estudo.service import CertificadoService

router = APIRouter(prefix="/publico", tags=["Publico"])


@router.get("/certificados/validar/{codigo}", response_model=CertificadoValidacao)
async def validar_certificado(codigo: str, db: AsyncSession = Depends(get_db)):
    resultado = await CertificadoService(db).validar(codigo)
    if not resultado.get("valido"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=resultado.get("mensagem", "Certificado nao encontrado"),
        )
    return resultado
