"""
Filename: app/models/review_run.py
Location: ai-code-reviewer/app/models/review_run.py
Action: ReviewRun Model Class

Description:
Represents a single execution cycle of the AI reviewer code analysis.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import BigInteger, ForeignKey, String, TIMESTAMP, TEXT, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class ReviewRun(db.Model):
    """ReviewRun model tracking AI reviewer analysis runs."""

    __tablename__ = "review_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pull_request_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("pull_requests.id"), nullable=False
    )
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued", nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)
    duration_sec: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )

    # Relationships
    pull_request: Mapped["PullRequest"] = relationship(
        "PullRequest", back_populates="review_runs"
    )
    review_issues: Mapped[List["ReviewIssue"]] = relationship(
        "ReviewIssue",
        back_populates="review_run",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ReviewRun id={self.id} commit={self.commit_sha} status={self.status}>"
