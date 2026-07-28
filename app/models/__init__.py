"""
Filename: app/models/__init__.py
Location: ai-code-reviewer/app/models/__init__.py
Action: Models Blueprint Init

Description:
Imports and registers all SQLAlchemy models with metadata to avoid lazy import issues.
"""

from app.models.organization import Organization
from app.models.repository import Repository
from app.models.pull_request import PullRequest
from app.models.review_run import ReviewRun
from app.models.review_issue import ReviewIssue

__all__ = [
    "Organization",
    "Repository",
    "PullRequest",
    "ReviewRun",
    "ReviewIssue",
]
