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
