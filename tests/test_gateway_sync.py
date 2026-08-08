def test_offline_gateway_sync_idempotency(client, db_session):
    sync_payload = {
        "gateway_id": "GATEWAY-RELAY-001",
        "events": [
            {
                "message_id": "VJ-OFFLINE-SOS-001",
                "type": "SOS",
                "created_at": "2026-08-08T10:00:00Z",
                "origin_device_id": "PHONE-MESH-VICTIM-99",
                "payload": {
                    "latitude": 26.4499,
                    "longitude": 80.3319,
                    "message": "Trapped in flood water with family on roof",
                    "severity": "CRITICAL"
                }
            },
            {
                "message_id": "VJ-OFFLINE-INC-002",
                "type": "INCIDENT",
                "created_at": "2026-08-08T10:05:00Z",
                "origin_device_id": "PHONE-MESH-VICTIM-99",
                "payload": {
                    "title": "Severe road collapse near embankment",
                    "description": "Main highway completely broken, vehicles cannot pass.",
                    "latitude": 26.4520,
                    "longitude": 80.3350,
                    "type": "LANDSLIDE",
                    "severity": "HIGH"
                }
            }
        ]
    }

    # 1. FIRST REQUEST: Both events should be accepted
    first_res = client.post("/api/v1/gateway/sync", json=sync_payload)
    assert first_res.status_code == 200
    first_data = first_res.json()
    assert first_data["success"] is True
    assert "VJ-OFFLINE-SOS-001" in first_data["accepted"]
    assert "VJ-OFFLINE-INC-002" in first_data["accepted"]
    assert len(first_data["duplicates"]) == 0
    assert len(first_data["failed"]) == 0

    # 2. SECOND REQUEST (SAME PAYLOAD): Both events must be detected as duplicates
    second_res = client.post("/api/v1/gateway/sync", json=sync_payload)
    assert second_res.status_code == 200
    second_data = second_res.json()
    assert second_data["success"] is True
    assert len(second_data["accepted"]) == 0
    assert "VJ-OFFLINE-SOS-001" in second_data["duplicates"]
    assert "VJ-OFFLINE-INC-002" in second_data["duplicates"]
    assert len(second_data["failed"]) == 0

    # 3. VERIFY DATABASE CONTAINS EXACTLY ONE RECORD PER MESSAGE_ID (NO DUPLICATES)
    from app.models.sos import SOSAlert
    from app.models.incident import Incident

    sos_count = db_session.query(SOSAlert).filter(SOSAlert.message_id == "VJ-OFFLINE-SOS-001").count()
    assert sos_count == 1, "There must NEVER be duplicate SOS records for the same offline message_id"

    inc_count = db_session.query(Incident).filter(Incident.message_id == "VJ-OFFLINE-INC-002").count()
    assert inc_count == 1, "There must NEVER be duplicate Incident records for the same offline message_id"

    # Verify origin device and original created_at was preserved
    sos_record = db_session.query(SOSAlert).filter(SOSAlert.message_id == "VJ-OFFLINE-SOS-001").first()
    assert sos_record.origin_device_id == "PHONE-MESH-VICTIM-99"
    assert sos_record.latitude == 26.4499
    assert sos_record.severity.value == "CRITICAL"
