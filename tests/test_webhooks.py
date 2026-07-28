import json
import pytest
import hmac
import hashlib
from app import create_app

@pytest.fixture
def client():
    app = create_app("development")
    app.config["TESTING"] = True
    app.config["GITHUB_WEBHOOK_SECRET"] = "webhook-test-secret"
    with app.test_client() as client:
        yield client

def test_github_webhook_invalid_signature(client):
    response = client.post(
        "/api/v1/webhooks/github",
        headers={"X-Hub-Signature-256": "sha256=invalid"},
        data=json.dumps({"ping": "pong"}),
        content_type="application/json"
    )
    assert response.status_code == 401
    assert response.get_json() == {
        "status": "error",
        "message": "Invalid signature"
    }

def test_github_webhook_ping_event_success(client):
    payload = {"ping": "pong"}
    data_bytes = json.dumps(payload).encode("utf-8")
    sig = hmac.new(b"webhook-test-secret", data_bytes, hashlib.sha256).hexdigest()
    headers = {
        "X-Hub-Signature-256": f"sha256={sig}",
        "X-GitHub-Event": "ping"
    }
    response = client.post(
        "/api/v1/webhooks/github",
        headers=headers,
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 202
    assert response.get_json() == {
        "status": "success",
        "message": "Event ignored"
    }

def test_github_webhook_pr_event_success(client):
    payload = {
        "action": "opened",
        "number": 42,
        "repository": {
            "full_name": "owner/repo"
        }
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    sig = hmac.new(b"webhook-test-secret", data_bytes, hashlib.sha256).hexdigest()
    
    headers = {
        "X-Hub-Signature-256": f"sha256={sig}",
        "X-GitHub-Event": "pull_request"
    }
    response = client.post(
        "/api/v1/webhooks/github",
        headers=headers,
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 202
    assert response.get_json() == {
        "status": "success",
        "message": "Webhook received successfully"
    }
