from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.rag.vector_store import get_vector_store

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    settings = get_settings()
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    vector_count = 0
    vector_ok = True
    try:
        vector_count = get_vector_store().count()
    except Exception:
        vector_ok = False

    return {
        "status": "ok" if db_ok and vector_ok else "degraded",
        "database_ok": db_ok,
        "vector_store_ok": vector_ok,
        "evidence_chunks_indexed": vector_count,
        "llm_provider": settings.llm_provider,
        "llm_enabled": settings.llm_provider == "openai" and bool(settings.openai_api_key),
        "environment": settings.environment,
    }
