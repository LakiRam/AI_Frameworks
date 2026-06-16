FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (sqlite is bundled; keep image small)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Default config; can be overridden via env / docker-compose
ENV API_HOST=0.0.0.0 \
    API_PORT=8080 \
    OLLAMA_BASE_URL=http://ollama:11434 \
    OLLAMA_MODEL=llama3.1:8b \
    CHECKPOINT_DB=/data/checkpoints.sqlite

VOLUME ["/data"]
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:8080/healthz || exit 1

CMD ["uvicorn", "soa_retail_agent.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
