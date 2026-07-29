# Design Specification: GitHub Webhook Integration and API Service Layer

This document details the design for the HMAC-SHA256 signature validation middleware and the GitHub REST API service layer.

## 1. Security Utilities (`app/utils/security.py`)
Implement HMAC-SHA256 signature verification for incoming GitHub webhook payloads.

### Specifications
* **Function Signature**: `verify_github_signature(request, secret: str) -> bool`
* **Inputs**:
  - `request`: Flask Request object.
  - `secret`: Webhook secret key string.
* **Logic**:
  1. Retrieve `X-Hub-Signature-256` header. If absent or malformed (doesn't start with `sha256=`), return `False`.
  2. Retrieve raw request body using `request.get_data()`.
  3. Generate the expected signature using `hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()`.
  4. Perform a timing-attack safe comparison between the header signature (after removing the `sha256=` prefix) and the expected signature using `hmac.compare_digest`.

---

## 2. Webhooks Blueprint Controller (`app/api/v1/webhooks.py`)
Handle the endpoint routing, authentication checks, and payload routing.

### Specifications
* **Endpoint**: `POST /api/v1/webhooks/github`
* **Control Flow**:
  1. Extract `GITHUB_WEBHOOK_SECRET` from `current_app.config`.
  2. Call `verify_github_signature(request, secret)`.
  3. If verification fails:
     - Return JSON `{"status": "error", "message": "Invalid signature"}` with status code `401`.
  4. If verification succeeds:
     - Retrieve `X-GitHub-Event` header.
     - If the event is not `pull_request` (e.g. `ping`):
       - Return JSON `{"status": "success", "message": "Event ignored"}` with status code `202`.
     - If the event is `pull_request`:
       - Parse the JSON payload to extract `action`, `number` (PR number), and `repository.full_name`.
       - Return JSON `{"status": "success", "message": "Webhook received successfully"}` with status code `202`.

---

## 3. GitHub Service (`app/services/github_service.py`)
Implement the client to communicate with the GitHub REST API.

### Specifications
* **Class**: `GitHubService`
* **Methods**:
  - `fetch_pr_diff(repo_name: str, pr_number: int) -> str`
    - Construct the request URL: `https://api.github.com/repos/{repo_name}/pulls/{pr_number}`
    - Retrieve `GITHUB_TOKEN` from `current_app.config`.
    - Make a HTTP `GET` request using `requests`.
    - Set headers:
      - `Authorization`: `Bearer {token}` (or `token {token}`)
      - `Accept`: `application/vnd.github.v3.diff`
    - Handle exceptions gracefully, log errors, and return the diff as a string.

---

## 4. Verification Plan
* Create tests under `tests/` directory to verify:
  - Valid signature webhook payloads are accepted (returns 202).
  - Invalid signature webhook payloads are rejected (returns 401).
  - Webhook handles non-`pull_request` events correctly.
  - `GitHubService.fetch_pr_diff` calls the correct GitHub URL with authenticating headers and returns the diff.
