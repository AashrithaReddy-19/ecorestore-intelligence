#!/usr/bin/env python
"""CLI entrypoint: chunk, embed, and store knowledge_base/seed_sources records
into ChromaDB, and mirror the structured fields into the relational database.

Usage (from backend/ with its virtualenv active):
    python ../scripts/ingest_knowledge.py
"""
from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.ingestion import run_full_ingestion  # noqa: E402


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        stats = run_full_ingestion(db)
        print("Knowledge base ingestion complete:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
