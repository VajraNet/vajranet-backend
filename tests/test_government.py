def test_government_rbac_denies_citizen(client, citizen_auth):
    # Citizen trying to publish government announcement
    payload = {
        "title": "Unauthorized broadcast",
        "content": "Should not be permitted",
        "priority": "CRITICAL"
    }
    res = client.post("/api/v1/government/announcements", headers=citizen_auth, json=payload)
    assert res.status_code == 403
    assert res.json()["success"] is False


def test_government_sos_triage_and_resolve(client, government_auth):
    # First create an SOS
    sos_res = client.post("/api/v1/sos", json={
        "message": "Building surrounded by landslide debris",
        "latitude": 30.3165,
        "longitude": 78.0322,
        "severity": "CRITICAL"
    })
    sos_id = sos_res.json()["data"]["id"]

    # Government fetches SOS alerts
    list_res = client.get("/api/v1/government/sos", headers=government_auth)
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) >= 1

    # Government updates SOS status to IN_PROGRESS then RESOLVED
    update_res = client.patch(f"/api/v1/government/sos/{sos_id}", headers=government_auth, json={
        "status": "RESOLVED"
    })
    assert update_res.status_code == 200
    data = update_res.json()["data"]
    assert data["status"] == "RESOLVED"
    assert data["resolved_at"] is not None


def test_government_announcement_publishing(client, government_auth):
    payload = {
        "title": "Severe Cyclone Warning for Coastal Belt",
        "content": "All residents in Zone A are instructed to evacuate to higher ground shelters immediately.",
        "type": "EVACUATION",
        "area": "Coastal Zone A",
        "priority": "CRITICAL"
    }
    create_res = client.post("/api/v1/government/announcements", headers=government_auth, json=payload)
    assert create_res.status_code == 201
    ann_id = create_res.json()["data"]["id"]

    # Check public endpoint
    pub_res = client.get("/api/v1/announcements")
    assert pub_res.status_code == 200
    titles = [a["title"] for a in pub_res.json()["data"]]
    assert "Severe Cyclone Warning for Coastal Belt" in titles
