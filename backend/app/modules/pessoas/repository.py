from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.pessoas.models import Pessoa


class PessoaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict) -> Pessoa:
        pessoa = Pessoa(**dados)
        self.db.add(pessoa)
        await self.db.flush()
        await self.db.refresh(pessoa)
        return pessoa

    async def buscar_por_id(self, pessoa_id: UUID) -> Pessoa | None:
        result = await self.db.execute(
            select(Pessoa).where(Pessoa.id == pessoa_id)
        )
        return result.scalar_one_or_none()

    async def listar(
        self,
        skip: int = 0,
        limit: int = 100,
        igreja_id: UUID | None = None,
        apenas_ativos: bool = False,
        apenas_membros: bool | None = None,
    ) -> list[Pessoa]:
        stmt = select(Pessoa).order_by(Pessoa.nome.asc())

        if igreja_id:
            stmt = stmt.where(Pessoa.igreja_id == igreja_id)
        if apenas_ativos:
            stmt = stmt.where(Pessoa.ativo.is_(True))
        if apenas_membros is True:
            stmt = stmt.where(Pessoa.membro.is_(True))
        elif apenas_membros is False:
            stmt = stmt.where(Pessoa.membro.is_(False))

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def contar_por_igreja(self, igreja_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(Pessoa.id)).where(Pessoa.igreja_id == igreja_id)
        )
        return result.scalar_one()

    async def atualizar(self, pessoa: Pessoa, dados: dict) -> Pessoa:
        for k, v in dados.items():
            if v is not None:
                setattr(pessoa, k, v)
        await self.db.flush()
        await self.db.refresh(pessoa)
        return pessoa

    async def deletar(self, pessoa: Pessoa) -> None:
        await self.db.delete(pessoa)
        await self.db.flush()


    async def aniversariantes(
        self,
        igreja_id: UUID | None = None,
        janela_dias: int = 7,
    ) -> list[dict]:
        """
        Retorna aniversariantes numa janela de +/- janela_dias em torno de hoje.
        Considera apenas mes/dia (ignora ano de nascimento).
        """
        from datetime import date, timedelta
        from sqlalchemy import extract, or_, and_

        hoje = date.today()
        mes_hoje = hoje.month
        dia_hoje = hoje.day

        # Calcula o intervalo [hoje - janela, hoje + janela]
        inicio = hoje - timedelta(days=janela_dias)
        fim = hoje + timedelta(days=janela_dias)

        # Extrai mes e dia como inteiros para comparacao
        mes = extract("month", Pessoa.data_nascimento)
        dia = extract("day", Pessoa.data_nascimento)

        # Monta filtro: pessoa cujo (mes, dia) esteja no intervalo
        # Como pode cruzar virada de mes/ano, vamos pegar todos os que tem data_nascimento
        # e filtrar em Python (mais simples e confiavel)

        stmt = select(Pessoa).where(
            Pessoa.ativo.is_(True),
            Pessoa.data_nascimento.is_not(None),
        )
        if igreja_id:
            stmt = stmt.where(Pessoa.igreja_id == igreja_id)

        r = await self.db.execute(stmt)
        pessoas = list(r.scalars().all())

        resultado = []
        for p in pessoas:
            dn = p.data_nascimento
            # Proximo aniversario neste ano
            try:
                aniv_este_ano = dn.replace(year=hoje.year)
            except ValueError:
                # 29 de fevereiro em ano nao bissexto -> 28 de fevereiro
                aniv_este_ano = dn.replace(year=hoje.year, day=28)

            # Se ja passou, considera o ano que vem
            if aniv_este_ano < hoje:
                try:
                    aniv_prox = dn.replace(year=hoje.year + 1)
                except ValueError:
                    aniv_prox = dn.replace(year=hoje.year + 1, day=28)
            else:
                aniv_prox = aniv_este_ano

            # Tambem considera o do ano passado, para "ultimos 7 dias"
            try:
                aniv_ant = dn.replace(year=hoje.year - 1)
            except ValueError:
                aniv_ant = dn.replace(year=hoje.year - 1, day=28)

            # Pega o mais relevante (mais proximo de hoje)
            candidatos = [aniv_ant, aniv_este_ano, aniv_prox]
            melhor = min(candidatos, key=lambda d: abs((d - hoje).days))
            dias_ate = (melhor - hoje).days

            if abs(dias_ate) <= janela_dias:
                idade = hoje.year - dn.year - ((hoje.month, hoje.day) < (dn.month, dn.day))
                resultado.append({
                    "id": p.id,
                    "nome": p.nome,
                    "data_nascimento": dn,
                    "idade": idade,
                    "dias_ate": dias_ate,
                    "telefone": p.telefone,
                    "email": p.email,
                    "igreja_id": p.igreja_id,
                    "igreja_nome": p.igreja.nome if p.igreja else None,
                })

        # Ordena: hoje primeiro, depois proximos, depois passados
        resultado.sort(key=lambda x: (abs(x["dias_ate"]), x["dias_ate"] < 0))
        return resultado
