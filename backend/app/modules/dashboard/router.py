from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database.connection import get_db
from app.modules.cuidado.service import AcompanhamentoService
from app.modules.igreja.models import Igreja
from app.modules.oracao.service import PedidoService
from app.modules.pessoas.models import Pessoa
from app.modules.usuarios.models import Usuario
from app.modules.dashboard.schemas import (
    AtividadeRecente,
    DashboardGeral,
    ResumoCuidado,
    ResumoIgrejas,
    ResumoOracao,
    ResumoPessoas,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/geral", response_model=DashboardGeral)
async def dashboard_geral(
    igreja_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    # Se o usuario tem igreja vinculada e nao especificou, filtra por ela
    if usuario.igreja_id and not igreja_id:
        igreja_id = usuario.igreja_id

    # ============ IGREJAS ============
    stmt_ig = select(func.count(Igreja.id))
    r = await db.execute(stmt_ig)
    total_igrejas = r.scalar_one()

    stmt_ig_ativ = select(func.count(Igreja.id)).where(Igreja.ativa.is_(True))
    r = await db.execute(stmt_ig_ativ)
    igrejas_ativas = r.scalar_one()

    # ============ PESSOAS ============
    stmt_p = select(func.count(Pessoa.id))
    if igreja_id:
        stmt_p = stmt_p.where(Pessoa.igreja_id == igreja_id)
    r = await db.execute(stmt_p)
    total_pessoas = r.scalar_one()

    stmt_p_ativ = select(func.count(Pessoa.id)).where(Pessoa.ativo.is_(True))
    if igreja_id:
        stmt_p_ativ = stmt_p_ativ.where(Pessoa.igreja_id == igreja_id)
    r = await db.execute(stmt_p_ativ)
    pessoas_ativas = r.scalar_one()

    stmt_p_mem = select(func.count(Pessoa.id)).where(Pessoa.membro.is_(True), Pessoa.ativo.is_(True))
    if igreja_id:
        stmt_p_mem = stmt_p_mem.where(Pessoa.igreja_id == igreja_id)
    r = await db.execute(stmt_p_mem)
    pessoas_membros = r.scalar_one()

    pessoas_visitantes = pessoas_ativas - pessoas_membros

    # ============ CUIDADO ============
    svc_cuidado = AcompanhamentoService(db)
    dash_cuidado = await svc_cuidado.dashboard(usuario, igreja_id)

    # ============ ORACAO ============
    svc_oracao = PedidoService(db)
    dash_oracao = await svc_oracao.dashboard(usuario, igreja_id)

    # ============ ATIVIDADES RECENTES ============
    atividades = []

    # Ultimos 5 acompanhamentos visiveis
    from app.modules.cuidado.models import Acompanhamento
    stmt_ac = (
        select(Acompanhamento)
        .where(Acompanhamento.ativo.is_(True))
        .order_by(Acompanhamento.created_at.desc())
        .limit(5)
    )
    if igreja_id:
        stmt_ac = stmt_ac.where(Acompanhamento.igreja_id == igreja_id)
    if usuario.role != "admin":
        stmt_ac = stmt_ac.where(
            (Acompanhamento.sigiloso.is_(False)) |
            (Acompanhamento.responsavel_id == usuario.id)
        )
    r = await db.execute(stmt_ac)
    for a in r.scalars().all():
        atividades.append(AtividadeRecente(
            id=a.id, tipo="acompanhamento", titulo=a.titulo,
            subtitulo=a.pessoa.nome if a.pessoa else None,
            data=a.data, status=a.status, sigiloso=a.sigiloso,
        ))

    # Ultimos 5 pedidos visiveis
    from app.modules.oracao.models import PedidoOracao
    stmt_or = (
        select(PedidoOracao)
        .where(PedidoOracao.ativo.is_(True))
        .order_by(PedidoOracao.created_at.desc())
        .limit(5)
    )
    if igreja_id:
        stmt_or = stmt_or.where(PedidoOracao.igreja_id == igreja_id)
    if usuario.role != "admin":
        stmt_or = stmt_or.where(
            (PedidoOracao.sigiloso.is_(False)) |
            (PedidoOracao.responsavel_id == usuario.id)
        )
    r = await db.execute(stmt_or)
    for o in r.scalars().all():
        atividades.append(AtividadeRecente(
            id=o.id, tipo="oracao", titulo=o.titulo,
            subtitulo=o.pessoa.nome if o.pessoa else None,
            data=o.data_pedido, status=o.status, sigiloso=o.sigiloso,
        ))

    atividades.sort(key=lambda x: x.data, reverse=True)
    atividades = atividades[:8]

    return DashboardGeral(
        igrejas=ResumoIgrejas(total=total_igrejas, ativas=igrejas_ativas),
        pessoas=ResumoPessoas(
            total=total_pessoas,
            ativas=pessoas_ativas,
            membros=pessoas_membros,
            visitantes=pessoas_visitantes,
            sem_interacao_30d=len(dash_cuidado["pessoas_sem_interacao"]),
        ),
        cuidado=ResumoCuidado(
            total=dash_cuidado["acompanhamentos_pendentes"] + len(dash_cuidado["acompanhamentos_vencidos"]) + 0,
            pendentes=dash_cuidado["acompanhamentos_pendentes"],
            vencidos=len(dash_cuidado["acompanhamentos_vencidos"]),
            concluidos=0,
            retornos_7d=len(dash_cuidado["retornos_proximos_7_dias"]),
        ),
        oracao=ResumoOracao(
            total=dash_oracao["total"],
            abertos=dash_oracao["abertos"],
            em_oracao=dash_oracao["em_oracao"],
            atendidos=dash_oracao["atendidos"],
            sem_resposta_30d=len(dash_oracao["sem_resposta_30d"]),
        ),
        atividades_recentes=atividades,
    )
