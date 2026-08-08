def test_report_incident(client, citizen_auth):
    payload = {
        "title": "Bridge damaged by heavy flash flood",
        "description": "The east bridge connecting sector 4 to sector 5 is flooded and blocked with debris.",
        "type": "FLOOD",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "severity": "HIGH",
        "media_urls": ["https://res.cloudinary.com/demo/image/upload/v1/bridge_flood.jpg"]
    }
    response = client.post("/api/v1/incidents", headers=citizen_auth, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Bridge damaged by heavy flash flood"
    assert data["data"]["status"] == "REPORTED"
    assert "https://res.cloudinary.com/demo/image/upload/v1/bridge_flood.jpg" in data["data"]["media_urls"]

    incident_id = data["data"]["id"]

    # Retrieve citizen's own incidents
    my_res = client.get("/api/v1/incidents/my", headers=citizen_auth)
    assert my_res.status_code == 200
    my_list = my_res.json()["data"]
    assert any(inc["id"] == incident_id for inc in my_list)

    # Retrieve by ID
    get_res = client.get(f"/api/v1/incidents/{incident_id}")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == incident_id
