"""Setup do modulo Anexos (upload + download de arquivos)."""
import argparse, shutil
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).parent.resolve()
PROJETO = BACKEND.parent

parser = argparse.ArgumentParser()
parser.add_argument("--force", action="store_true")
args = parser.parse_args()
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

def escrever(caminho: Path, conteudo: str):
    if caminho.exists():
        if not args.force:
            print(f"  [SKIP] {caminho.relative_to(PROJETO)}")
            return
        backup = caminho.with_suffix(caminho.suffix + f".bak.{STAMP}")
        shutil.copy2(caminho, backup)
        print(f"  [BACKUP] {backup.name}")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(conteudo, encoding="utf-8")
    print(f"  [OK] {caminho.relative_to(PROJETO)}")


# ============================================================
# 1. MODEL
# ============================================================
models_py = '''from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin, UUIDMixin


class Anexo(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "anexos"

    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    enviado_por: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    entidade_tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    entidade_id: Mapped["PGUUID"] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)

    nome_original: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tamanho_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    igreja = relationship("Igreja", lazy="joined")
    enviado_por_usuario = relationship("Usuario", lazy="joined")

    def __repr__(self) -> str:
        return f"<Anexo {self.nome_original} ({self.entidade_tipo})>"
'''

# ============================================================
# 2. SCHEMAS
# ============================================================
schemas_py = '''from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UsuarioResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class AnexoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    igreja_id: UUID
    enviado_por: UUID
    entidade_tipo: str
    entidade_id: UUID
    nome_original: str
    nome_arquivo: str
    mime_type: str | None = None
    tamanho_bytes: int
    descricao: str | None = None
    created_at: datetime
    enviado_por_usuario: UsuarioResumo | None = None

    @property
    def url_download(self) -> str:
        return f"/api/v1/anexos/{self.id}/download"
'''

# ============================================================
# 3. REPOSITORY
# ============================================================
repository_py = '''from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.anexos.models import Anexo


class AnexoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict) -> Anexo:
        obj = Anexo(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar_por_id(self, obj_id: UUID) -> Anexo | None:
        r = await self.db.execute(select(Anexo).where(Anexo.id == obj_id))
        return r.scalar_one_or_none()

    async def listar(
        self,
        entidade_tipo: str | None = None,
        entidade_id: UUID | None = None,
        igreja_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Anexo]:
        stmt = select(Anexo).order_by(Anexo.created_at.desc())
        if entidade_tipo:
            stmt = stmt.where(Anexo.entidade_tipo == entidade_tipo)
        if entidade_id:
            stmt = stmt.where(Anexo.entidade_id == entidade_id)
        if igreja_id:
            stmt = stmt.where(Anexo.igreja_id == igreja_id)
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def deletar(self, obj: Anexo) -> None:
        await self.db.delete(obj)
        await self.db.flush()
'''

# ============================================================
# 4. SERVICE
# ============================================================
service_py = '''import os
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
'''

# ============================================================
# 5. ROUTER
# ============================================================
router_py = '''from uuid import UUID

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
'''

# ============================================================
# 6. __init__
# ============================================================
init_py = '''from app.modules.anexos.models import Anexo

__all__ = ["Anexo"]
'''

# ============================================================
# 7. API ROUTER ATUALIZADO
# ============================================================
api_router_py = '''from fastapi import APIRouter

from app.modules.anexos.router import router as anexos_router
from app.modules.cuidado.router import router as cuidado_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.eventos.router import router as eventos_router
from app.modules.igreja.router import router as igreja_router
from app.modules.jornada.router import router as jornada_router
from app.modules.notificacoes.router import router as notificacoes_router
from app.modules.oracao.router import router as oracao_router
from app.modules.pessoas.router import router as pessoa_router
from app.modules.usuarios.router import router as auth_router

api_router = APIRouter()
api_router.include_router(dashboard_router)
api_router.include_router(notificacoes_router)
api_router.include_router(auth_router)
api_router.include_router(igreja_router)
api_router.include_router(pessoa_router)
api_router.include_router(cuidado_router)
api_router.include_router(oracao_router)
api_router.include_router(eventos_router)
api_router.include_router(jornada_router)
api_router.include_router(anexos_router)
'''


def atualizar_env_alembic():
    p = BACKEND / "migrations" / "env.py"
    if not p.exists():
        print(f"  [SKIP] env.py nao encontrado")
        return
    c = p.read_text(encoding="utf-8")
    if "anexos" in c:
        print("  [SKIP] env.py ja importa anexos")
        return
    linha_base = "from app.modules.jornada import models  # noqa: F401"
    linha_nova = "from app.modules.anexos import models  # noqa: F401"
    if linha_base not in c:
        print("  [AVISO] nao achei import de jornada em env.py. Adicione manualmente:")
        print(f"        {linha_nova}")
        return
    c = c.replace(linha_base, f"{linha_base}\n{linha_nova}")
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] env.py atualizado")


print(f"Backend: {BACKEND}")
print()

print("Criando modulo anexos...")
escrever(BACKEND / "app" / "modules" / "anexos" / "models.py", models_py)
escrever(BACKEND / "app" / "modules" / "anexos" / "schemas.py", schemas_py)
escrever(BACKEND / "app" / "modules" / "anexos" / "repository.py", repository_py)
escrever(BACKEND / "app" / "modules" / "anexos" / "service.py", service_py)
escrever(BACKEND / "app" / "modules" / "anexos" / "router.py", router_py)
escrever(BACKEND / "app" / "modules" / "anexos" / "__init__.py", init_py)

print()
print("Atualizando API router...")
escrever(BACKEND / "app" / "api" / "router.py", api_router_py)

print()
print("Atualizando migrations/env.py...")
atualizar_env_alembic()

print()
print("Criando pasta de uploads...")
uploads = BACKEND / "uploads"
uploads.mkdir(exist_ok=True)
print(f"  [OK] {uploads.relative_to(BACKEND)}/")

print()
print("=" * 60)
print("PRONTO! Agora rode:")
print("  alembic revision --autogenerate -m 'criar tabela anexos'")
print("  alembic upgrade head")
print("=" * 60)