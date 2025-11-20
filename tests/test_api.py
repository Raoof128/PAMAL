from fastapi.testclient import TestClient

from api.server import app

# Mock auth to bypass header check or just use the header
client = TestClient(app)

def test_read_main():
    response = client.get("/secrets", headers={"X-User": "test-user"})
    assert response.status_code == 200
    assert response.json() == []

def test_create_secret():
    secret_data = {
        "id": "api-test-01",
        "name": "API Test Secret",
        "type": "linux",
        "value": "SuperSecret",
        "metadata": {"host": "localhost"}
    }
    response = client.post("/secrets", json=secret_data, headers={"X-User": "test-user"})
    assert response.status_code == 201
    assert response.json() == {"status": "created", "id": "api-test-01"}

    # Verify it's in the list
    response = client.get("/secrets", headers={"X-User": "test-user"})
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "api-test-01"

def test_access_request_flow():
    # 1. Create Secret
    client.post("/secrets", json={
        "id": "flow-test-01",
        "name": "Flow Test",
        "type": "linux",
        "value": "FlowPass",
        "metadata": {"role": "linux-admin"} # Requires approval by default policy
    }, headers={"X-User": "admin"})

    # 2. Request Access
    req_payload = {"user": "bob", "secret_id": "flow-test-01", "reason": "Testing"}
    response = client.post("/request", json=req_payload)
    assert response.status_code == 200
    data = response.json()
    
    # Should be pending approval (based on default policy for linux-admin)
    # Wait, default policy in policies.py says linux-admin requires approval.
    # But wait, allowed_users for linux-admin are ["alice", "bob", "raouf"].
    # "bob" is allowed.
    
    assert data["status"] == "pending_approval"
    req_id = data["request_id"]

    # 3. Approve Request
    approve_payload = {"admin_user": "admin", "request_id": req_id, "decision": "APPROVED"}
    response = client.post("/approve", json=approve_payload, headers={"X-User": "admin"})
    assert response.status_code == 200
    assert response.json()["status"] == "approved"

    # 4. Get Credential
    response = client.get(f"/credential/{req_id}", headers={"X-User": "bob"})
    assert response.status_code == 200
    assert response.json()["secret"] == "FlowPass"
