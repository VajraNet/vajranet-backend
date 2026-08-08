def test_create_sos_anonymous(client):
    payload = {
        "message": "Trapped on roof in rising flood water",
        "latitude": 26.4499,
        "longitude": 80.3319,
        "severity": "CRITICAL"
    }
    response = client.post("/api/v1/sos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["message"] == "Trapped on roof in rising flood water"
    assert data["data"]["status"] == "ACTIVE"
    assert data["data"]["message_id"].startswith("VJ-SOS-")


def test_create_and_fetch_my_sos(client, citizen_auth):
    payload = {
        "message": "Need urgent medical evacuation for elderly patient",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "severity": "HIGH"
    }
    create_res = client.post("/api/v1/sos", headers=citizen_auth, json=payload)
    assert create_res.status_code == 201
    sos_id = create_res.json()["data"]["id"]

    my_res = client.get("/api/v1/sos/my", headers=citizen_auth)
    assert my_res.status_code == 200
    my_data = my_res.json()
    assert my_data["success"] is True
    assert len(my_data["data"]) >= 1

    detail_res = client.get(f"/api/v1/sos/{sos_id}", headers=citizen_auth)
    assert detail_res.status_code == 200
    assert detail_res.json()["data"]["id"] == sos_id
