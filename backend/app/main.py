"""FastAPI application entrypoint."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import EvidenceSource  # noqa: F401 ensures models are registered
from app.routers import assessments, chat, evidence, health, mrv

logger = logging.getLogger("ecorestore")
settings = get_settings()

app = FastAPI(
    title="EcoRestore Intelligence API",
    description=(
        "Evidence-grounded AI for biodiversity recovery and environmental MRV. "
        "Combines deterministic multi-metric reasoning with RAG-backed evidence retrieval."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(assessments.router)
app.include_router(chat.router)
app.include_router(mrv.router)
app.include_router(evidence.router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        already_seeded = db.query(EvidenceSource).count() > 0
        if not already_seeded:
            from app.ingestion import run_full_ingestion

            try:
                stats = run_full_ingestion(db)
                logger.info("Knowledge base auto-ingested on startup: %s", stats)
            except Exception:
                logger.exception("Knowledge base auto-ingestion failed; run scripts/ingest_knowledge.py manually.")
        else:
            from app.ingestion import seed_intervention_catalogue

            seed_intervention_catalogue(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "name": "EcoRestore Intelligence API",
        "docs": "/docs",
        "health": "/api/health",
    }
