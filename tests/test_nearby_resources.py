def test_nearby_shelters_search(client, government_auth):
    # Create Shelter 1 (Close: ~1 km away from 28.6139, 77.2090)
    client.post("/api/v1/government/shelters", headers=government_auth, json={
        "name": "Connaught High School Shelter",
        "description": "Reinforced gymnasium with backup generators",
        "latitude": 28.6200,
        "longitude": 77.2150,
        "address": "Connaught Place, New Delhi",
        "capacity": 300,
        "occupied": 50,
        "status": "OPEN"
    })

    # Create Shelter 2 (Far: ~1100 km away in Mumbai)
    client.post("/api/v1/government/shelters", headers=government_auth, json={
        "name": "Mumbai Coastal Shelter",
        "description": "Far away shelter",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "address": "Bandra, Mumbai",
        "capacity": 500,
        "occupied": 100,
        "status": "OPEN"
    })

    # Query near New Delhi (28.6139, 77.2090) with 20 km radius
    res = client.get("/api/v1/shelters/nearby?latitude=28.6139&longitude=77.2090&radius_km=20")
    assert res.status_code == 200
    data = res.json()["data"]

    assert len(data) >= 1
    # Check that the nearby shelter is present and Mumbai shelter is filtered out
    names = [s["name"] for s in data]
    assert "Connaught High School Shelter" in names
    assert "Mumbai Coastal Shelter" not in names

    # Available capacity calculation check: 300 - 50 = 250
    first_shelter = [s for s in data if s["name"] == "Connaught High School Shelter"][0]
    assert first_shelter["available_capacity"] == 250
    assert first_shelter["distance_km"] < 5.0


def test_nearby_hospitals_search(client, government_auth):
    client.post("/api/v1/government/hospitals", headers=government_auth, json={
        "name": "Central Metro Emergency Hospital",
        "type": "GOVERNMENT",
        "latitude": 28.6150,
        "longitude": 77.2100,
        "address": "Near Central Secretariat",
        "emergency_available": True,
        "total_beds": 100,
        "available_beds": 35,
        "icu_total": 20,
        "icu_available": 8
    })

    res = client.get("/api/v1/hospitals/nearby?latitude=28.6139&longitude=77.2090&radius_km=15")
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) >= 1
    hospital = data[0]
    assert hospital["name"] == "Central Metro Emergency Hospital"
    assert hospital["available_beds"] == 35
    assert hospital["icu_available"] == 8


def test_nearby_relief_centers(client, government_auth):
    client.post("/api/v1/government/relief-centers", headers=government_auth, json={
        "name": "Disaster Relief Supply Depot A",
        "description": "Ration kits, drinking water, and blankets",
        "latitude": 28.6145,
        "longitude": 77.2110,
        "address": "Red Cross Grounds",
        "items_available": ["Food", "Water", "Medicine", "Blankets"],
        "status": "OPEN"
    })

    res = client.get("/api/v1/relief-centers/nearby?latitude=28.6139&longitude=77.2090&radius_km=10")
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) >= 1
    center = data[0]
    assert "Medicine" in center["items_available"]
