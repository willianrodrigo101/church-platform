"""Setup do fluxo de Reset de Senha."""
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
# 1. MODEL TokenResetSenha
# ============================================================
model_py = '''from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, UUIDMixin


class TokenResetSenha(Base, UUIDMixin):
    __tablename__ = "tokens_reset_senha"

    usuario_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    usado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )

    usuario = relationship("Usuario", lazy="joined")

    def __repr__(self) -> str:
        return f"<TokenResetSenha user={self.usuario_id} usado={self.usado}>"
'''

# ============================================================
# 2. SCHEMAS
# ============================================================
schemas_extra = '''

# ============ RESET DE SENHA ============

class EsqueciSenhaRequest(BaseModel):
    email: EmailStr


class EsqueciSenhaResponse(BaseModel):
    mensagem: str
    token_debug: str | None = None  # apenas em desenvolvimento


class ResetarSenhaRequest(BaseModel):
    token: str = Field(..., min_length=8)
    nova_senha: str = Field(..., min_length=6, max_length=100)


class TrocarSenhaRequest(BaseModel):
    senha_atual: str = Field(..., min_length=6)
    nova_senha: str = Field(..., min_length=6, max_length=100)


class AdminResetarSenhaRequest(BaseModel):
    nova_senha: str = Field(..., min_length=6, max_length=100)
'''

