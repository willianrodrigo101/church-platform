"""Deploy Etapa 1 — Backend serve o frontend na mesma porta."""
import re
import shutil
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).parent.resolve()
PROJETO = BACKEND.parent
FRONTEND_INDEX = PROJETO / "frontend" / "web" / "index.html"
STATIC_DIR = BACKEND / "app" / "static"
DEST_INDEX = STATIC_DIR / "index.html"
MAIN_PY = BACKEND / "app" / "main.py"

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

print(f"Backend:  {BACKEND}")
print(f"Frontend: {FRONTEND_INDEX}")
print()

# ============================================================
# 1. Criar pasta static/ e copiar index.html
# ============================================================
STATIC_DIR.mkdir(parents=True, exist_ok=True)
conteudo = FRONTEND_INDEX.read_text(encoding="utf-8")

# Ajusta a constante API: dinamica
padroes = [
    r'const API = ["\']http://127\.0\.0\.1:8000/api/v1["\'];',
    r'const API = ["\']http://localhost:8000/api/v1["\'];',
    r'const API = `http://127\.0\.0\.1:8000/api/v1`;',
]
novo = 'const API = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") ? "http://127.0.0.1:8000/api/v1" : window.location.origin + "/api/v1";'

ajustou = False
for p in padroes:
    if re.search(p, conteudo):
        conteudo = re.sub(p, novo, conteudo, count=1)
        ajustou = True
        print("[OK] API base ajustada no index.html (dinamica)")
        break

if not ajustou:
    # Tenta pela linha "const API ="
    m = re.search(r'const API = [^;]+;', conteudo)
    if m:
        conteudo = conteudo.replace(m.group(0), novo, 1)
        print(f"[OK] API base ajustada: {m.group(0)[:60]}...")

DEST_INDEX.write_text(conteudo, encoding="utf-8")
print(f"[OK] Copiado para {DEST_INDEX.relative_to(BACKEND)}")
print()

# ============================================================
# 2. Ajustar main.py
# ============================================================
c = MAIN_PY.read_text(encoding="utf-8")

# 2.1 — Backup
backup = MAIN_PY.with_suffix(f".py.bak.{STAMP}")
shutil.copy2(MAIN_PY, backup)
print(f"[BACKUP] {backup.name}")

# 2.2 — Import FileResponse e StaticFiles
if "FileResponse" not in c:
    c = c.replace(
        "from fastapi.responses import JSONResponse",
        "from fastapi.responses import FileResponse, JSONResponse",
        1,
    )
    print("[OK] Import FileResponse adicionado")

if "from fastapi.staticfiles import StaticFiles" not in c:
    c = c.replace(
        "from fastapi import FastAPI, Request, status",
        "from fastapi import FastAPI, Request, status\nfrom fastapi.staticfiles import StaticFiles",
        1,
    )
    print("[OK] Import StaticFiles adicionado")

# 2.3 — Adiciona rota "/" que serve o index.html
if 'async def serve_frontend' not in c:
    marcador = 'app.include_router(api_router, prefix=settings.API_V1_PREFIX)'
    if marcador in c:
        bloco = marcador + '''


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
'''
        c = c.replace(marcador, bloco, 1)
        print("[OK] Rota / adicionada no main.py")

MAIN_PY.write_text(c, encoding="utf-8")
print(f"[OK] {MAIN_PY.name} salvo")

print()
print("=" * 60)
print("PRONTO! Teste local:")
print("  1. uvicorn app.main:app --reload")
print("  2. Abra http://127.0.0.1:8000/  (deve abrir o frontend!)")
print("=" * 60)