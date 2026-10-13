from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.handlers import BusinessRuleError, NotFoundError, PermissionDeniedError
from app.modules.igreja.repository import IgrejaRepository
from app.modules.jornada.repository import ProgressoRepository, TrilhaRepository
from app.modules.pessoas.repository import PessoaRepository
from app.modules.usuarios.models import Usuario


class TrilhaService:
    def __init__(self, db: AsyncSession):
        self.repo = TrilhaRepository(db)
        self.prog_repo = ProgressoRepository(db)
        self.igreja_repo = IgrejaRepository(db)
        self.db = db

    async def criar(self, dados: dict, autor: Usuario):
        etapas = dados.pop("etapas", []) or []
        igreja_id = dados.pop("igreja_id", None)

        if autor.role == "admin":
            if not igreja_id:
                if autor.igreja_id:
                    igreja_id = autor.igreja_id
                else:
                    igrejas = await self.igreja_repo.listar(apenas_ativas=True)
                    if not igrejas:
                        raise BusinessRuleError("Nenhuma igreja ativa cadastrada.")
                    igreja_id = igrejas[0].id
        else:
            if not autor.igreja_id:
                raise BusinessRuleError("Usuario sem igreja vinculada.")
            igreja_id = autor.igreja_id

        dados["igreja_id"] = igreja_id

        # Normaliza ordem
        for i, e in enumerate(etapas, start=1):
            e["ordem"] = i

        return await self.repo.criar(dados, etapas)

    async def buscar(self, obj_id: UUID):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Trilha", str(obj_id))
        return obj

    async def listar(self, usuario, skip=0, limit=100, igreja_id=None, tipo=None, apenas_ativas=False):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        trilhas = await self.repo.listar(skip, limit, igreja_id, tipo, apenas_ativas)
        if trilhas:
            ids = [t.id for t in trilhas]
            totais = await self.repo.contar_progressos_por_trilha(ids)
            concluidos = await self.repo.contar_concluidos_por_trilha(ids)
            for t in trilhas:
                t.total_progressos = totais.get(t.id, 0)
                t.total_concluidos = concluidos.get(t.id, 0)
        return trilhas

    async def atualizar(self, obj_id: UUID, dados: dict, usuario: Usuario):
        obj = await self.buscar(obj_id)
        if usuario.role != "admin" and usuario.igreja_id and str(obj.igreja_id) != str(usuario.igreja_id):
            raise PermissionDeniedError("editar trilha de outra igreja")
        return await self.repo.atualizar(obj, dados)

    async def desativar(self, obj_id: UUID, usuario: Usuario):
        obj = await self.buscar(obj_id)
        if not obj.ativa:
            raise BusinessRuleError("Trilha ja esta desativada")
        return await self.repo.atualizar(obj, {"ativa": False})

    async def reativar(self, obj_id: UUID, usuario: Usuario):
        obj = await self.buscar(obj_id)
        if obj.ativa:
            raise BusinessRuleError("Trilha ja esta ativa")
        return await self.repo.atualizar(obj, {"ativa": True})

    async def deletar(self, obj_id: UUID, usuario: Usuario):
        obj = await self.buscar(obj_id)
        total = await self.repo.contar_progressos(obj_id)
        if total > 0:
            raise BusinessRuleError(
                f"Nao e possivel excluir: {total} pessoa(s) fazendo esta trilha. "
                "Desative a trilha em vez de exclui-la."
            )
        await self.repo.deletar(obj)


