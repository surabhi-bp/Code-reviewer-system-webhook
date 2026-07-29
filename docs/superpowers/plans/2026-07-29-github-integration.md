# GitHub Webhook and API Service Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement HMAC-SHA256 signature validation middleware and the GitHub REST API service layer for the AI Code Reviewer.

**Architecture:** Implement a utility for HMAC validation, update the webhooks API route to perform signature check, parse payload if event is `pull_request`, and define a client service to fetch PR diffs.

**Tech Stack:** Python, Flask, Requests, Pytest, HMAC/hashlib.

## Global Constraints
* No hardcoded secrets. Always read from `current_app.config`.
* Ensure blueprint responses follow the standard JSON schema: `{"status": "...", "message": "..."}`.
* Thin Controllers: Do not place the `requests` logic inside the blueprint.
* Strictly follow PEP-8 and include type hints and docstrings.

---

### Task 1: Security HMAC Signature Validation

**Files:**
- Create: `app/utils/security.py`
- Test: `tests/test_security.py`

**Interfaces:**
- Produces: `verify_github_signature(request, secret: str) -> bool`

- [ ] **Step 1: Write tests for signature verification**

Write tests checking for valid and invalid signatures, including missing or invalid headers.

Create `tests/test_security.py`:
```python
import hmac
import hashlib
import pytest
from flask import Flask, request
from app.utils.security import verify_github_signature

def test_verify_github_signature_success():
    app = Flask("test_app")
    with app.test_request_context(
        path="/github",
        method="POST",
        data=b"test-body",
        headers={"X-Hub-Signature-256": "sha256=d386d38e2d4e8b8b548b81373507fb728b97d8b51d8bbf7b9a5c81d3f66810a9"}  # HMAC-SHA256 of b"test-body" with secret "test-secret"
    ):
        assert verify_github_signature(request, "test-secret") is True

def test_verify_github_signature_failure_invalid_signature():
    app = Flask("test_app")
    with app.test_request_context(
        path="/github",
        method="POST",
        data=b"test-body",
        headers={"X-Hub-Signature-256": "sha256=invalid-signature-hash-here"}
    ):
        assert verify_github_signature(request, "test-secret") is False

def test_verify_github_signature_failure_missing_header():
    app = Flask("test_app")
    with app.test_request_context(
        path="/github",
        method="POST",
        data=b"test-body",
        headers={}
    ):
        assert verify_github_signature(request, "test-secret") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_security.py -v`
Expected: FAIL due to `ModuleNotFoundError: No module named 'app.utils'` or import failure.

- [ ] **Step 3: Write minimal implementation**

Create `app/utils/security.py`:
```python
"""
Filename: app/utils/security.py
Description: Security utility functions including GitHub Webhook signature validation.
"""

import hmac
import hashlib
from flask import Request

def verify_github_signature(request: Request, secret: str) -> bool:
    """
    Verify that the payload was sent from GitHub by validating the HMAC-SHA256 signature.
    
    Args:
        request: The Flask request object containing the headers and raw body.
        secret: The GitHub Webhook secret.
        
    Returns:
        bool: True if signature is valid, False otherwise.
    """
    if not secret:
        return False
        
    signature_header = request.headers.get("X-Hub-Signature-256")
    if not signature_header or not signature_header.startswith("sha256="):
        return False
        
    received_signature = signature_header.split("sha256=")[-1]
    
    # Compute expected signature
    payload_bytes = request.get_data()
    computed_signature = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(received_signature, computed_signature)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_security.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/utils/security.py tests/test_security.py
git commit -m "feat(security): implement HMAC-SHA256 signature verification"
```

---

### Task 2: Webhooks Blueprint Controller Integration

**Files:**
- Modify: `app/api/v1/webhooks.py`
- Test: `tests/test_webhooks.py`

**Interfaces:**
- Consumes: `verify_github_signature(request, secret: str) -> bool`

- [ ] **Step 1: Write test for webhooks route**

Create `tests/test_webhooks.py`:
```python
import json
import pytest
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
    # HMAC-SHA256 of b'{"ping": "pong"}' with key 'webhook-test-secret' is:
    # 57790b9b3e1a067ffc75e2fa672439c2794c48972e79603cf3f9d511979b008d
    headers = {
        "X-Hub-Signature-256": "sha256=57790b9b3e1a067ffc75e2fa672439c2794c48972e79603cf3f9d511979b008d",
        "X-GitHub-Event": "ping"
    }
    response = client.post(
        "/api/v1/webhooks/github",
        headers=headers,
        data=json.dumps({"ping": "pong"}),
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
    # HMAC-SHA256 of payload with secret "webhook-test-secret"
    # Using python to pre-compute the signature:
    import hmac, hashlib, json
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_webhooks.py -v`
Expected: FAIL since signature check is not yet integrated and format does not match.

