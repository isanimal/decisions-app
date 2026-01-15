from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    context: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Decision Statement fields (kept explicit & textual)
    technical_goal: Mapped[str] = mapped_column(Text, nullable=False, default="")
    assumptions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    conscious_simplifications: Mapped[str] = mapped_column(Text, nullable=False, default="")
    non_negotiables: Mapped[str] = mapped_column(Text, nullable=False, default="")
    accepted_worst_case: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # lifecycle (NOT security status)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")  # draft|active

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    revisions: Mapped[list["DecisionRevision"]] = relationship(
        back_populates="decision",
        cascade="all, delete-orphan",
        order_by="DecisionRevision.changed_at.desc()",
    )


class DecisionRevision(Base):
    __tablename__ = "decision_revisions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    decision_id: Mapped[int] = mapped_column(ForeignKey("decisions.id"), nullable=False)

    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    change_summary: Mapped[str] = mapped_column(String(300), nullable=False, default="Updated decision")

    # minimal “what changed” (human-readable)
    changed_fields: Mapped[str] = mapped_column(String(500), nullable=False, default="")

    # minimal snapshots (optional but useful for v0.1)
    before_snapshot: Mapped[str] = mapped_column(Text, nullable=False, default="")
    after_snapshot: Mapped[str] = mapped_column(Text, nullable=False, default="")

    decision: Mapped["Decision"] = relationship(back_populates="revisions")
