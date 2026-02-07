from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml


class KBLoadError(RuntimeError):
    pass


@dataclass(frozen=True)
class MitigationCard:
    raw: Dict[str, Any]

    @property
    def id(self) -> str:
        return str(self.raw.get("id", "")).strip()

    @property
    def title(self) -> str:
        return str(self.raw.get("title", "")).strip()

    @property
    def decision_pattern(self) -> str:
        return str(self.raw.get("decision_pattern", "")).strip()

    @property
    def summary(self) -> str:
        return str(self.raw.get("summary", "")).strip()

    def tags(self) -> Dict[str, List[str]]:
        tags = self.raw.get("tags", {}) or {}
        return {
            "assumption": list(tags.get("assumption", []) or []),
            "boundary": list(tags.get("boundary", []) or []),
            "failure_mode": list(tags.get("failure_mode", []) or []),
            "control": list(tags.get("control", []) or []),
        }


@dataclass(frozen=True)
class KnowledgeBase:
    version: str
    taxonomy: Dict[str, Set[str]]
    cards: List[MitigationCard]


def _read_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_taxonomy(taxonomy_path: Path) -> Dict[str, Set[str]]:
    data = _read_yaml(taxonomy_path) or {}
    return {
        "assumption": set(data.get("assumption_tags", []) or []),
        "boundary": set(data.get("boundary_tags", []) or []),
        "failure_mode": set(data.get("failure_mode_tags", []) or []),
        "control": set(data.get("control_tags", []) or []),
    }


def validate_card_tags(card: MitigationCard, taxonomy: Dict[str, Set[str]]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    tags = card.tags()
    for dim, values in tags.items():
        allowed = taxonomy.get(dim, set())
        for v in values:
            if v not in allowed:
                errors.append(f"{card.id}: unknown tag '{v}' in tags.{dim}")
    return (len(errors) == 0, errors)


def load_cards(cards_dir: Path) -> List[MitigationCard]:
    if not cards_dir.exists():
        raise KBLoadError(f"Cards directory not found: {cards_dir}")
    cards: List[MitigationCard] = []
    for path in sorted(cards_dir.glob("*.yml")):
        raw = _read_yaml(path) or {}
        cards.append(MitigationCard(raw=raw))
    return cards


def load_kb(base_dir: Path) -> KnowledgeBase:
    taxonomy_path = base_dir / "schema" / "taxonomy.yml"
    cards_dir = base_dir / "cards"

    if not taxonomy_path.exists():
        raise KBLoadError(f"taxonomy.yml not found: {taxonomy_path}")

    taxonomy = load_taxonomy(taxonomy_path)
    cards = load_cards(cards_dir)

    all_errors: List[str] = []
    for c in cards:
        ok, errs = validate_card_tags(c, taxonomy)
        if not ok:
            all_errors.extend(errs)

    if all_errors:
        msg = "KB validation failed:\n" + "\n".join(all_errors[:50])
        if len(all_errors) > 50:
            msg += f"\n... and {len(all_errors) - 50} more"
        raise KBLoadError(msg)

    version = str((_read_yaml(taxonomy_path) or {}).get("version", "1"))
    return KnowledgeBase(version=version, taxonomy=taxonomy, cards=cards)
