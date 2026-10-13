from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.handlers import (
    BusinessRuleError,
    NotFoundError,
)
from app.modules.igreja.repository import IgrejaRepository


class IgrejaService:
    def __init__(self, db: AsyncSession):
        self.repo = IgrejaRepository(db)
        self.db = db

    async def criar(self, dados: dict):
        return await self.repo.criar(dados)

    async def buscar(self, igreja_id: UUID):
        igreja = await self.repo.buscar_por_id(igreja_id)
        if not igreja:
            raise NotFoundError("Igreja", str(igreja_id))
        return igreja

    async def listar(
        self,
        skip: int = 0,
        limit: int = 100,
        apenas_ativas: bool = False,
    ):
        return await self.repo.listar(skip, limit, apenas_ativas)

    async def atualizar(self, igreja_id: UUID, dados: dict):
        igreja = await self.buscar(igreja_id)
        return await self.repo.atualizar(igreja, dados)

    async def desativar(self, igreja_id: UUID):
        igreja = await self.buscar(igreja_id)
        if not igreja.ativa:
            raise BusinessRuleError("Igreja ja esta desativada")
        return await self.repo.atualizar(igreja, {"ativa": False})

    async def reativar(self, igreja_id: UUID):
        igreja = await self.buscar(igreja_id)
        if igreja.ativa:
            raise BusinessRuleError("Igreja ja esta ativa")
        return await self.repo.atualizar(igreja, {"ativa": True})

    async def deletar_com_protecao(self, igreja_id: UUID):
        igreja = await self.buscar(igreja_id)

        # PROTECAO MULTI-IGREJA: bloqueia exclusao se houver pessoas vinculadas
        from app.modules.pessoas.repository import PessoaRepository

        total = await PessoaRepository(self.db).contar_por_igreja(igreja.id)
        if total > 0:
            raise BusinessRuleError(
                f"Nao e possivel excluir: {total} pessoa(s) vinculada(s) a esta igreja. "
                "Desative a igreja em vez de exclui-la."
            )

        await self.repo.deletar(igreja)
