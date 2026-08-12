import pytest
from app.core.security import create_access_token

@pytest.fixture
def other_citizen_auth():
    token = create_access_token({"sub": "user-2", "email": "user2@test.com", "user_metadata": {"role": "CITIZEN"}})
    return {"Authorization": f"Bearer {token}"}

def test_emergency_contact_crud(client, citizen_auth, other_citizen_auth):
    # 1. Citizen creates contact
    res1 = client.post("/api/v1/emergency-contacts", json={
        "name": "Mom",
        "phone": "9876543210",
        "relation": "Mother"
    }, headers=citizen_auth)
    assert res1.status_code == 200
    data1 = res1.json()["data"]
    assert data1["name"] == "Mom"
    contact_id = data1["id"]

    # 2. Citizen can list own contacts
    res2 = client.get("/api/v1/emergency-contacts", headers=citizen_auth)
    assert res2.status_code == 200
    data2 = res2.json()["data"]
    assert len(data2) >= 1
    assert any(c["id"] == contact_id for c in data2)

    # 3. Another citizen cannot see the first citizen's contacts
    res3 = client.get("/api/v1/emergency-contacts", headers=other_citizen_auth)
    assert res3.status_code == 200
    data3 = res3.json()["data"]
    assert len(data3) == 0

    # 4. Another citizen accessing specific contact gets 404 (simulates 403/404 cross user)
    res4 = client.patch(f"/api/v1/emergency-contacts/{contact_id}", json={"name": "Dad"}, headers=other_citizen_auth)
    assert res4.status_code == 404

    # 5. Citizen deletes own contact
    res5 = client.delete(f"/api/v1/emergency-contacts/{contact_id}", headers=citizen_auth)
    assert res5.status_code == 200

    # Verify deleted
    res6 = client.get("/api/v1/emergency-contacts", headers=citizen_auth)
    data6 = res6.json()["data"]
    assert not any(c["id"] == contact_id for c in data6)
