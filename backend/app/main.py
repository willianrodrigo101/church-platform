import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.api.router import api_router
from app.core.config.settings import settings
from app.core.database.connection import engine
from app.core.exceptions.handlers import (
    BusinessRuleError,
    ChurchPlatformException,
    NotFoundError,
    PermissionDeniedError,
)
from app.core.logging.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    await engine.dispose()
    logger.info("Encerrando aplicacao")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# EXCEPTION HANDLERS
# Transformam excecoes de dominio em respostas HTTP amigaveis
# ============================================================
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message, "code": exc.code},
    )


@app.exception_handler(BusinessRuleError)
async def business_rule_handler(request: Request, exc: BusinessRuleError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message, "code": exc.code},
    )


@app.exception_handler(PermissionDeniedError)
async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.message, "code": exc.code},
    )


@app.exception_handler(ChurchPlatformException)
async def church_platform_handler(request: Request, exc: ChurchPlatformException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message, "code": exc.code},
    )


app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# ============================================================
# STATIC FILES — frontend embutido
# ============================================================
from pathlib import Path as _Path
_static_dir = _Path(__file__).parent / "static"
_static_dir.mkdir(exist_ok=True)

_media_dir = _Path(__file__).parent.parent / "media"
_media_dir.mkdir(exist_ok=True)
app.mount("/media", StaticFiles(directory=str(_media_dir)), name="media")


@app.get("/", include_in_schema=False)
async def serve_frontend():
    index_file = _static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"app": settings.APP_NAME, "status": "online", "frontend": "ausente"}



# ============================================================
# STATIC FILES — certificados PDF
# ============================================================
from pathlib import Path as _Path
_media_dir = _Path(__file__).parent.parent / 'media'
_media_dir.mkdir(exist_ok=True)
app.mount('/media', StaticFiles(directory=str(_media_dir)), name='media')


@app.get("/", tags=["Health"])
async def root():
    return {"app": settings.APP_NAME, "status": "online"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}