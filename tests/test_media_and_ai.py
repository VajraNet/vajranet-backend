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
    # 1. Citizen Safety Query (Flood)
    payload_citizen = {
        "message": "Water is entering my living room during flash flood. What safety steps should I follow?",
        "latitude": 28.6139,
        "longitude": 77.2090
    }
    res = client.post("/api/v1/ai/chat", json=payload_citizen)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "reply" in data
    assert "Flood Safety Advisory" in data["reply"]
    assert "safety_advisory" in data
    assert "never makes independent" in data["safety_advisory"].lower() or "does not perform" in data["safety_advisory"].lower()
    assert len(data["suggested_actions"]) > 0

    # 2. Government Situational Query
    payload_gov = {
        "message": "Which areas currently have the highest number of SOS alerts?",
        "latitude": 28.6139,
        "longitude": 77.2090
    }
    res_gov = client.post("/api/v1/ai/chat", json=payload_gov)
    assert res_gov.status_code == 200
    data_gov = res_gov.json()["data"]
    assert "Situational Awareness Summary" in data_gov["reply"]
    assert len(data_gov["suggested_actions"]) > 0

    # 3. Volunteer Operational Query
    payload_vol = {
        "message": "Show me nearby incidents requiring assistance in the field",
        "latitude": 28.6139,
        "longitude": 77.2090
    }
    res_vol = client.post("/api/v1/ai/chat", json=payload_vol)
    assert res_vol.status_code == 200
    data_vol = res_vol.json()["data"]
    assert "Operational Guidance for Responders" in data_vol["reply"]
    assert len(data_vol["suggested_actions"]) > 0

