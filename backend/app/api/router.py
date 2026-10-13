from fastapi import APIRouter

from app.modules.anexos.router import router as anexos_router
from app.modules.cuidado.router import router as cuidado_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.estudo.router import router as estudo_router
from app.modules.estudo.router_publico import router as estudo_publico_router
from app.modules.eventos.router import router as eventos_router
from app.modules.igreja.router import router as igreja_router
from app.modules.jornada.router import router as jornada_router
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
api_router.include_router(eventos_router)
api_router.include_router(jornada_router)
api_router.include_router(anexos_router)
api_router.include_router(estudo_router)
api_router.include_router(estudo_publico_router)
