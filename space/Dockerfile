# Stack complète Hugging Face Space (GPU NVIDIA T4 / CPU) :
#   - Front Angular compilé servi directement par FastAPI
#   - Moteur Stockfish embarqué
#   - Base vectorielle Milvus Lite intégrée (corpus 477 fiches pré-vectorisées)
#   - Modèle d'embedding Qwen3-Embedding-0.6B local
#   - Serveur LLM Ollama avec modèle Qwen pré-embarqué (accélération CUDA T4 automatique)

# ── Étage 1 : compiler le front Angular ──
FROM node:22-slim AS front
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ── Étage 2 : API + Stockfish + Ollama GPU + Milvus ──
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    stockfish \
    curl \
    ca-certificates \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Installation du binaire officiel Ollama avec support CUDA
RUN curl -fsSL https://ollama.com/install.sh | sh

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    STOCKFISH_PATH=/usr/games/stockfish \
    HF_HOME=/app/hf-cache \
    OLLAMA_MODELS=/app/ollama_models

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY backend/ .
RUN uv sync --frozen --no-dev \
    && uv pip install "sentence-transformers>=3.0" milvus-lite

# Préchargement du modèle d'embedding dans l'image
RUN uv run --no-sync python -c "from sentence_transformers import SentenceTransformer; \
SentenceTransformer('Qwen/Qwen3-Embedding-0.6B', device='cpu')"

# Pré-téléchargement du modèle LLM dans l'image
RUN mkdir -p /app/ollama_models \
    && (ollama serve & PID=$!; sleep 4; ollama pull qwen2.5:3b; kill $PID || true)

COPY space/corpus_export.json.gz /app/corpus_export.json.gz
COPY --from=front /app/dist/chess-board /app/static
COPY space/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh && chmod -R a+rwX /app

ENV MILVUS_LITE_PATH=/tmp/openings.db \
    EMBED_PROVIDER=local \
    SERVE_FRONT=1 \
    CORPUS_EXPORT=/app/corpus_export.json.gz \
    LLM_PROVIDER=ollama \
    LLM_MODEL=qwen2.5:3b \
    OLLAMA_BASE_URL=http://127.0.0.1:11434 \
    MONGO_URI=mongodb://127.0.0.1:1/ \
    CORS_ORIGINS=*

EXPOSE 7860
ENTRYPOINT ["/app/entrypoint.sh"]
