from __future__ import annotations

from fastapi import APIRouter, Query

from app.rag.retrieval import retrieve_evidence
from app.schemas import EvidenceSearchResult

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@router.get("/search", response_model=list[EvidenceSearchResult])
def search_evidence(
    q: str = Query(..., min_length=2, description="Free-text search query"),
    ecosystem_type: str | None = None,
    top_k: int = Query(default=5, ge=1, le=20),
):
    results = retrieve_evidence(query=q, ecosystem_type=ecosystem_type, top_k=top_k)
    return [
        EvidenceSearchResult(
            chunk_id=r["chunk_id"], source_id=r["source_id"], title=r["title"],
            organization=r["organization"], year=r["year"], url=r["url"],
            evidence_text=r["evidence_text"], relevance_score=r["relevance_score"],
        )
        for r in results
    ]