# ============================================================
# 3. SERVICE — adicionar metodos
# ============================================================
service_py = '''import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import settings
from app.core.exceptions.handlers import (
    BusinessRuleError,
    NotFoundError,
    PermissionDeniedError,
)
from app.modules.igreja.repository import IgrejaRepository
from app.modules.usuarios.models import TokenResetSenha, Usuario
from app.modules.usuarios.repository import UsuarioRepository
from app.modules.usuarios.security import (
    criar_token,
    hash_senha,
    verificar_senha,
)


class UsuarioService:
    def __init__(self, db: AsyncSession):
        self.repo = UsuarioRepository(db)
        self.igreja_repo = IgrejaRepository(db)
        self.db = db

    # ============ AUTENTICACAO ============
    async def autenticar(self, email: str, senha: str):
        usuario = await self.repo.buscar_por_email(email)
        if not usuario or not usuario.ativo:
            raise BusinessRuleError("Credenciais invalidas")
        if not verificar_senha(senha, usuario.senha_hash):
            raise BusinessRuleError("Credenciais invalidas")
        token = criar_token({"sub": str(usuario.id), "role": usuario.role})
        return {"access_token": token, "token_type": "bearer", "usuario": usuario}

    async def setup_inicial(self, dados: dict):
        if await self.repo.contar() > 0:
            raise BusinessRuleError("Setup ja foi executado.")
        dados["role"] = "admin"
        return await self.criar(dados)

    # ============ CRUD ============
    async def criar(self, dados: dict):
        existente = await self.repo.buscar_por_email(dados["email"])
        if existente:
            raise BusinessRuleError("Ja existe usuario com este email")

        role = dados.get("role", "membro")
        igreja_id = dados.get("igreja_id")

        if role != "admin" and not igreja_id:
            raise BusinessRuleError(
                "Usuario com role diferente de admin precisa estar vinculado a uma igreja"
            )

        if igreja_id:
            igreja = await self.igreja_repo.buscar_por_id(igreja_id)
            if not igreja:
                raise BusinessRuleError("Igreja informada nao existe")
            if not igreja.ativa:
                raise BusinessRuleError("Nao e possivel vincular usuario a igreja inativa")

        dados["senha_hash"] = hash_senha(dados.pop("senha"))
        return await self.repo.criar(dados)

    async def buscar(self, usuario_id: UUID):
        u = await self.repo.buscar_por_id(usuario_id)
        if not u:
            raise NotFoundError("Usuario", str(usuario_id))
        return u

    async def listar(self, skip=0, limit=100, role=None, igreja_id=None, apenas_ativos=False):
        return await self.repo.listar(skip, limit, role, igreja_id, apenas_ativos)

    async def atualizar(self, usuario_id, dados, editor):
        usuario = await self.buscar(usuario_id)
        if str(editor.id) == str(usuario_id) and "role" in dados:
            if dados["role"] != usuario.role:
                raise PermissionDeniedError("alterar sua propria role")
        if "igreja_id" in dados and dados["igreja_id"]:
            igreja = await self.igreja_repo.buscar_por_id(dados["igreja_id"])
            if not igreja:
                raise BusinessRuleError("Igreja informada nao existe")
        return await self.repo.atualizar(usuario, dados)

    async def desativar(self, usuario_id, editor):
        if str(editor.id) == str(usuario_id):
            raise PermissionDeniedError("desativar a si mesmo")
        usuario = await self.buscar(usuario_id)
        if not usuario.ativo:
            raise BusinessRuleError("Usuario ja esta desativado")
        if usuario.role == "admin":
            total = await self.repo.contar_admins_ativos()
            if total <= 1:
                raise BusinessRuleError("Nao e possivel desativar o ultimo admin ativo")
        return await self.repo.atualizar(usuario, {"ativo": False})

    async def reativar(self, usuario_id):
        usuario = await self.buscar(usuario_id)
        if usuario.ativo:
            raise BusinessRuleError("Usuario ja esta ativo")
        return await self.repo.atualizar(usuario, {"ativo": True})

    async def deletar(self, usuario_id, editor):
        if str(editor.id) == str(usuario_id):
            raise PermissionDeniedError("excluir a si mesmo")
        usuario = await self.buscar(usuario_id)
        if usuario.role == "admin":
            total = await self.repo.contar_admins_ativos()
            if total <= 1:
                raise BusinessRuleError("Nao e possivel excluir o ultimo admin ativo")
        await self.repo.deletar(usuario)

    # ============ RESET DE SENHA ============

    async def trocar_propria_senha(self, usuario: Usuario, senha_atual: str, nova_senha: str):
        """Usuario logado troca a propria senha."""
        if not verificar_senha(senha_atual, usuario.senha_hash):
            raise BusinessRuleError("Senha atual incorreta")
        if verificar_senha(nova_senha, usuario.senha_hash):
            raise BusinessRuleError("Nova senha deve ser diferente da atual")
        await self.repo.atualizar(usuario, {"senha_hash": hash_senha(nova_senha)})
        return {"mensagem": "Senha alterada com sucesso"}

    async def admin_resetar_senha(self, usuario_id: UUID, nova_senha: str, editor: Usuario):
        """Admin reseta senha de outro usuario."""
        usuario = await self.buscar(usuario_id)
        await self.repo.atualizar(usuario, {"senha_hash": hash_senha(nova_senha)})
        return {"mensagem": f"Senha de {usuario.nome} resetada com sucesso"}

    async def esqueci_senha(self, email: str):
        """Gera token de reset. Em dev, retorna o token na resposta."""
        usuario = await self.repo.buscar_por_email(email)
        # Seguranca: sempre retorna mesma mensagem, mesmo se email nao existir
        resposta_padrao = {
            "mensagem": "Se o email estiver cadastrado, um token de reset foi gerado. "
                        "Procure o administrador do sistema para obter o token."
        }
        if not usuario or not usuario.ativo:
            return resposta_padrao

        # Gera token aleatorio
        token = secrets.token_urlsafe(32)
        expira_em = datetime.now(timezone.utc) + timedelta(hours=1)

        obj = TokenResetSenha(
            usuario_id=usuario.id,
            token=token,
            expira_em=expira_em,
        )
        self.db.add(obj)
        await self.db.flush()

        # Em desenvolvimento, devolve o token para facilitar
        if settings.ENVIRONMENT == "development":
            resposta_padrao["token_debug"] = token

        return resposta_padrao

    async def resetar_com_token(self, token: str, nova_senha: str):
        """Valida token e troca a senha."""
        r = await self.db.execute(
            select(TokenResetSenha).where(TokenResetSenha.token == token)
        )
        obj = r.scalar_one_or_none()
        if not obj:
            raise BusinessRuleError("Token invalido ou expirado")
        if obj.usado:
            raise BusinessRuleError("Este token ja foi utilizado")
        if obj.expira_em < datetime.now(timezone.utc):
            raise BusinessRuleError("Token expirado. Solicite um novo.")

        usuario = await self.buscar(obj.usuario_id)
        if not usuario.ativo:
            raise BusinessRuleError("Usuario inativo")

        await self.repo.atualizar(usuario, {"senha_hash": hash_senha(nova_senha)})
        obj.usado = True
        await self.db.flush()

        return {"mensagem": "Senha redefinida com sucesso. Faca login novamente."}
'''

