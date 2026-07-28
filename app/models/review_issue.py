"""
Filename: app/models/review_issue.py
Location: ai-code-reviewer/app/models/review_issue.py
Action: ReviewIssue Model Class

Description:
Represents an individual finding (bug, security threat, code smell) generated during a ReviewRun.
"""

from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, String, TIMESTAMP, Integer, TEXT, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class ReviewIssue(db.Model):
    """ReviewIssue model representing specific code quality findings."""

    __tablename__ = "review_issues"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    review_run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("review_runs.id"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(TEXT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )

    # Relationships
    review_run: Mapped["ReviewRun"] = relationship(
        "ReviewRun", back_populates="review_issues"
    )

    def __repr__(self) -> str:
        return f"<ReviewIssue id={self.id} file={self.file_path} line={self.line_number} category={self.category}>"
