from app.reasoning.engine import run_assessment

FULL_DATA = {
    "location_name": "Sundarbans-adjacent coastal area",
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

SPARSE_DATA = {"ecosystem_type": "mangrove"}


def test_confidence_is_within_bounds():
    result = run_assessment(FULL_DATA)
    assert 0.0 <= result["confidence"] <= 1.0


def test_confidence_decreases_with_missing_critical_fields():
    full_result = run_assessment(FULL_DATA)
    sparse_result = run_assessment(SPARSE_DATA)
    assert sparse_result["confidence"] < full_result["confidence"]
    assert len(sparse_result["missing_critical_fields"]) > len(full_result["missing_critical_fields"])


def test_confidence_explanation_is_present_and_references_fields():
    result = run_assessment(SPARSE_DATA)
    assert result["confidence_explanation"]
    assert "rule" in result["confidence_explanation"].lower() or "field" in result["confidence_explanation"].lower()


def test_risk_level_is_valid_enum_value():
    result = run_assessment(FULL_DATA)
    assert result["biodiversity_risk_level"] in {"low", "medium", "high", "critical"}
