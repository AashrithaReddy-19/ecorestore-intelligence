"""ChromaDB persistent vector store wrapper for evidence chunks."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import chromadb

from app.config import get_settings

COLLECTION_NAME = "evidence_chunks"


class VectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        Path(settings.chroma_persist_directory).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )

    def upsert(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict],
        embeddings: list[list[float]],
    ) -> None:
        self.collection.upsert(
            ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings
        )

    def query(self, query_embedding: list[float], n_results: int = 12) -> dict:
        n_results = max(1, min(n_results, max(self.collection.count(), 1)))
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

    def count(self) -> int:
        return self.collection.count()

    def reset(self) -> None:
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )


@lru_cache
def get_vector_store() -> VectorStore:
    return VectorStore()
