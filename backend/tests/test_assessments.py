from tests.conftest import SUNDARBANS_SAMPLE


def test_health_endpoint(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in {"ok", "degraded"}
    assert "evidence_chunks_indexed" in body


def test_create_assessment_rejects_invalid_ph(client):
    payload = dict(SUNDARBANS_SAMPLE)
    payload["soil_ph"] = 25  # invalid, pH is 0-14
    resp = client.post("/api/assessments", json=payload)
    assert resp.status_code == 422


def test_create_assessment_rejects_invalid_latitude(client):
    payload = dict(SUNDARBANS_SAMPLE)
    payload["latitude"] = 200
    resp = client.post("/api/assessments", json=payload)
    assert resp.status_code == 422


def test_create_sundarbans_assessment_returns_ranked_recommendations(client):
    resp = client.post("/api/assessments", json=SUNDARBANS_SAMPLE)
    assert resp.status_code == 200
    body = resp.json()
    assert body["biodiversity_risk_level"] in {"high", "critical"}
    assert len(body["recommendations"]) >= 1
    priorities = [r["priority"] for r in body["recommendations"]]
    assert priorities == sorted(priorities)
    for rec in body["recommendations"]:
        assert rec["time_horizon"] in {"short", "medium", "long"}
        assert rec["impacted_metrics"]
        assert rec["scientific_reasoning"]


def test_get_assessment_round_trips(client):
    create_resp = client.post("/api/assessments", json=SUNDARBANS_SAMPLE)
    assessment_id = create_resp.json()["assessment_id"]
    get_resp = client.get(f"/api/assessments/{assessment_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["assessment_id"] == assessment_id


def test_get_missing_assessment_returns_404(client):
    resp = client.get("/api/assessments/does-not-exist")
    assert resp.status_code == 404


def test_evidence_search_endpoint(client):
    resp = client.get("/api/evidence/search", params={"q": "mangrove restoration"})
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) > 0
    assert all(r["url"].startswith("http") for r in results)
