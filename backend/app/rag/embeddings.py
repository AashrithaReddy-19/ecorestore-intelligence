"""Embedding model wrapper.

Uses Sentence Transformers `all-MiniLM-L6-v2` as required. If the model
cannot be loaded (e.g. no network access in an offline CI sandbox), a
deterministic hashed bag-of-words fallback is used instead so ingestion and
retrieval remain testable without downloading weights. The fallback is never
used to fabricate evidence text — it only affects which chunks rank highest.
"""
from __future__ import annotations

import hashlib
from functools import lru_cache

from app.config import get_settings

_FALLBACK_DIM = 384


class EmbeddingModel:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._model = None
        self._use_fallback = False

    def _ensure_loaded(self) -> None:
        if self._model is not None or self._use_fallback:
            return
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.settings.embedding_model_name)
        except Exception:
            self._use_fallback = True

    def encode(self, texts: list[str]) -> list[list[float]]:
        self._ensure_loaded()
        if self._use_fallback:
            return [self._hash_embed(t) for t in texts]
        vectors = self._model.encode(list(texts), normalize_embeddings=True)
        return [v.tolist() for v in vectors]

    @property
    def is_fallback(self) -> bool:
        self._ensure_loaded()
        return self._use_fallback

    @staticmethod
    def _hash_embed(text: str) -> list[float]:
        vec = [0.0] * _FALLBACK_DIM
        for token in text.lower().split():
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            vec[int(digest, 16) % _FALLBACK_DIM] += 1.0
        norm = sum(v * v for v in vec) ** 0.5 or 1.0
        return [v / norm for v in vec]


@lru_cache
def get_embedding_model() -> EmbeddingModel:
    return EmbeddingModel()