# ============================================================
# 4. ROUTER — adicionar endpoints
# ============================================================
router_py = '''from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database.connection import get_db
from app.core.exceptions.handlers import PermissionDeniedError
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import (
    AdminResetarSenhaRequest,
    EsqueciSenhaRequest,
    EsqueciSenhaResponse,
    LoginRequest,
    ResetarSenhaRequest,
    TokenResponse,
    TrocarSenhaRequest,
    UsuarioAdminCreate,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)
from app.modules.usuarios.service import UsuarioService


router = APIRouter(prefix="/auth", tags=["Autenticacao"])


def apenas_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.role != "admin":
        raise PermissionDeniedError("acesso restrito a administradores")
    return usuario


# ============ PUBLICO ============

@router.post("/setup", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def setup_inicial(dados: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    return await UsuarioService(db).setup_inicial(dados.model_dump())


@router.post("/login", response_model=TokenResponse)
async def login(dados: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await UsuarioService(db).autenticar(dados.email, dados.senha)


@router.post("/esqueci-senha", response_model=EsqueciSenhaResponse)
async def esqueci_senha(dados: EsqueciSenhaRequest, db: AsyncSession = Depends(get_db)):
    return await UsuarioService(db).esqueci_senha(dados.email)


@router.post("/resetar-senha")
async def resetar_senha(dados: ResetarSenhaRequest, db: AsyncSession = Depends(get_db)):
    return await UsuarioService(db).resetar_com_token(dados.token, dados.nova_senha)


# ============ AUTENTICADO ============

@router.get("/me", response_model=UsuarioResponse)
async def me(usuario: Usuario = Depends(get_current_user)):
    return usuario


@router.put("/me/senha")
async def trocar_minha_senha(
    dados: TrocarSenhaRequest,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await UsuarioService(db).trocar_propria_senha(
        usuario, dados.senha_atual, dados.nova_senha,
    )


# ============ APENAS ADMIN ============

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register(
    dados: UsuarioAdminCreate,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    return await UsuarioService(db).criar(dados.model_dump())


@router.get("/usuarios", response_model=list[UsuarioResponse])
async def listar_usuarios(
    skip: int = 0, limit: int = 100,
    role: str | None = None, igreja_id: UUID | None = None,
    apenas_ativos: bool = False,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    return await UsuarioService(db).listar(skip, limit, role, igreja_id, apenas_ativos)


@router.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def buscar_usuario(
    usuario_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    return await UsuarioService(db).buscar(usuario_id)


@router.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def atualizar_usuario(
    usuario_id: UUID, dados: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    return await UsuarioService(db).atualizar(usuario_id, dados.model_dump(exclude_unset=True), editor=admin)


@router.patch("/usuarios/{usuario_id}/desativar", response_model=UsuarioResponse)
async def desativar_usuario(
    usuario_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    return await UsuarioService(db).desativar(usuario_id, editor=admin)


@router.patch("/usuarios/{usuario_id}/reativar", response_model=UsuarioResponse)
async def reativar_usuario(
    usuario_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    return await UsuarioService(db).reativar(usuario_id)


@router.put("/usuarios/{usuario_id}/resetar-senha")
async def admin_resetar_senha(
    usuario_id: UUID, dados: AdminResetarSenhaRequest,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    return await UsuarioService(db).admin_resetar_senha(usuario_id, dados.nova_senha, editor=admin)


@router.delete("/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_usuario(
    usuario_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(apenas_admin),
):
    await UsuarioService(db).deletar(usuario_id, editor=admin)
'''

# ============================================================
# 5. __init__ do modulo usuarios (atualiza import)
# ============================================================
init_py = '''from app.modules.usuarios.models import TokenResetSenha, Usuario

__all__ = ["Usuario", "TokenResetSenha"]
'''

# ============================================================
# ATUALIZAR SCHEMAS existentes (adiciona novos)
# ============================================================
def atualizar_schemas():
    p = BACKEND / "app" / "modules" / "usuarios" / "schemas.py"
    if not p.exists():
        print(f"  [AVISO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "EsqueciSenhaRequest" in c:
        print("  [SKIP] schemas.py ja tem classes de reset")
        return
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    c = c.rstrip() + schemas_extra
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] schemas.py atualizado")


def atualizar_env_alembic():
    p = BACKEND / "migrations" / "env.py"
    if not p.exists():
        return
    c = p.read_text(encoding="utf-8")
    if "TokenResetSenha" in c or "tokens_reset" in c:
        print("  [SKIP] env.py ja considera reset")
        return
    # TokenResetSenha esta no mesmo arquivo models.py do Usuario,
    # entao o import "from app.modules.usuarios import models" ja cobre.
    # Nao precisa fazer nada.
    print("  [SKIP] env.py nao precisa atualizar (mesmo models.py)")


print(f"Backend: {BACKEND}")
print()

print("Criando modulo de reset de senha...")
escrever(BACKEND / "app" / "modules" / "usuarios" / "models.py", model_py)
escrever(BACKEND / "app" / "modules" / "usuarios" / "service.py", service_py)
escrever(BACKEND / "app" / "modules" / "usuarios" / "router.py", router_py)
escrever(BACKEND / "app" / "modules" / "usuarios" / "__init__.py", init_py)

print()
print("Atualizando schemas...")
atualizar_schemas()

print()
print("=" * 60)
print("PRONTO! Agora rode:")
print("  alembic revision --autogenerate -m 'criar tabela tokens_reset_senha'")
print("  alembic upgrade head")
print("=" * 60)