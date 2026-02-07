from __future__ import annotations
from typing import Any

from .models import Decision, DecisionRevision
from .models import Decision, DecisionRevision, ThreatLiteAssessment



def serialize_revision(r: DecisionRevision) -> dict[str, Any]:
    return {
        "revision_id": r.id,
        "decision_id": r.decision_id,
        "created_by": r.created_by,
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
        "status": d.status,  # lifecycle only (DRAFT/ACTIVE/SUPERSEDED)
        "superseded_by_id": d.superseded_by_id,
        "team_id": d.team_id,
        "created_by": d.created_by,
        "updated_by": d.updated_by,
        "archived": d.archived,
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

def serialize_threat_lite(t: ThreatLiteAssessment) -> dict:
    return {
        "id": t.id,
        "decision_id": t.decision_id,
        "created_by": t.created_by,
        "updated_by": t.updated_by,
        "context_summary": t.context_summary,
        "assumptions": t.assumptions,
        "assumption_stress_test": t.assumption_stress_test,
        "boundaries_trust": t.boundaries_trust,
        "threat_scenarios": t.threat_scenarios,
        "reflection_outcome": t.reflection_outcome,
        "reflection_notes": t.reflection_notes,
        "reflection_rationale": t.reflection_rationale,
        "guided_mode": t.guided_mode,
        "archived": t.archived,
        "tags": t.tags,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
    }
