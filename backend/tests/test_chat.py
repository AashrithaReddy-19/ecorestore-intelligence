def test_chat_asks_clarifying_questions_for_vague_message(client):
    resp = client.post("/api/chat", json={"message": "Biodiversity is declining on my land."})
    assert resp.status_code == 200
    body = resp.json()
    assert body["assessment"] is None
    assert 1 <= len(body["follow_up_questions"]) <= 3
    assert "please share" in body["reply"].lower()


def test_chat_multiturn_memory_accumulates_facts(client):
    first = client.post("/api/chat", json={"message": "This is a mangrove site."}).json()
    conversation_id = first["conversation_id"]
    assert first["assessment"] is None

    second = client.post(
        "/api/chat",
        json={
            "message": "Rainfall is irregular and there is aquaculture expansion nearby. Bird activity is low.",
            "conversation_id": conversation_id,
        },
    ).json()
    assert second["conversation_id"] == conversation_id
    assert second["collected_facts"].get("ecosystem_type") == "mangrove"
    assert second["collected_facts"].get("rainfall_pattern") == "irregular"


def test_chat_produces_assessment_once_enough_data_given(client):
    resp = client.post(
        "/api/chat",
        json={
            "message": (
                "This is a mangrove site with irregular rainfall, aquaculture expansion, "
                "and low bird and pollinator activity."
            )
        },
    )
    body = resp.json()
    assert body["assessment"] is not None
    assert len(body["assessment"]["recommendations"]) >= 1
    assert len(body["retrieved_evidence"]) >= 0


def test_get_conversation_returns_message_history(client):
    first = client.post("/api/chat", json={"message": "This is a mangrove site."}).json()
    conversation_id = first["conversation_id"]
    resp = client.get(f"/api/conversations/{conversation_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["messages"]) == 2  # user + assistant
    assert body["messages"][0]["role"] == "user"
    assert body["messages"][1]["role"] == "assistant"
