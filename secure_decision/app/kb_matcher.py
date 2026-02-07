from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, List, Tuple

from .kb_loader import KnowledgeBase, MitigationCard


@dataclass(frozen=True)
class MatchResult:
    card_id: str
    title: str
    score: int
    why: List[str]
    card: dict


def _fuzzy_ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def match_cards(
    kb: KnowledgeBase,
    decision_pattern: str,
    tags: Dict[str, List[str]],
    top_k: int = 5,
) -> List[MatchResult]:
    """
    Scoring v1 (simple, transparent):
      - fuzzy decision pattern match: +6 if ratio >= 0.60 (scaled)
      - assumption tag match: +3 each
      - boundary tag match: +2 each
      - failure_mode tag match: +2 each
      - control tag match: +1 each
      - coverage bonus (assumption + boundary each have >=1 match): +3
    """
    inp = {
        "assumption": set(tags.get("assumption", []) or []),
        "boundary": set(tags.get("boundary", []) or []),
        "failure_mode": set(tags.get("failure_mode", []) or []),
        "control": set(tags.get("control", []) or []),
    }

    results: List[MatchResult] = []

    for c in kb.cards:
        score = 0
        why: List[str] = []

        # decision pattern fuzzy
        ratio = _fuzzy_ratio(decision_pattern, c.decision_pattern)
        if ratio >= 0.60:
            dp_score = int(6 * ratio)
            score += dp_score
            why.append(f"decision_pattern similar (ratio={ratio:.2f}, +{dp_score})")

        ct = c.tags()
        card_tags = {
            "assumption": set(ct["assumption"]),
            "boundary": set(ct["boundary"]),
            "failure_mode": set(ct["failure_mode"]),
            "control": set(ct["control"]),
        }

        a_match = inp["assumption"] & card_tags["assumption"]
        b_match = inp["boundary"] & card_tags["boundary"]
        f_match = inp["failure_mode"] & card_tags["failure_mode"]
        c_match = inp["control"] & card_tags["control"]

        if a_match:
            add = 3 * len(a_match)
            score += add
            why.append(f"assumption tags match {sorted(a_match)} (+{add})")
        if b_match:
            add = 2 * len(b_match)
            score += add
            why.append(f"boundary tags match {sorted(b_match)} (+{add})")
        if f_match:
            add = 2 * len(f_match)
            score += add
            why.append(f"failure_mode tags match {sorted(f_match)} (+{add})")
        if c_match:
            add = 1 * len(c_match)
            score += add
            why.append(f"control tags match {sorted(c_match)} (+{add})")

        if a_match and b_match:
            score += 3
            why.append("coverage bonus (assumption+boundary) (+3)")

        if score > 0:
            results.append(
                MatchResult(
                    card_id=c.id,
                    title=c.title,
                    score=score,
                    why=why,
                    card=c.raw,
                )
            )

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_k]
