from tests.conftest import SUNDARBANS_SAMPLE


def _create_assessment(client) -> str:
    return client.post("/api/assessments", json=SUNDARBANS_SAMPLE).json()["assessment_id"]


def test_baseline_requires_existing_assessment(client):
    resp = client.post(
        "/api/mrv/baselines",
        json={"assessment_id": "does-not-exist", "soil_organic_carbon_percent": 0.4},
    )
    assert resp.status_code == 404


def test_tracker_without_baseline_returns_404(client):
    assessment_id = _create_assessment(client)
    resp = client.get(f"/api/mrv/{assessment_id}")
    assert resp.status_code == 404


def test_baseline_only_reports_no_claimed_improvement(client):
    assessment_id = _create_assessment(client)
    client.post(
        "/api/mrv/baselines",
        json={
            "assessment_id": assessment_id,
            "soil_organic_carbon_percent": 0.4,
            "soil_moisture_percent": 18,
            "species_richness_index": 20,
            "habitat_connectivity_index": 15,
            "pollution_risk_index": 70,
        },
    )
    resp = client.get(f"/api/mrv/{assessment_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["observations"] == []
    assert "no improvement or decline can be claimed" in body["summary"].lower()
    for comparison in body["comparisons"]:
        assert comparison["trend"] == "insufficient_data"


def test_followup_observation_shows_real_comparison(client):
    assessment_id = _create_assessment(client)
    baseline_resp = client.post(
        "/api/mrv/baselines",
        json={
            "assessment_id": assessment_id,
            "soil_organic_carbon_percent": 0.4,
            "soil_moisture_percent": 18,
            "species_richness_index": 20,
            "habitat_connectivity_index": 15,
            "pollution_risk_index": 70,
        },
    ).json()
    baseline_id = baseline_resp["baseline_id"]

    client.post(
        "/api/mrv/observations",
        json={
            "baseline_id": baseline_id,
            "soil_organic_carbon_percent": 0.6,
            "soil_moisture_percent": 22,
            "species_richness_index": 28,
            "habitat_connectivity_index": 15,
            "pollution_risk_index": 55,
        },
    )

    resp = client.get(f"/api/mrv/{assessment_id}")
    body = resp.json()
    assert len(body["observations"]) == 1

    by_metric = {c["metric"]: c for c in body["comparisons"]}
    assert by_metric["Soil organic carbon (%)"]["trend"] == "improved"
    assert by_metric["Species richness index"]["trend"] == "improved"
    assert by_metric["Pollution risk index (lower is better)"]["trend"] == "improved"
    assert by_metric["Habitat connectivity index"]["trend"] == "no_change"
