# AI Reviewer E2E Orchestration Design Spec

Design for integrating the webhook receiver, code parser, database persistence, Ollama AI provider, and GitHub commenting API in a background thread context.

## 1. Webhook Endpoint (`app/api/v1/webhooks.py`)
- Receives pull request events ("opened", "synchronize").
- Validates the GitHub signature.
- Spawns a background worker thread (`threading.Thread`) containing the Flask application context to execute the orchestrator.
- Returns a `202 Accepted` response immediately.

## 2. Review Orchestrator (`app/services/review_orchestrator.py`)
- Coordinates the flow:
  1. Checks for/auto-creates database records (`Organization`, `Repository`, `PullRequest`).
  2. Fetches the PR diff from GitHub.
  3. Parses the diff into individual file patches.
  4. Analyzes each patch using `AIEngineService` with the `OllamaProvider`.
  5. Inserts `ReviewRun` and `ReviewIssue` records.
  6. Posts a single markdown review comment using `GitHubService.post_pr_review()`.

## 3. GitHub Service Comments (`app/services/github_service.py`)
- Method: `post_pr_review(repo_name: str, pr_number: int, issues: list[dict])`
- POSTs to: `POST /repos/{repo_name}/issues/{pr_number}/comments`
- Body formatting:
  - Header: `## Automated Code Review Summary`
  - If no issues are found: `No code quality issues found! Great job!`
  - If issues are found, a markdown table format:
    ```markdown
    | File | Line | Category | Severity | Message |
    | :--- | :--- | :------- | :------- | :------ |
    | app/main.py | 12 | security | high | Prevent SQL injection by parameterized statements. |
    ```
