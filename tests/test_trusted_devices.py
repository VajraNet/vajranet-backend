import pytest

def test_list_trusted_devices(client):
    resp = client.get("/api/v1/devices/trusted/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "data" in data
    assert isinstance(data["data"], list)

def test_relay_sms_sos(client):
    payload = {
        "raw_sms_content": "🚨 VAJRANET EMERGENCY SOS Urgency: CRITICAL GPS: 12.9716, 77.5946",
        "sender_phone": "+91 98765 11111",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "severity": "CRITICAL",
        "user_name": "Test Citizen SMS",
        "notes": "Trapped in flood",
        "relayed_by_phone": "+91 98765 43210"
    }
    resp = client.post("/api/v1/devices/trusted/relay-sos", json=payload)
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["success"] is True
    assert res_data["data"]["source"] == "SMS_RELAY"
