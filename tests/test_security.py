import hmac
import hashlib
import pytest
from flask import Flask, request
from app.utils.security import verify_github_signature

def test_verify_github_signature_success():
    app = Flask("test_app")
    secret = "test-secret"
    body = b"test-body"
    signature = f"sha256={hmac.new(secret.encode('utf-8'), body, hashlib.sha256).hexdigest()}"
    with app.test_request_context(
        path="/github",
        method="POST",
        data=body,
        headers={"X-Hub-Signature-256": signature}
    ):
        assert verify_github_signature(request, secret) is True

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

def test_verify_github_signature_failure_empty_secret():
    app = Flask("test_app")
    with app.test_request_context(
        path="/github",
        method="POST",
        data=b"test-body",
        headers={"X-Hub-Signature-256": "sha256=somehash"}
    ):
        assert verify_github_signature(request, "") is False

def test_verify_github_signature_failure_malformed_header():
    app = Flask("test_app")
    with app.test_request_context(
        path="/github",
        method="POST",
        data=b"test-body",
        headers={"X-Hub-Signature-256": "sha1=somehash"}
    ):
        assert verify_github_signature(request, "test-secret") is False
