# Backend image for Railway: FastAPI + ChromaDB + BGE embeddings (CPU)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface \
    TOKENIZERS_PARALLELISM=false \
    ANONYMIZED_TELEMETRY=False

WORKDIR /app

# CPU-only torch keeps the image ~1.5GB smaller than the default CUDA build
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch

COPY requirements-api.txt .
RUN pip install -r requirements-api.txt

# Bake the embedding model into the image so cold starts don't download it
ARG EMBEDDING_MODEL_NAME=BAAI/bge-small-en-v1.5
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${EMBEDDING_MODEL_NAME}')"

COPY config/ config/
COPY src/ src/
COPY chroma_db/ chroma_db/

EXPOSE 8000
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
