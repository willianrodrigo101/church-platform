"""Setup do modulo de Notificacoes (endpoint agregador)."""
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


schemas_py = '''from datetime import date
from uuid import UUID

from pydantic import BaseModel


class NotificacaoItem(BaseModel):
    id: UUID
    tipo: str          # "acompanhamento_vencido" | "retorno_proximo" | "pedido_sem_resposta" | "pessoa_sem_interacao"
    titulo: str
    subtitulo: str | None = None
    data: date | None = None
    dias: int = 0      # dias vencido / dias sem interacao / dias aberto
    sigiloso: bool = False
    aba_destino: str   # "cuidado" | "oracao" | "pessoas"


class NotificacoesResumo(BaseModel):
    total: int
    por_tipo: dict[str, int]
    itens: list[NotificacaoItem]
'''

router_py = '''from datetime import date
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
'''

init_py = '''from app.modules.notificacoes.schemas import NotificacoesResumo

__all__ = ["NotificacoesResumo"]
'''

api_router_py = '''from fastapi import APIRouter

from app.modules.cuidado.router import router as cuidado_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.igreja.router import router as igreja_router
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
'''


print(f"Backend: {BACKEND}")
print()

print("Criando modulo notificacoes...")
escrever(BACKEND / "app" / "modules" / "notificacoes" / "schemas.py", schemas_py)
escrever(BACKEND / "app" / "modules" / "notificacoes" / "router.py", router_py)
escrever(BACKEND / "app" / "modules" / "notificacoes" / "__init__.py", init_py)

print()
print("Atualizando API router...")
escrever(BACKEND / "app" / "api" / "router.py", api_router_py)

print()
print("=" * 60)
print("PRONTO! Suba o uvicorn e teste:")
print("  GET /api/v1/notificacoes/")
print("=" * 60)