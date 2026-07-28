"""
Filename: app/models/pull_request.py
Location: ai-code-reviewer/app/models/pull_request.py
Action: PullRequest Model Class

Description:
Represents a GitHub Pull Request event within a Repository.
"""

from datetime import datetime
from typing import List
from sqlalchemy import BigInteger, ForeignKey, String, TIMESTAMP, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class PullRequest(db.Model):
    """PullRequest model representing pull requests within repositories."""

    __tablename__ = "pull_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    repository_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("repositories.id"), nullable=False
    )
    github_pr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    state: Mapped[str] = mapped_column(String(50), default="open", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )

    # Relationships
    repository: Mapped["Repository"] = relationship(
        "Repository", back_populates="pull_requests"
    )
    review_runs: Mapped[List["ReviewRun"]] = relationship(
        "ReviewRun",
        back_populates="pull_request",
        cascade="all, delete-orphan",
    )

    # Unique Constraint on repository_id and github_pr_number
    __table_args__ = (
        UniqueConstraint(
            "repository_id", "github_pr_number", name="uq_pr_repo_number"
        ),
    )

    def __repr__(self) -> str:
        return f"<PullRequest id={self.id} number={self.github_pr_number} state={self.state}>"
