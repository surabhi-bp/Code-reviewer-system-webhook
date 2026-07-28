"""
Filename: app/models/organization.py
Location: ai-code-reviewer/app/models/organization.py
Action: Organization Model Class

Description:
Represents a GitHub organization or user account that owns repositories.
"""

from datetime import datetime
from typing import List
from sqlalchemy import BigInteger, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class Organization(db.Model):
    """Organization model representing GitHub organizations or individual user accounts."""

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    github_org_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )

    # Relationships
    repositories: Mapped[List["Repository"]] = relationship(
        "Repository",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Organization id={self.id} name={self.name} github_org_id={self.github_org_id}>"
