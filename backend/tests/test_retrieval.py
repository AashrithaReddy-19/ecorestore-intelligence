from app.rag.retrieval import retrieve_evidence


def test_retrieval_returns_scored_results_with_source_metadata():
    results = retrieve_evidence(query="mangrove restoration aquaculture salinity", ecosystem_type="mangrove", top_k=3)
    assert len(results) > 0
    for r in results:
        assert r["source_id"]
        assert r["organization"]
        assert r["url"].startswith("http")
        assert 0.0 <= r["relevance_score"] <= 1.0


def test_retrieval_is_topically_relevant():
    results = retrieve_evidence(query="soil organic carbon cover crops monoculture", top_k=5)
    source_ids = {r["source_id"] for r in results}
    assert "FAO_SOC_001" in source_ids or "IPCC_SOILCARBON_CLIMATE_001" in source_ids


def test_retrieval_deduplicates_by_source():
    results = retrieve_evidence(query="habitat fragmentation corridor connectivity", top_k=5)
    source_ids = [r["source_id"] for r in results]
    assert len(source_ids) == len(set(source_ids))
