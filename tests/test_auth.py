def test_get_me_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["success"] is False


def test_get_me_citizen(client, citizen_auth):
    response = client.get("/api/v1/auth/me", headers=citizen_auth)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["role"] == "CITIZEN"


def test_get_me_government(client, government_auth):
    response = client.get("/api/v1/auth/me", headers=government_auth)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["role"] == "GOVERNMENT"


def test_update_profile(client, citizen_auth):
    payload = {
        "name": "Jane Citizen Updated",
        "phone": "+91-9876543210"
    }
    response = client.patch("/api/v1/auth/me", headers=citizen_auth, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Jane Citizen Updated"
    assert data["data"]["phone"] == "+91-9876543210"
