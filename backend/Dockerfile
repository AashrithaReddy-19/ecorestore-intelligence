FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CHROMA_PERSIST_DIRECTORY=/app/knowledge_base/chroma_store

# No apt-get/build-essential needed: every dependency below (including
# psycopg[binary], chromadb, and sentence-transformers/torch) ships
# prebuilt manylinux wheels for this base image, so nothing compiles here.
#
# torch is pulled in transitively by sentence-transformers. On Linux, PyPI's
# default torch build depends on several GB of separate NVIDIA CUDA packages
# we never use (inference here is CPU-only). Installing the CPU-only build
# from PyTorch's own wheel index first satisfies that dependency before
# requirements.txt is processed, so pip never reaches for the CUDA variant.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY knowledge_base ./knowledge_base
COPY scripts ./scripts

WORKDIR /app/backend

EXPOSE 8000

# Auto-ingests the knowledge base into Chroma/DB on first startup if empty
# (see app/main.py on_startup), so this image is deploy-ready as-is.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
