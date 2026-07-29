# E2E Review Orchestration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the end-to-end PR review orchestration pipeline including asynchronous webhook processing, database entity auto-creation, LLM-based analysis coordination, and GitHub comments posting.

**Architecture:** Webhook endpoint validates requests and spins off a background thread with the Flask app context. The orchestrator inside the thread checks/creates DB records, retrieves the PR diff, runs Ollama AI engine analysis, commits results to the DB, and formats/posts a markdown summary table to GitHub.

**Tech Stack:** Python, Flask, SQLAlchemy, requests, pytest

## Global Constraints
- Strictly adhere to PEP-8.
- Mock all database commits and network calls in the test suite.
- Use Python's built-in `threading.Thread` with Flask application context.
- Keep controller thin, move orchestration to `ReviewOrchestratorService`.

---

### Task 1: Update GitHubService

**Files:**
- Modify: `app/services/github_service.py`
- Modify: `tests/test_github_service.py`

**Interfaces:**
- Consumes: `GITHUB_TOKEN` from application config.
- Produces: `post_pr_review(repo_name: str, pr_number: int, issues: list[dict]) -> dict`

- [ ] **Step 1: Write failing tests for post_pr_review**
  Create `test_post_pr_review_success` and `test_post_pr_review_failure` in `tests/test_github_service.py` asserting post request payload is correct.
- [ ] **Step 2: Run test to verify it fails**
  Run: `venv\Scripts\python -m pytest tests/test_github_service.py`
  Expected: FAIL with AttributeError (no post_pr_review method).
- [ ] **Step 3: Implement post_pr_review**
  Add `post_pr_review` method to `GitHubService` in `app/services/github_service.py`. It should format issues into a clean Markdown table with header `## Automated Code Review Summary` and post it to `POST /repos/{repo_name}/issues/{pr_number}/comments`.
- [ ] **Step 4: Run test to verify it passes**
  Run: `venv\Scripts\python -m pytest tests/test_github_service.py`
  Expected: PASS
- [ ] **Step 5: Commit**
  Run: `git add app/services/github_service.py tests/test_github_service.py` and commit.

---

### Task 2: Create ReviewOrchestratorService

**Files:**
- Create: `app/services/review_orchestrator.py`

**Interfaces:**
- Consumes: `GitHubService`, `CodeParserService`, `AIEngineService`, `OllamaProvider`, `db.session`
- Produces: `ReviewOrchestratorService.process_pull_request(repo_name: str, pr_number: int, webhook_payload: dict = None)`

- [ ] **Step 1: Write shell class for ReviewOrchestratorService**
  Create `app/services/review_orchestrator.py` with empty `process_pull_request` method.
- [ ] **Step 2: Implement process_pull_request logic**
  Implement the auto-creation of `Organization`, `Repository`, and `PullRequest` records (extracting name, ids, etc., from `webhook_payload` or fetching via GitHub APIs if needed). Then fetch diff, parse diff, run `AIEngineService` with `OllamaProvider`, save `ReviewRun` & `ReviewIssue` records, and call `GitHubService.post_pr_review`.
- [ ] **Step 3: Commit**
  Run: `git add app/services/review_orchestrator.py` and commit.

---

### Task 3: Update Webhooks Controller

**Files:**
- Modify: `app/api/v1/webhooks.py`

**Interfaces:**
- Consumes: `ReviewOrchestratorService`
- Produces: Webhook endpoint spawns background thread.

- [ ] **Step 1: Implement background thread spawning**
  Update `app/api/v1/webhooks.py` to spawn a `threading.Thread` with application context to process pull request opened/synchronize events.
- [ ] **Step 2: Commit**
  Run: `git add app/api/v1/webhooks.py` and commit.

---

### Task 4: E2E and Orchestrator Unit Testing

**Files:**
- Create: `tests/test_review_orchestrator.py`
- Modify: `tests/test_webhooks.py`

**Interfaces:**
- Consumes: Whole integration flow.

- [ ] **Step 1: Write E2E mock tests**
  Create tests in `tests/test_review_orchestrator.py` mocking `GitHubService`, database session, `CodeParserService`, and `AIEngineService`.
- [ ] **Step 2: Run tests to verify all pass**
  Run: `venv\Scripts\python -m pytest`
  Expected: PASS
- [ ] **Step 3: Commit**
  Run: `git add tests/test_review_orchestrator.py tests/test_webhooks.py` and commit.
