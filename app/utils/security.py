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
