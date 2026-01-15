from __future__ import annotations
from typing import Any

from .models import Decision, DecisionRevision


def serialize_revision(r: DecisionRevision) -> dict[str, Any]:
    return {
        "revision_id": r.id,
        "decision_id": r.decision_id,
        "changed_at": r.changed_at.isoformat(),
        "change_summary": r.change_summary,
        "changed_fields": r.changed_fields,
        # snapshots are optional but useful for learning/transfer
        "before_snapshot": r.before_snapshot,
        "after_snapshot": r.after_snapshot,
    }


def serialize_decision(d: Decision, include_history: bool = True) -> dict[str, Any]:
    payload = {
        "decision_id": d.id,
        "title": d.title,
        "context": d.context,
        "status": d.status,  # lifecycle only (draft/active)
        "statement": {
            "technical_goal": d.technical_goal,
            "assumptions": d.assumptions,
            "conscious_simplifications": d.conscious_simplifications,
            "non_negotiables": d.non_negotiables,
            "accepted_worst_case": d.accepted_worst_case,
        },
        "created_at": d.created_at.isoformat(),
        "updated_at": d.updated_at.isoformat(),
    }

    if include_history:
        # newest first due to relationship order_by
        payload["history"] = [serialize_revision(r) for r in d.revisions]
    return payload
