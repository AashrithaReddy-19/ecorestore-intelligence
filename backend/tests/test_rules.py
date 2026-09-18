from app.reasoning.rules import evaluate_rules


def test_rule1_soil_carbon_monoculture_rainfall():
    data = {
        "soil_organic_carbon_percent": 0.8,
        "land_use": "monoculture cropland",
        "rainfall_pattern": "irregular",
    }
    results = evaluate_rules(data)
    ids = [r.rule_id for r in results]
    assert "R1_soil_carbon_monoculture_rainfall" in ids
    rule = next(r for r in results if r.rule_id == "R1_soil_carbon_monoculture_rainfall")
    assert len(rule.variables_used) >= 3
    assert "legume_cover_crops" in rule.interventions


def test_rule2_fragmentation_species_disturbance():
    data = {
        "habitat_fragmentation": "high",
        "species_observations": "low bird activity observed",
        "human_impact": ["construction"],
    }
    results = evaluate_rules(data)
    ids = [r.rule_id for r in results]
    assert "R2_fragmentation_species_disturbance" in ids
    rule = next(r for r in results if r.rule_id == "R2_fragmentation_species_disturbance")
    assert len(rule.variables_used) >= 3
    assert "habitat_corridor_restoration" in rule.interventions


def test_rule3_mangrove_salinity_aquaculture():
    data = {
        "ecosystem_type": "mangrove",
        "soil_salinity": "high",
        "human_impact": ["aquaculture expansion"],
        "species_observations": "low pollinator activity",
    }
    results = evaluate_rules(data)
    ids = [r.rule_id for r in results]
    assert "R3_mangrove_salinity_aquaculture" in ids
    rule = next(r for r in results if r.rule_id == "R3_mangrove_salinity_aquaculture")
    assert len(rule.variables_used) >= 3
    assert "mangrove_buffer_restoration" in rule.interventions


def test_rule4_rainfall_erosion():
    data = {
        "rainfall_pattern": "high",
        "land_use": "degraded cropland",
        "habitat_fragmentation": "high",
    }
    results = evaluate_rules(data)
    ids = [r.rule_id for r in results]
    assert "R4_rainfall_erosion" in ids
    rule = next(r for r in results if r.rule_id == "R4_rainfall_erosion")
    assert len(rule.variables_used) >= 3
    assert "riparian_buffer_restoration" in rule.interventions


def test_no_rules_fire_on_insufficient_signal():
    data = {"ecosystem_type": "grassland"}
    results = evaluate_rules(data)
    assert results == []


def test_sundarbans_sample_triggers_multiple_rules():
    data = {
        "ecosystem_type": "mangrove",
        "land_use": "degraded mangrove edge",
        "soil_organic_carbon_percent": 0.4,
        "soil_salinity": "high",
        "rainfall_pattern": "irregular",
        "temperature_trend": "rising",
        "habitat_fragmentation": "high",
        "human_impact": ["aquaculture expansion", "plastic pollution"],
        "species_observations": "low bird and pollinator activity",
    }
    results = evaluate_rules(data)
    assert len(results) >= 3
    for rule in results:
        assert len(rule.variables_used) >= 3
