FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CHROMA_PERSIST_DIRECTORY=/app/knowledge_base/chroma_store

# No apt-get/build-essential needed: every dependency below (including
# psycopg[binary], chromadb, and sentence-transformers/torch) ships
# prebuilt manylinux wheels for this base image, so nothing compiles here.
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
