from datetime import date, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.handlers import (
    BusinessRuleError,
    NotFoundError,
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

    async def buscar(self, pessoa_id: UUID):
        pessoa = await self.repo.buscar_por_id(pessoa_id)
        if not pessoa:
            raise NotFoundError("Pessoa", str(pessoa_id))
        return pessoa

    async def listar(self, skip=0, limit=100, igreja_id=None, apenas_ativos=False, apenas_membros=None):
        return await self.repo.listar(skip, limit, igreja_id, apenas_ativos, apenas_membros)

    async def atualizar(self, pessoa_id: UUID, dados: dict):
        pessoa = await self.buscar(pessoa_id)
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

        pessoa = await self.buscar(pessoa_id)

        stmt = (
            select(Acompanhamento)
            .where(Acompanhamento.pessoa_id == pessoa_id, Acompanhamento.ativo.is_(True))
            .order_by(Acompanhamento.data.desc())
        )
        if usuario.role != "admin":
            stmt = stmt.where(
                (Acompanhamento.sigiloso.is_(False)) |
                (Acompanhamento.responsavel_id == usuario.id)
            )
        r = await self.db.execute(stmt)
        acomp_list = list(r.scalars().all())

        stmt_max = select(func.max(Acompanhamento.data)).where(
            Acompanhamento.pessoa_id == pessoa_id, Acompanhamento.ativo.is_(True),
        )
        if usuario.role != "admin":
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