- [ ] **Step 3: Write minimal implementation**

Modify `app/api/v1/webhooks.py`:
```python
"""
Filename: app/api/v1/webhooks.py
Location: ai-code-reviewer/app/api/v1/webhooks.py
Action: Webhook Blueprint Endpoint

Description:
Receives, validates, and routes incoming GitHub webhook HTTP POST requests.
"""

from flask import Blueprint, request, jsonify, current_app
from app.utils.security import verify_github_signature

webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/github', methods=['POST'])
def handle_github_webhook():
    """Receive and process GitHub Webhook events with signature verification."""
    secret = current_app.config.get("GITHUB_WEBHOOK_SECRET")
    
    # 1. Validate signature to maintain the security barrier
    if not verify_github_signature(request, secret):
        return jsonify({
            "status": "error",
            "message": "Invalid signature"
        }), 401
        
    # 2. Check the event type
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    if event_type != "pull_request":
        return jsonify({
            "status": "success",
            "message": "Event ignored"
        }), 202
        
    # 3. Parse JSON payload
    payload = request.get_json()
    if not payload:
        return jsonify({
            "status": "error",
            "message": "Missing payload"
        }), 400
        
    action = payload.get("action")
    pr_number = payload.get("number")
    repo_name = payload.get("repository", {}).get("full_name")
    
    # Return standard accepted response
    return jsonify({
        "status": "success",
        "message": "Webhook received successfully"
    }), 202
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_webhooks.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/api/v1/webhooks.py tests/test_webhooks.py
git commit -m "feat(webhook): add signature validation and payload parsing to route"
```

---

### Task 3: GitHub REST API Service Layer

**Files:**
- Create: `app/services/github_service.py`
- Test: `tests/test_github_service.py`

**Interfaces:**
- Produces: `GitHubService.fetch_pr_diff(repo_name: str, pr_number: int) -> str`

- [ ] **Step 1: Write test for GitHubService**

Create `tests/test_github_service.py`:
```python
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.services.github_service import GitHubService

def test_fetch_pr_diff_success():
    app = Flask("test_app")
    app.config["GITHUB_TOKEN"] = "fake-github-token"
    
    with app.app_context():
        service = GitHubService()
        
        with patch("app.services.github_service.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.text = "diff --git a/file.txt b/file.txt"
            mock_get.return_value = mock_response
            
            diff = service.fetch_pr_diff("owner/repo", 123)
            
            assert diff == "diff --git a/file.txt b/file.txt"
            mock_get.assert_called_once_with(
                "https://api.github.com/repos/owner/repo/pulls/123",
                headers={
                    "Authorization": "Bearer fake-github-token",
                    "Accept": "application/vnd.github.v3.diff"
                },
                timeout=10
            )

def test_fetch_pr_diff_http_error():
    app = Flask("test_app")
    app.config["GITHUB_TOKEN"] = "fake-github-token"
    
    with app.app_context():
        service = GitHubService()
        
        with patch("app.services.github_service.requests.get") as mock_get:
            from requests.exceptions import HTTPError
            mock_get.side_effect = HTTPError("Not Found")
            
            with pytest.raises(Exception) as exc_info:
                service.fetch_pr_diff("owner/repo", 123)
            assert "Failed to fetch Pull Request diff" in str(exc_info.value)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_github_service.py -v`
Expected: FAIL (missing `GitHubService`)

- [ ] **Step 3: Write minimal implementation**

Create `app/services/github_service.py`:
```python
"""
Filename: app/services/github_service.py
Description: Service for interacting with GitHub REST API endpoints.
"""

import requests
from flask import current_app

class GitHubService:
    """Service to handle REST requests to the GitHub API."""

    def fetch_pr_diff(self, repo_name: str, pr_number: int) -> str:
        """
        Fetch the unified diff of a Pull Request from GitHub.
        
        Args:
            repo_name: Full repository name (e.g. 'owner/repo').
            pr_number: Pull request number.
            
        Returns:
            str: The raw diff content.
            
        Raises:
            Exception: If request fails or configuration is missing.
        """
        token = current_app.config.get("GITHUB_TOKEN")
        if not token:
            raise Exception("GITHUB_TOKEN is not configured in the application.")
            
        url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.diff"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch Pull Request diff from GitHub: {str(e)}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_github_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/github_service.py tests/test_github_service.py
git commit -m "feat(services): implement GitHubService to fetch PR diffs"
```
