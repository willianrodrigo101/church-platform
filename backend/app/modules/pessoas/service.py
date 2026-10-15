from datetime import date, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.permissions import (
    filtrar_pessoas_por_role,
    filtrar_por_igreja,
    is_admin,
)
from app.core.exceptions.handlers import (
    BusinessRuleError,
    NotFoundError,
    PermissionDeniedError,
)
from app.modules.igreja.repository import IgrejaRepository
from app.modules.pessoas.repository import PessoaRepository


class PessoaService:
    def __init__(self, db: AsyncSession):
        self.repo = PessoaRepository(db)
        self.igreja_repo = IgrejaRepository(db)
        self.db = db

    async def criar(self, dados: dict):
        igreja_id = dados.get("igreja_id")
        if not igreja_id:
            igrejas = await self.igreja_repo.listar(apenas_ativas=True)
            if len(igrejas) == 1:
                igreja_id = igrejas[0].id
                dados["igreja_id"] = igreja_id
            elif len(igrejas) == 0:
                raise BusinessRuleError("Nenhuma igreja ativa cadastrada. Cadastre uma igreja antes.")
            else:
                raise BusinessRuleError("Existem varias igrejas ativas. Informe 'igreja_id'.")
        igreja = await self.igreja_repo.buscar_por_id(igreja_id)
        if not igreja:
            raise BusinessRuleError("Igreja informada nao existe.")
        if not igreja.ativa:
            raise BusinessRuleError("Nao e possivel vincular pessoa a igreja inativa.")
        return await self.repo.criar(dados)

    async def buscar(self, pessoa_id: UUID, usuario=None):
        """
        Busca uma pessoa por id.

        Se 'usuario' for informado, aplica a regra de visibilidade:
        membro so pode buscar a si proprio.
        """
        pessoa = await self.repo.buscar_por_id(pessoa_id)
        if not pessoa:
            raise NotFoundError("Pessoa", str(pessoa_id))

        if usuario is not None and not self._pode_ver_pessoa(usuario, pessoa):
            raise PermissionDeniedError("Voce nao tem permissao para acessar esta pessoa.")

        return pessoa

    async def listar(
        self,
        skip=0,
        limit=100,
        igreja_id=None,
        apenas_ativos=False,
        apenas_membros=None,
        usuario=None,
    ):
        """
        Lista pessoas aplicando filtro de igreja + role.

        - admin: ve todas
        - pastor: ve da propria igreja
        - lider: ve da propria igreja (ministerio vem na Etapa 4)
        - membro: ve apenas a si proprio
        """
        return await self.repo.listar(
            skip=skip,
            limit=limit,
            igreja_id=igreja_id,
            apenas_ativos=apenas_ativos,
            apenas_membros=apenas_membros,
            usuario=usuario,
        )

    async def atualizar(self, pessoa_id: UUID, dados: dict, usuario=None):
        pessoa = await self.buscar(pessoa_id, usuario=usuario)
        return await self.repo.atualizar(pessoa, dados)

    async def desativar(self, pessoa_id: UUID):
        pessoa = await self.buscar(pessoa_id)
        if not pessoa.ativo:
            raise BusinessRuleError("Pessoa ja esta desativada")
        return await self.repo.atualizar(pessoa, {"ativo": False})

    async def reativar(self, pessoa_id: UUID):
        pessoa = await self.buscar(pessoa_id)
        if pessoa.ativo:
            raise BusinessRuleError("Pessoa ja esta ativa")
        return await self.repo.atualizar(pessoa, {"ativo": True})

    async def deletar_com_protecao(self, pessoa_id: UUID):
        pessoa = await self.buscar(pessoa_id)

        # Protecao: bloqueia exclusao se houver acompanhamentos
        from app.modules.cuidado.models import Acompanhamento
        r = await self.db.execute(
            select(func.count(Acompanhamento.id)).where(
                Acompanhamento.pessoa_id == pessoa_id
            )
        )
        total = r.scalar_one()
        if total > 0:
            raise BusinessRuleError(
                f"Nao e possivel excluir: {total} acompanhamento(s) vinculado(s) a esta pessoa. "
                "Desative a pessoa em vez de exclui-la."
            )

        await self.repo.deletar(pessoa)

    async def perfil_completo(self, pessoa_id: UUID, usuario):
        from app.modules.cuidado.models import Acompanhamento

        # Aplica visibilidade: membro so ve o proprio perfil
        pessoa = await self.buscar(pessoa_id, usuario=usuario)

        stmt = (
            select(Acompanhamento)
            .where(Acompanhamento.pessoa_id == pessoa_id, Acompanhamento.ativo.is_(True))
            .order_by(Acompanhamento.data.desc())
        )
        if not is_admin(usuario):
            stmt = stmt.where(
                (Acompanhamento.sigiloso.is_(False)) |
                (Acompanhamento.responsavel_id == usuario.id)
            )
        r = await self.db.execute(stmt)
        acomp_list = list(r.scalars().all())

        stmt_max = select(func.max(Acompanhamento.data)).where(
            Acompanhamento.pessoa_id == pessoa_id, Acompanhamento.ativo.is_(True),
        )
        if not is_admin(usuario):
            stmt_max = stmt_max.where(
                (Acompanhamento.sigiloso.is_(False)) |
                (Acompanhamento.responsavel_id == usuario.id)
            )
        r2 = await self.db.execute(stmt_max)
        ultima = r2.scalar_one_or_none()

        return {
            "id": pessoa.id,
            "nome": pessoa.nome,
            "cpf": pessoa.cpf,
            "email": pessoa.email,
            "telefone": pessoa.telefone,
            "data_nascimento": pessoa.data_nascimento,
            "endereco": pessoa.endereco,
            "cidade": pessoa.cidade,
            "estado": pessoa.estado,
            "batizado": pessoa.batizado,
            "membro": pessoa.membro,
            "observacoes": pessoa.observacoes,
            "ativo": pessoa.ativo,
            "created_at": pessoa.created_at,
            "updated_at": pessoa.updated_at,
            "igreja": pessoa.igreja,
            "total_acompanhamentos": len(acomp_list),
            "ultima_interacao": datetime.combine(ultima, datetime.min.time()) if ultima else None,
            "acompanhamentos": [
                {
                    "id": a.id, "tipo": a.tipo, "titulo": a.titulo,
                    "data": a.data, "status": a.status, "sigiloso": a.sigiloso,
                    "responsavel_nome": a.responsavel.nome if a.responsavel else None,
                }
                for a in acomp_list
            ],
        }

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _pode_ver_pessoa(self, usuario, pessoa) -> bool:
        """
        Regra de visibilidade de UMA pessoa especifica.

        - admin: ve tudo
        - pastor/lider: ve da propria igreja
        - membro: so a si proprio
        """
        if is_admin(usuario):
            return True

        # Membro so ve a si proprio
        if getattr(usuario, "role", None) == "membro":
            return getattr(usuario, "pessoa_id", None) == pessoa.id

        # Pastor / lider: da propria igreja
        user_igreja = getattr(usuario, "igreja_id", None)
        if user_igreja is None:
            return False
        return pessoa.igreja_id == user_igreja