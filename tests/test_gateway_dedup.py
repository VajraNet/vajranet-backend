def test_gateway_dedup_behavior(client, db_session):
    sync_payload = {
        "gateway_id": "GATEWAY-DEDUP-TEST",
        "events": [
            {
                "message_id": "VJ-OFFLINE-DEDUP-001",
                "type": "SOS",
                "created_at": "2026-08-08T10:00:00Z",
                "origin_device_id": "PHONE-TEST-DEDUP",
                "payload": {
                    "latitude": 26.4499,
                    "longitude": 80.3319,
                    "message": "Testing deduplication",
                    "severity": "CRITICAL"
                }
            }
        ]
    }

    # First call
    res1 = client.post("/api/v1/gateway/sync", json=sync_payload)
    assert res1.status_code == 200
    data1 = res1.json()
    assert "VJ-OFFLINE-DEDUP-001" in data1["accepted"]

    # Second call
    res2 = client.post("/api/v1/gateway/sync", json=sync_payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert "VJ-OFFLINE-DEDUP-001" in data2["duplicates"]

    # Database verification
    from app.models.sos import SOSAlert
    count = db_session.query(SOSAlert).filter(SOSAlert.message_id == "VJ-OFFLINE-DEDUP-001").count()
    assert count == 1, "Expected exactly ONE SOS record"
