"""Knowledge ingestion: reads knowledge_base/seed_sources/*.json, chunks the
evidence text, embeds each chunk, and stores it in both the relational
database (for structured queries/joins) and ChromaDB (for semantic
retrieval). Shared by scripts/ingest_knowledge.py (CLI) and the FastAPI
startup event (auto-bootstrap on first run).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import EvidenceChunk, EvidenceSource, InterventionCatalogue
from app.rag.embeddings import get_embedding_model
from app.rag.vector_store import get_vector_store
from app.reasoning.intervention_catalogue import INTERVENTION_CATALOGUE

REQUIRED_FIELDS = [
    "source_id", "organization", "title", "year", "url", "topic_tags",
    "ecosystem_tags", "claim", "conditions", "metrics_affected", "evidence_text",
]


def load_seed_sources(seed_dir: str | None = None) -> list[dict]:
    directory = Path(seed_dir or get_settings().seed_sources_dir)
    sources = []
    for path in sorted(directory.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            record = json.load(f)
        missing = [field for field in REQUIRED_FIELDS if field not in record]
        if missing:
            raise ValueError(f"{path.name} is missing required fields: {missing}")
        sources.append(record)
    return sources


def chunk_text(text: str, max_chars: int = 350) -> list[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 > max_chars and current:
            chunks.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        chunks.append(current.strip())
    return chunks


def ingest_to_db(db: Session, sources: list[dict]) -> tuple[int, int]:
    source_count = 0
    chunk_count = 0
    for record in sources:
        existing = db.get(EvidenceSource, record["source_id"]) or (
            db.query(EvidenceSource).filter_by(source_id=record["source_id"]).one_or_none()
        )
        if existing is None:
            existing = EvidenceSource(source_id=record["source_id"])
            db.add(existing)
        existing.organization = record["organization"]
        existing.title = record["title"]
        existing.year = record["year"]
        existing.url = record["url"]
        existing.topic_tags = record["topic_tags"]
        existing.ecosystem_tags = record["ecosystem_tags"]
        existing.claim = record["claim"]
        existing.conditions = record["conditions"]
        existing.metrics_affected = record["metrics_affected"]
        source_count += 1

        db.query(EvidenceChunk).filter_by(source_id=record["source_id"]).delete()
        chunks = chunk_text(record["evidence_text"])
        for i, chunk in enumerate(chunks):
            db.add(
                EvidenceChunk(
                    chunk_id=f"{record['source_id']}_chunk{i}",
                    source_id=record["source_id"],
                    evidence_text=chunk,
                    chunk_index=i,
                )
            )
            chunk_count += 1
    db.commit()
    return source_count, chunk_count


def ingest_to_vector_store(sources: list[dict]) -> int:
    store = get_vector_store()
    model = get_embedding_model()

    ids, documents, metadatas = [], [], []
    for record in sources:
        chunks = chunk_text(record["evidence_text"])
        for i, chunk in enumerate(chunks):
            ids.append(f"{record['source_id']}_chunk{i}")
            documents.append(chunk)
            metadatas.append(
                {
                    "source_id": record["source_id"],
                    "organization": record["organization"],
                    "title": record["title"],
                    "year": record["year"] or 0,
                    "url": record["url"],
                    "claim": record["claim"],
                    "topic_tags": "|".join(record["topic_tags"]),
                    "ecosystem_tags": "|".join(record["ecosystem_tags"]),
                    "metrics_affected": "|".join(record["metrics_affected"]),
                }
            )
    if not ids:
        return 0
    embeddings = model.encode(documents)
    store.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    return len(ids)


def seed_intervention_catalogue(db: Session) -> int:
    count = 0
    for key, item in INTERVENTION_CATALOGUE.items():
        existing = db.query(InterventionCatalogue).filter_by(intervention_key=key).one_or_none()
        if existing is None:
            existing = InterventionCatalogue(intervention_key=key)
            db.add(existing)
        existing.name = item.name
        existing.description = item.description
        existing.default_time_horizon = item.default_time_horizon
        existing.typical_metrics = item.typical_metrics
        existing.typical_ecosystems = item.typical_ecosystems
        count += 1
    db.commit()
    return count


def run_full_ingestion(db: Session, seed_dir: str | None = None) -> dict:
    sources = load_seed_sources(seed_dir)
    source_count, chunk_count = ingest_to_db(db, sources)
    vector_count = ingest_to_vector_store(sources)
    catalogue_count = seed_intervention_catalogue(db)
    return {
        "sources": source_count,
        "chunks": chunk_count,
        "vectors": vector_count,
        "interventions": catalogue_count,
    }
