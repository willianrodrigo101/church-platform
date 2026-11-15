FROM python:3.12-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia o requirements e instala as dependências Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY backend/ .

# Cria pastas de mídia
RUN mkdir -p /app/media/certificados /app/uploads

# Comando de inicialização (espera o banco, roda migrações e sobe o uvicorn)
CMD sh -c "sleep 15 && python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
