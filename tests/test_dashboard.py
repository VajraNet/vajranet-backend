def test_citizen_overview(client, citizen_auth):
    res = client.get("/api/v1/citizen/overview?latitude=28.6139&longitude=77.2090", headers=citizen_auth)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "total_my_incidents" in data
    assert "nearby_shelters_count" in data
    assert "active_announcements" in data


def test_government_overview(client, government_auth):
    res = client.get("/api/v1/government/overview", headers=government_auth)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "active_sos_count" in data
    assert "active_incidents_count" in data
    assert "critical_incidents_count" in data
    assert "available_shelters_count" in data
    assert "available_hospital_beds" in data


def test_volunteer_overview(client, volunteer_auth):
    res = client.get("/api/v1/volunteers/overview", headers=volunteer_auth)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "available_tasks_count" in data
    assert "accepted_tasks_count" in data
    assert "volunteer_status" in data
