from app.ingestion import load_seed_sources
from app.reasoning.engine import NO_NUMERIC_ESTIMATE_SENTENCE, run_assessment

SUNDARBANS_SAMPLE = {
    "location_name": "Sundarbans-adjacent coastal area",
    "latitude": 21.95,
    "longitude": 88.75,
    "ecosystem_type": "mangrove",
    "land_use": "degraded mangrove edge",
    "soil_organic_carbon_percent": 0.4,
    "soil_ph": 7.8,
    "soil_moisture_percent": 18,
    "soil_salinity": "high",
    "rainfall_pattern": "irregular",
    "temperature_trend": "rising",
    "habitat_fragmentation": "high",
    "human_impact": ["aquaculture expansion", "plastic pollution"],
    "species_observations": "low bird and pollinator activity",
}


def _known_source_ids() -> set[str]:
    return {s["source_id"] for s in load_seed_sources()}


def test_every_cited_source_exists_in_knowledge_base():
    result = run_assessment(SUNDARBANS_SAMPLE)
    known = _known_source_ids()
    for rec in result["recommendations"]:
        for evidence in rec["evidence"]:
            assert evidence["source_id"] in known, f"Fabricated/unknown source cited: {evidence['source_id']}"
            assert evidence["url"].startswith("http")


def test_no_recommendation_invents_a_numeric_improvement_claim():
    result = run_assessment(SUNDARBANS_SAMPLE)
    for rec in result["recommendations"]:
        assert NO_NUMERIC_ESTIMATE_SENTENCE in rec["limitations"]


def test_recommendation_without_evidence_says_so_explicitly():
    # A sparse, unusual combination unlikely to have direct evidence coverage.
    sparse_data = {"ecosystem_type": "grassland", "habitat_fragmentation": "high",
                    "species_observations": "low", "human_impact": ["mining"]}
    result = run_assessment(sparse_data)
    for rec in result["recommendations"]:
        if not rec["evidence"]:
            assert any("No directly matching evidence" in lim for lim in rec["limitations"])
