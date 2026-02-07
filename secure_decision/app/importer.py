from typing import Any
from sqlalchemy.orm import Session

from .models import Decision, DecisionRevision


class ImportError(Exception):
    pass


def validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("format") != "secure-decision.export.v0.1":
        raise ImportError("Unsupported export format")

    if "decisions" not in payload and "decision" not in payload:
        raise ImportError("Payload must contain 'decisions' or 'decision'")


def normalize_decisions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if "decisions" in payload:
        return payload["decisions"]
    return [payload["decision"]]


def import_decisions(
    db: Session,
    payload: dict[str, Any],
    team_id: int | None = None,
    created_by: int | None = None,
) -> dict[str, Any]:
    validate_payload(payload)
    items = normalize_decisions(payload)

    imported = []

    for item in items:
        stmt = item.get("statement", {})

        d = Decision(
            team_id=team_id,
            created_by=created_by,
            updated_by=created_by,
            title=item.get("title", "").strip(),
            context=item.get("context", "").strip(),
            status="DRAFT",  # ALWAYS draft on import
            technical_goal=stmt.get("technical_goal", ""),
            assumptions=stmt.get("assumptions", ""),
            conscious_simplifications=stmt.get("conscious_simplifications", ""),
            non_negotiables=stmt.get("non_negotiables", ""),
            accepted_worst_case=stmt.get("accepted_worst_case", ""),
        )
        db.add(d)
        db.flush()  # get ID without commit
