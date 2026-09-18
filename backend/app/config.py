"""Application configuration.

Reads settings from environment variables with sane local-dev defaults so the
project runs without any secrets configured (SQLite + deterministic LLM
fallback).
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings:
    def __init__(self) -> None:
        self.database_url: str = os.getenv(
            "DATABASE_URL", f"sqlite:///{(BACKEND_DIR / 'ecorestore.db').as_posix()}"
        )
        self.llm_provider: str = os.getenv("LLM_PROVIDER", "none").lower()
        self.openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.cors_origins: list[str] = [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
            if origin.strip()
        ]
        self.chroma_persist_directory: str = os.getenv(
            "CHROMA_PERSIST_DIRECTORY",
            str(PROJECT_ROOT / "knowledge_base" / "chroma_store"),
        )
        self.seed_sources_dir: str = os.getenv(
            "SEED_SOURCES_DIR", str(PROJECT_ROOT / "knowledge_base" / "seed_sources")
        )
        self.embedding_model_name: str = os.getenv(
            "EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2"
        )
        self.environment: str = os.getenv("ENVIRONMENT", "development")


@lru_cache
def get_settings() -> Settings:
    return Settings()
