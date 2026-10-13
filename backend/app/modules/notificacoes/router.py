from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database.connection import get_db
from app.modules.cuidado.service import AcompanhamentoService
from app.modules.notificacoes.schemas import (
    NotificacaoItem,
    NotificacoesResumo,
)
from app.modules.oracao.service import PedidoService
from app.modules.usuarios.models import Usuario


router = APIRouter(prefix="/notificacoes", tags=["Notificacoes"])


@router.get("/", response_model=NotificacoesResumo)
async def listar_notificacoes(
    igreja_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    # Se o usuario tem igreja, filtra por ela
    if usuario.igreja_id and not igreja_id:
        igreja_id = usuario.igreja_id

    itens: list[NotificacaoItem] = []

    # ============ CUIDADO PASTORAL ============
    svc_cuidado = AcompanhamentoService(db)
    dash_cuidado = await svc_cuidado.dashboard(usuario, igreja_id)

    # Acompanhamentos vencidos
    for v in dash_cuidado["acompanhamentos_vencidos"]:
        itens.append(NotificacaoItem(
            id=v["id"],
            tipo="acompanhamento_vencido",
            titulo=v["titulo"],
            subtitulo=f'{v["pessoa_nome"]} · {v["responsavel_nome"]}',
            data=v["data_retorno"],
            dias=v["dias_atraso"],
            aba_destino="cuidado",
        ))

    # Retornos proximos (7 dias)
    for v in dash_cuidado["retornos_proximos_7_dias"]:
        itens.append(NotificacaoItem(
            id=v["id"],
            tipo="retorno_proximo",
            titulo=v["titulo"],
            subtitulo=f'{v["pessoa_nome"]} · {v["responsavel_nome"]}',
            data=v["data_retorno"],
            dias=0,
            aba_destino="cuidado",
        ))

    # Pessoas sem interacao
    for p in dash_cuidado["pessoas_sem_interacao"]:
        itens.append(NotificacaoItem(
            id=p["id"],
            tipo="pessoa_sem_interacao",
            titulo=p["nome"],
            subtitulo=p.get("telefone") or p.get("email"),
            data=None,
            dias=p["dias_sem_interacao"] or 0,
            aba_destino="pessoas",
        ))

    # ============ ORACAO ============
    svc_oracao = PedidoService(db)
    dash_oracao = await svc_oracao.dashboard(usuario, igreja_id)

    for p in dash_oracao["sem_resposta_30d"]:
        itens.append(NotificacaoItem(
            id=p["id"],
            tipo="pedido_sem_resposta",
            titulo=p["titulo"],
            subtitulo=p["pessoa_nome"] or p["responsavel_nome"],
            data=p["data_pedido"],
            dias=p["dias_aberto"],
            aba_destino="oracao",
        ))

    # Ordena por "dias" decrescente (mais urgentes primeiro)
    itens.sort(key=lambda x: x.dias, reverse=True)

    # Contagem por tipo
    por_tipo: dict[str, int] = {}
    for item in itens:
        por_tipo[item.tipo] = por_tipo.get(item.tipo, 0) + 1

    return NotificacoesResumo(
        total=len(itens),
        por_tipo=por_tipo,
        itens=itens[:50],  # limite de 50
    )
