import os
import uuid as uuid_lib
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import settings
from app.core.exceptions.handlers import (
    BusinessRuleError,
    NotFoundError,
    PermissionDeniedError,
)
from app.modules.anexos.repository import AnexoRepository
from app.modules.usuarios.models import Usuario

# Configuracoes de upload
UPLOAD_DIR = Path("uploads")
TAMANHO_MAX = 10 * 1024 * 1024  # 10 MB
TIPOS_PERMITIDOS = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "audio/mpeg", "audio/mp4", "audio/ogg", "audio/wav",
    "text/plain",
}
EXTENSOES_PERMITIDAS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".mp3", ".m4a", ".ogg", ".wav",
    ".txt",
}

TIPOS_ENTIDADE_VALIDOS = {
    "pessoa", "evento", "acompanhamento", "pedido_oracao", "trilha",
}


class AnexoService:
    def __init__(self, db: AsyncSession):
        self.repo = AnexoRepository(db)
        self.db = db

    async def upload(
        self,
        arquivo: UploadFile,
        entidade_tipo: str,
        entidade_id: UUID,
        descricao: str | None,
        usuario: Usuario,
    ) -> dict:
        # Validacao basica
        if entidade_tipo not in TIPOS_ENTIDADE_VALIDOS:
            raise BusinessRuleError(
                f"Tipo de entidade invalido. Use: {', '.join(TIPOS_ENTIDADE_VALIDOS)}"
            )

        if not usuario.igreja_id:
            raise BusinessRuleError("Usuario sem igreja vinculada.")

        # Validacao de extensao
        nome_original = arquivo.filename or "arquivo"
        ext = Path(nome_original).suffix.lower()
        if ext not in EXTENSOES_PERMITIDAS:
            raise BusinessRuleError(f"Extensao nao permitida: {ext}")

        # Le o conteudo e valida tamanho
        conteudo = await arquivo.read()
        if len(conteudo) > TAMANHO_MAX:
            raise BusinessRuleError(
                f"Arquivo excede o limite de {TAMANHO_MAX // 1024 // 1024} MB"
            )

        if len(conteudo) == 0:
            raise BusinessRuleError("Arquivo vazio")

        # Gera nome unico
        ext_final = ext if ext else ".bin"
        nome_arquivo = f"{uuid_lib.uuid4().hex}{ext_final}"

        # Monta pasta: uploads/{igreja_id}/{entidade_tipo}/{entidade_id}/
        pasta = UPLOAD_DIR / str(usuario.igreja_id) / entidade_tipo / str(entidade_id)
        pasta.mkdir(parents=True, exist_ok=True)

        # Salva no disco
        caminho = pasta / nome_arquivo
        caminho.write_bytes(conteudo)

        # Cria registro no banco
        dados = {
            "igreja_id": usuario.igreja_id,
            "enviado_por": usuario.id,
            "entidade_tipo": entidade_tipo,
            "entidade_id": entidade_id,
            "nome_original": nome_original,
            "nome_arquivo": nome_arquivo,
            "mime_type": arquivo.content_type,
            "tamanho_bytes": len(conteudo),
            "descricao": descricao,
        }
        return await self.repo.criar(dados)

    async def buscar(self, obj_id: UUID):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Anexo", str(obj_id))
        return obj

    async def listar(self, usuario, entidade_tipo=None, entidade_id=None, skip=0, limit=100):
        igreja_id = usuario.igreja_id
        return await self.repo.listar(entidade_tipo, entidade_id, igreja_id, skip, limit)

    def caminho_arquivo(self, anexo) -> Path:
        return (
            UPLOAD_DIR
            / str(anexo.igreja_id)
            / anexo.entidade_tipo
            / str(anexo.entidade_id)
            / anexo.nome_arquivo
        )

    async def deletar(self, obj_id: UUID, usuario: Usuario):
        obj = await self.buscar(obj_id)

        # Autor ou admin pode deletar
        if usuario.role != "admin" and str(obj.enviado_por) != str(usuario.id):
            raise PermissionDeniedError("excluir anexo de outro usuario")

        # Remove do disco
        caminho = self.caminho_arquivo(obj)
        if caminho.exists():
            try:
                caminho.unlink()
            except Exception:
                pass

        await self.repo.deletar(obj)
