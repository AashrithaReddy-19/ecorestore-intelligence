"""Evidence retrieval: embeds a query, searches ChromaDB, and re-ranks by
ecosystem/metric relevance. Every result carries the source metadata, chunk
id, and a relevance score so recommendations can cite exactly what was
retrieved — nothing is invented downstream.
"""
from __future__ import annotations

from app.rag.embeddings import get_embedding_model
from app.rag.vector_store import get_vector_store


def _cosine_distance_to_score(distance: float) -> float:
    score = 1.0 - (distance / 2.0)
    return max(0.0, min(1.0, round(score, 4)))


def retrieve_evidence(
    query: str,
    ecosystem_type: str | None = None,
    metrics: list[str] | None = None,
    top_k: int = 5,
) -> list[dict]:
    """Return up to `top_k` evidence chunks relevant to `query`.

    Retrieves a wider candidate set from Chroma, then re-ranks with a small
    boost for ecosystem/metric metadata overlap so mangrove-specific
    evidence outranks generic cropland evidence for a mangrove assessment,
    without ever fabricating a source.
    """
    store = get_vector_store()
    if store.count() == 0:
        return []

    model = get_embedding_model()
    embedding = model.encode([query])[0]
    raw = store.query(embedding, n_results=min(top_k * 4, store.count()))

    ids = raw.get("ids", [[]])[0]
    documents = raw.get("documents", [[]])[0]
    metadatas = raw.get("metadatas", [[]])[0]
    distances = raw.get("distances", [[]])[0]

    candidates = []
    for chunk_id, doc, meta, dist in zip(ids, documents, metadatas, distances):
        base_score = _cosine_distance_to_score(dist)
        boost = 0.0
        ecosystem_tags = (meta.get("ecosystem_tags") or "").split("|")
        metrics_affected = (meta.get("metrics_affected") or "").split("|")
        if ecosystem_type and any(
            ecosystem_type.lower() in tag or tag in ecosystem_type.lower()
            for tag in ecosystem_tags
            if tag
        ):
            boost += 0.08
        if metrics and any(m in metrics_affected for m in metrics):
            boost += 0.05
        final_score = max(0.0, min(1.0, round(base_score + boost, 4)))
        candidates.append(
            {
                "chunk_id": chunk_id,
                "source_id": meta.get("source_id"),
                "title": meta.get("title"),
                "organization": meta.get("organization"),
                "year": meta.get("year"),
                "url": meta.get("url"),
                "evidence_text": doc,
                "relevance_score": final_score,
            }
        )

    candidates.sort(key=lambda c: c["relevance_score"], reverse=True)

    seen_sources: set[str] = set()
    deduped: list[dict] = []
    for c in candidates:
        if c["source_id"] in seen_sources:
            continue
        seen_sources.add(c["source_id"])
        deduped.append(c)
        if len(deduped) >= top_k:
            break
    return deduped
