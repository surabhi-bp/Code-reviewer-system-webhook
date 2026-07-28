"""
Filename: app/models/repository.py
Location: ai-code-reviewer/app/models/repository.py
Action: Repository Model Class

Description:
Represents an individual version-controlled code repository.
"""

from datetime import datetime
from typing import List
from sqlalchemy import BigInteger, ForeignKey, String, TIMESTAMP, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class Repository(db.Model):
    """Repository model representing code repositories."""

    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("organizations.id"), nullable=False
    )
    github_repo_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="repositories"
    )
    pull_requests: Mapped[List["PullRequest"]] = relationship(
        "PullRequest",
        back_populates="repository",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Repository id={self.id} name={self.name} github_repo_id={self.github_repo_id}>"
