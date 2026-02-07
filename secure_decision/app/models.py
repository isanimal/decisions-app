from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    memberships: Mapped[List["Membership"]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan",
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    default_team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)

    memberships: Mapped[List["Membership"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="MEMBER")  # ADMIN|MEMBER|VIEWER

    user: Mapped["User"] = relationship(back_populates="memberships")
    team: Mapped["Team"] = relationship(back_populates="memberships")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    decision_id: Mapped[int] = mapped_column(ForeignKey("decisions.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    decision: Mapped["Decision"] = relationship(back_populates="comments")


class Mention(Base):
    __tablename__ = "mentions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"), nullable=False)
    mentioned_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    context: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Decision Statement fields (kept explicit & textual)
    technical_goal: Mapped[str] = mapped_column(Text, nullable=False, default="")
    assumptions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    conscious_simplifications: Mapped[str] = mapped_column(Text, nullable=False, default="")
    non_negotiables: Mapped[str] = mapped_column(Text, nullable=False, default="")
    accepted_worst_case: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # lifecycle (NOT security status)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT")  # DRAFT|ACTIVE|SUPERSEDED
    superseded_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("decisions.id"), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    revisions: Mapped[List["DecisionRevision"]] = relationship(
        back_populates="decision",
        cascade="all, delete-orphan",
        order_by="DecisionRevision.changed_at.desc()",
    )
    
    threat_lite_assessments: Mapped[List["ThreatLiteAssessment"]] = relationship(
        back_populates="decision",
        cascade="all, delete-orphan",
        order_by="ThreatLiteAssessment.created_at.desc()",
    )

    comments: Mapped[List["Comment"]] = relationship(
        back_populates="decision",
        cascade="all, delete-orphan",
        order_by="Comment.created_at.asc()",
    )

class DecisionRevision(Base):
    __tablename__ = "decision_revisions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    decision_id: Mapped[int] = mapped_column(ForeignKey("decisions.id"), nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    change_summary: Mapped[str] = mapped_column(String(300), nullable=False, default="Updated decision")

    # minimal “what changed” (human-readable)
    changed_fields: Mapped[str] = mapped_column(String(500), nullable=False, default="")

    # minimal snapshots (optional but useful for v0.1)
    before_snapshot: Mapped[str] = mapped_column(Text, nullable=False, default="")
    after_snapshot: Mapped[str] = mapped_column(Text, nullable=False, default="")

    decision: Mapped["Decision"] = relationship(back_populates="revisions")

class ThreatLiteAssessment(Base):
    __tablename__ = "threat_lite_assessments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    decision_id: Mapped[int] = mapped_column(ForeignKey("decisions.id"), nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Step 1 — Context framing
    context_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Step 2 — Assumption extraction
    assumptions: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Step 3 — Stress test assumptions
    assumption_stress_test: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Step 4 — Boundary & trust shift
    boundaries_trust: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Step 5 — Threat framing (realistic scenarios)
    threat_scenarios: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Step 6 — Decision reflection (accept/change/compensate)
    reflection_outcome: Mapped[str] = mapped_column(String(20), nullable=False, default="accept")
    reflection_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    reflection_rationale: Mapped[str] = mapped_column(Text, nullable=False, default="")
    guided_mode: Mapped[bool] = mapped_column(default=True)

    # Future bridge to KB matching (CSV tags or JSON string)
    tags: Mapped[str] = mapped_column(Text, nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    decision: Mapped["Decision"] = relationship(back_populates="threat_lite_assessments")


class KBCard(Base):
    """Knowledge Base Card model."""
    
    __tablename__ = "kb_cards"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    examples: Mapped[str] = mapped_column(Text, nullable=True, default="")
    source: Mapped[str] = mapped_column(String(200), nullable=True, default="")
    
    # Categorization
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tags: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Assessment mapping
    threat_lite_assessment_ids: Mapped[List[int]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "examples": self.examples,
            "source": self.source,
            "category": self.category,
            "tags": self.tags,
            "severity": self.severity,
            "threat_lite_assessment_ids": self.threat_lite_assessment_ids,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
