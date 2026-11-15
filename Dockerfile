FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia a pasta backend inteira
COPY backend/ /app/

# Instala dependencias
RUN pip install --no-cache-dir -r /app/requirements.txt

# Cria pasta de media e uploads
RUN mkdir -p /app/media/certificados /app/uploads

EXPOSE 8000

# Roda migrations e sobe o uvicorn
CMD sh -c "until pg_isready -h $POSTGRES_HOST -p 5432 -U $POSTGRES_USER; do echo 'Aguardando banco de dados...'; sleep 2; done; rm -f /app/.env && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"

