from datetime import datetime
from sqlalchemy.orm import Session

from .models import Decision, DecisionRevision


TRACKED_FIELDS = [
    "title",
    "context",
    "technical_goal",
    "assumptions",
    "conscious_simplifications",
    "non_negotiables",
    "accepted_worst_case",
    "status",
]


def snapshot(decision: Decision) -> str:
    # lightweight snapshot for v0.1; readable, not meant for audit scoring
    parts = [
        f"title: {decision.title}",
        f"status: {decision.status}",
        f"context: {decision.context}",
        f"technical_goal: {decision.technical_goal}",
        f"assumptions: {decision.assumptions}",
        f"conscious_simplifications: {decision.conscious_simplifications}",
        f"non_negotiables: {decision.non_negotiables}",
        f"accepted_worst_case: {decision.accepted_worst_case}",
    ]
    return "\n\n".join(parts)


def compute_changed_fields(before: Decision, after: Decision) -> list[str]:
    changed = []
    for f in TRACKED_FIELDS:
        if getattr(before, f) != getattr(after, f):
            changed.append(f)
    return changed


def create_revision_if_needed(db: Session, before: Decision, after: Decision, change_summary: str | None = None) -> None:
    """
    v0.1 rule:
    - If decision is ACTIVE and something meaningful changed -> create revision
    - No blame, no scoring, just traceability for knowledge transfer.
    """
    changed = compute_changed_fields(before, after)
    if not changed:
        return

    # Only create history when the decision is active (align with our v0.1 discipline)
    if before.status != "active" and after.status != "active":
        return

    rev = DecisionRevision(
        decision_id=after.id,
        change_summary=(change_summary or "Updated decision"),
        changed_fields=", ".join(changed),
        before_snapshot=snapshot(before),
        after_snapshot=snapshot(after),
    )
    db.add(rev)


def touch_updated_at(decision: Decision) -> None:
    decision.updated_at = datetime.utcnow()
