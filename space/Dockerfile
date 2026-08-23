# Vitrine Hugging Face Space — le POC en UN conteneur (variante dégradée assumée) :
#   front Angular servi par FastAPI · Milvus Lite embarqué (corpus pré-vectorisé) ·
#   embeddings sentence-transformers CPU (même modèle Qwen3-Embedding-0.6B) ·
#   synthèse en gabarit déterministe (pas de LLM) · Stockfish Debian · sans MongoDB.
# La version complète (7 conteneurs + LLM local) reste le docker compose du dépôt.

# ── Étage 1 : compiler le front Angular ──
FROM node:22-slim AS front
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ── Étage 2 : l'API + le corpus + le modèle d'embedding ──
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends stockfish \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    STOCKFISH_PATH=/usr/games/stockfish \
    HF_HOME=/app/hf-cache

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev \
    && uv pip install "sentence-transformers>=3.0" milvus-lite

# Le modèle d'embedding entre dans l'image : pas de téléchargement au démarrage
RUN uv run --no-sync python -c "from sentence_transformers import SentenceTransformer; \
SentenceTransformer('Qwen/Qwen3-Embedding-0.6B', device='cpu')"

COPY backend/ .
RUN uv sync --frozen --no-dev
COPY space/corpus_export.json.gz /app/corpus_export.json.gz
COPY --from=front /app/dist/chess-board /app/static

# Les Spaces exécutent le conteneur sous un utilisateur arbitraire
RUN chmod -R a+rwX /app

ENV MILVUS_URI=/tmp/openings.db \
    EMBED_PROVIDER=local \
    SERVE_FRONT=1 \
    CORPUS_EXPORT=/app/corpus_export.json.gz \
    LLM_PROVIDER=none \
    MONGO_URI=mongodb://127.0.0.1:1/ \
    CORS_ORIGINS=*

EXPOSE 7860
CMD ["uv", "run", "--no-sync", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
