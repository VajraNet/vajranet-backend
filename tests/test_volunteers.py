def test_volunteer_profile_registration(client, volunteer_auth):
    profile_payload = {
        "skills": ["Emergency Medical Responder", "Boat Navigation", "Ham Radio"],
        "availability_status": "AVAILABLE",
        "phone": "+91-9876543211",
        "location": "North Rescue Command Center"
    }
    res = client.post("/api/v1/volunteers/profile", headers=volunteer_auth, json=profile_payload)
    assert res.status_code == 201
    data = res.json()["data"]
    assert "Ham Radio" in data["skills"]
    assert data["availability_status"] == "AVAILABLE"


def test_volunteer_claim_and_complete_task(client, volunteer_auth, citizen_auth):
    # 1. Citizen reports an incident
    inc_res = client.post("/api/v1/incidents", headers=citizen_auth, json={
        "title": "Elderly citizens stranded on 1st floor",
        "description": "Need boat evacuation assistance due to 4 feet floodwater.",
        "type": "FLOOD",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "severity": "HIGH"
    })
    incident_id = inc_res.json()["data"]["id"]

    # 2. Volunteer views incidents and claims the task
    claim_res = client.post(f"/api/v1/volunteers/incidents/{incident_id}/accept", headers=volunteer_auth)
    assert claim_res.status_code == 201
    task_data = claim_res.json()["data"]
    assert task_data["status"] == "ACCEPTED"

    # 3. Volunteer updates task status to COMPLETED
    update_res = client.patch(f"/api/v1/volunteers/incidents/{incident_id}/status", headers=volunteer_auth, json={
        "status": "COMPLETED",
        "notes": "Elderly citizens safely evacuated to North Shelter via rescue raft."
    })
    assert update_res.status_code == 200
    assert update_res.json()["data"]["status"] == "COMPLETED"


def test_volunteer_fundraiser_lifecycle(client, volunteer_auth):
    camp_payload = {
        "title": "Emergency Rations for Flood Victims",
        "description": "Fundraising for 1,000 dry ration food kits and water purification tablets.",
        "target_amount": 250000.0,
        "beneficiary": "East District Flood Victims"
    }
    create_res = client.post("/api/v1/volunteers/fundraisers", headers=volunteer_auth, json=camp_payload)
    assert create_res.status_code == 201
    camp_id = create_res.json()["data"]["id"]

    # List fundraisers
    list_res = client.get("/api/v1/volunteers/fundraisers", headers=volunteer_auth)
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) >= 1

    # Update amount raised
    patch_res = client.patch(f"/api/v1/volunteers/fundraisers/{camp_id}", headers=volunteer_auth, json={
        "raised_amount": 150000.0
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["raised_amount"] == 150000.0
