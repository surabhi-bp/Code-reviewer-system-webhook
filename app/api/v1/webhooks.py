"""
Filename: app/api/v1/webhooks.py
Location: ai-code-reviewer/app/api/v1/webhooks.py
Action: Webhook Blueprint Endpoint

Description:
Receives, validates, and routes incoming GitHub webhook HTTP POST requests.
"""

from typing import Tuple
import threading
from flask import Blueprint, request, jsonify, current_app, Response
from app.utils.security import verify_github_signature
from app.services.review_orchestrator import ReviewOrchestratorService

webhooks_bp = Blueprint('webhooks', __name__)


def _run_async_pr_review(app, repo_name: str, pr_number: int, payload: dict) -> None:
    """Helper target function to run PR review inside an application context in a background thread."""
    with app.app_context():
        try:
            orchestrator = ReviewOrchestratorService()
            orchestrator.process_pull_request(
                repo_name, pr_number, webhook_payload=payload
            )
        except Exception as e:
            app.logger.error(
                f"Error processing pull request webhook in background: {e}",
                exc_info=True,
            )


@webhooks_bp.route('/github', methods=['POST'])
def handle_github_webhook() -> Tuple[Response, int]:
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
    repository = payload.get("repository") or {}
    repo_name = repository.get("full_name")
    
    # 4. Spawn background thread for opened and synchronize PR actions
    if action in ("opened", "synchronize"):
        app = current_app._get_current_object()
        thread = threading.Thread(
            target=_run_async_pr_review,
            args=(app, repo_name, pr_number, payload),
            daemon=True,
        )
        thread.start()

    # Return standard accepted response
    return jsonify({
        "status": "success",
        "message": "Webhook received successfully"
    }), 202