class ProgressoService:
    def __init__(self, db: AsyncSession):
        self.repo = ProgressoRepository(db)
        self.trilha_repo = TrilhaRepository(db)
        self.pessoa_repo = PessoaRepository(db)
        self.db = db

    def _calcular_campos(self, prog):
        """Calcula total_etapas, etapas_concluidas e progresso_percentual."""
        total = len(prog.etapas) if prog.etapas else 0
        concluidas = sum(1 for pe in (prog.etapas or []) if pe.concluida)
        prog.total_etapas = total
        prog.etapas_concluidas = concluidas
        prog.progresso_percentual = round((concluidas / total * 100) if total > 0 else 0, 1)
        return prog

    async def criar(self, dados: dict, autor: Usuario):
        pessoa_id = dados["pessoa_id"]
        trilha_id = dados["trilha_id"]

        pessoa = await self.pessoa_repo.buscar_por_id(pessoa_id)
        if not pessoa:
            raise BusinessRuleError("Pessoa informada nao existe")
        if not pessoa.ativo:
            raise BusinessRuleError("Pessoa inativa")

        trilha = await self.trilha_repo.buscar_por_id(trilha_id)
        if not trilha:
            raise BusinessRuleError("Trilha informada nao existe")
        if not trilha.ativa:
            raise BusinessRuleError("Trilha desativada. Nao aceita novos progressos.")

        if str(pessoa.igreja_id) != str(trilha.igreja_id):
            raise BusinessRuleError("Pessoa e trilha pertencem a igrejas diferentes")

        existente = await self.repo.buscar_por_pessoa_e_trilha(pessoa_id, trilha_id)
        if existente:
            raise BusinessRuleError("Esta pessoa ja esta fazendo esta trilha")

        # Cria progresso com etapas
        etapas_ids = [e.id for e in trilha.etapas]

        prog_dados = {
            "pessoa_id": pessoa_id,
            "trilha_id": trilha_id,
            "igreja_id": trilha.igreja_id,
            "responsavel_id": autor.id,
            "status": "em_andamento",
            "iniciado_em": dados.get("iniciado_em") or date.today(),
            "observacoes": dados.get("observacoes"),
        }
        prog = await self.repo.criar(prog_dados, etapas_ids)
        return await self.buscar(prog.id)

    async def buscar(self, obj_id: UUID):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Progresso", str(obj_id))
        return self._calcular_campos(obj)

    async def listar(self, usuario, skip=0, limit=100, igreja_id=None, pessoa_id=None, trilha_id=None, status=None):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        progressos = await self.repo.listar(skip, limit, igreja_id, pessoa_id, trilha_id, status)
        for p in progressos:
            self._calcular_campos(p)
        return progressos

    async def marcar_etapa(self, progresso_id: UUID, etapa_id: UUID, concluida: bool, observacao, usuario: Usuario):
        prog = await self.buscar(progresso_id)
        if prog.status != "em_andamento":
            raise BusinessRuleError("So e possivel marcar etapas de progressos em andamento")

        pe = await self.repo.buscar_etapa(progresso_id, etapa_id)
        if not pe:
            raise NotFoundError("Etapa do progresso", str(etapa_id))

        dados = {
            "concluida": concluida,
            "concluida_em": date.today() if concluida else None,
        }
        if observacao is not None:
            dados["observacao"] = observacao

        await self.repo.atualizar_etapa(pe, dados)

        # Verifica se pode auto-concluir
        await self._verificar_auto_conclusao(prog)

        return await self.buscar(progresso_id)

    async def _verificar_auto_conclusao(self, prog):
        """Se todas as etapas obrigatorias estao concluidas, conclui automaticamente."""
        # Refresh para pegar etapas atualizadas
        await self.db.refresh(prog)
        obrigatorias = [e for e in prog.trilha.etapas if e.obrigatoria]
        if not obrigatorias:
            return

        progresso_etapas = {pe.etapa_id: pe for pe in prog.etapas}
        todas_ok = all(
            progresso_etapas.get(e.id) and progresso_etapas[e.id].concluida
            for e in obrigatorias
        )
        if todas_ok:
            await self.repo.atualizar(prog, {
                "status": "concluida",
                "concluido_em": date.today(),
            })

    async def concluir(self, obj_id: UUID, usuario: Usuario):
        prog = await self.buscar(obj_id)
        if prog.status == "concluida":
            raise BusinessRuleError("Progresso ja esta concluido")
        await self.repo.atualizar(prog, {
            "status": "concluida",
            "concluido_em": date.today(),
        })
        return await self.buscar(obj_id)

    async def cancelar(self, obj_id: UUID, usuario: Usuario):
        prog = await self.buscar(obj_id)
        if prog.status == "cancelada":
            raise BusinessRuleError("Progresso ja esta cancelado")
        await self.repo.atualizar(prog, {"status": "cancelada"})
        return await self.buscar(obj_id)

    async def deletar(self, obj_id: UUID, usuario: Usuario):
        prog = await self.buscar(obj_id)
        await self.repo.deletar(prog)

    async def dashboard(self, usuario, igreja_id=None):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id

        return {
            "total_trilhas_ativas": len(await self.trilha_repo.listar(
                igreja_id=igreja_id, apenas_ativas=True, limit=10000,
            )),
            "total_em_andamento": await self.repo.contar_por_status("em_andamento", igreja_id),
            "total_concluidas": await self.repo.contar_por_status("concluida", igreja_id),
            "concluidas_ultimos_30_dias": await self.repo.contar_concluidas_periodo(30, igreja_id),
            "pessoas_paradas_30d": await self.repo.contar_paradas_30d(30, igreja_id),
            "trilhas_mais_populares": await self.repo.trilhas_populares(igreja_id),
        }

    async def listar_por_pessoa(self, pessoa_id: UUID):
        return await self.repo.listar(pessoa_id=pessoa_id, limit=1000)