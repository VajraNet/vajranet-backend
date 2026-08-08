def test_media_upload_signature(client, citizen_auth):
    payload = {
        "folder": "vajranet/incident_evidence",
        "resource_type": "image",
        "tags": ["flood", "disaster"]
    }
    res = client.post("/api/v1/media/signature", headers=citizen_auth, json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "signature" in data
    assert "timestamp" in data
    assert "upload_url" in data
    assert data["folder"] == "vajranet/incident_evidence"


def test_ai_disaster_safety_chat(client):
    payload = {
        "message": "Water is entering my living room during flash flood. What safety steps should I follow?",
        "latitude": 28.6139,
        "longitude": 77.2090
    }
    res = client.post("/api/v1/ai/chat", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "reply" in data
    assert "safety_advisory" in data
    assert len(data["suggested_actions"]) > 0
