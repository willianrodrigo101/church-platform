import secrets
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
