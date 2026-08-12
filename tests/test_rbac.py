import pytest

def test_rbac_government_sos_patch(client, citizen_auth, volunteer_auth, government_auth):
    # Setup dummy data or rely on 404
    sos_id = "test-sos-id"
    payload = {"status": "IN_PROGRESS"}
    
    # 1. Citizen calling PATCH gets 403
    res1 = client.patch(f"/api/v1/government/sos/{sos_id}", json=payload, headers=citizen_auth)
    assert res1.status_code == 403

    # 2. Volunteer calling PATCH gets 403
    res2 = client.patch(f"/api/v1/government/sos/{sos_id}", json=payload, headers=volunteer_auth)
    assert res2.status_code == 403

    # 3. Government calling PATCH gets 200 or 404 (if not found, meaning auth succeeded)
    res3 = client.patch(f"/api/v1/government/sos/{sos_id}", json=payload, headers=government_auth)
    assert res3.status_code in (200, 404)
