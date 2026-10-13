"""Deploy Etapa 2 — Criar Dockerfile, docker-compose e .dockerignore."""
from pathlib import Path

BACKEND = Path(__file__).parent.resolve()
PROJETO = BACKEND.parent

print(f"Backend: {BACKEND}")
print()

# ============================================================
# 1. Dockerfile (na pasta backend)
# ============================================================
dockerfile = '''FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc libpq-dev curl \\
    && rm -rf /var/lib/apt/lists/*

# Instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o codigo
COPY . .

# Cria pasta de media e uploads
RUN mkdir -p /app/media/certificados /app/uploads

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
'''

(BACKEND / "Dockerfile").write_text(dockerfile, encoding="utf-8")
print("[OK] backend/Dockerfile criado")

# ============================================================
# 2. .dockerignore
# ============================================================
dockerignore = '''__pycache__
*.pyc
*.pyo
*.pyd
.Python
.venv/
venv/
env/
.env.local
.pytest_cache/
.mypy_cache/
*.bak.*
*.bak
*.log
.git/
.gitignore
media/
uploads/
node_modules/
*.md
'''

(BACKEND / ".dockerignore").write_text(dockerignore, encoding="utf-8")
print("[OK] backend/.dockerignore criado")

# ============================================================
# 3. docker-compose.yml (na raiz do projeto — pra dev)
# ============================================================
compose = '''version: "3.9"

services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: church_platform
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/church_platform
      SECRET_KEY: dev-secret-key-troque-em-producao
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 1440
      ENVIRONMENT: production
      DEBUG: "False"
    ports:
      - "8000:8000"

volumes:
  postgres_data:
'''

(PROJETO / "docker-compose.yml").write_text(compose, encoding="utf-8")
print("[OK] docker-compose.yml criado (raiz do projeto)")

# ============================================================
# 4. Confere requirements.txt
# ============================================================
req = BACKEND / "requirements.txt"
if req.exists():
    c = req.read_text(encoding="utf-8")
    faltando = []
    for lib in ["fastapi", "uvicorn", "sqlalchemy", "asyncpg", "alembic", "pydantic", "bcrypt", "pyjwt", "python-multipart", "aiofiles", "reportlab"]:
        if lib.lower() not in c.lower():
            faltando.append(lib)
    if faltando:
        print(f"[AVISO] Faltam em requirements.txt: {', '.join(faltando)}")
        print("        (verificar manualmente antes de fazer deploy)")
    else:
        print("[OK] requirements.txt tem todas as libs necessarias")

print()
print("=" * 60)
print("ETAPA 2 CONCLUIDA!")
print()
print("Arquivos criados:")
print("  backend/Dockerfile")
print("  backend/.dockerignore")
print("  docker-compose.yml")
print()
print("PROXIMO PASSO: ETAPA 3 (GitHub)")
print("=" * 60)