"""Expression preset planning and item selection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List
from .schemas import ExpressionItem


def get_default_presets_path() -> Path:
    # First look relative to this module in references/
    repo_root = Path(__file__).resolve().parent.parent.parent
    ref_path = repo_root / "references" / "expression-presets.json"
    if ref_path.exists():
        return ref_path
    raise FileNotFoundError("expression-presets.json not found in references/")


def load_all_presets(presets_path: Path | None = None) -> List[ExpressionItem]:
    path = presets_path or get_default_presets_path()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    items = [ExpressionItem(**item) for item in data]

    # Validate uniqueness
    ids = set()
    captions = set()
    for item in items:
        if not item.id or not item.caption:
            raise ValueError(f"Preset item missing id or caption: {item}")
        if item.id in ids:
            raise ValueError(f"Duplicate preset id: {item.id}")
        if item.caption in captions:
            raise ValueError(f"Duplicate preset caption: {item.caption}")
        ids.add(item.id)
        captions.add(item.caption)

    return items


def plan_expressions(count: int = 16, presets_path: Path | None = None) -> List[ExpressionItem]:
    """Select 8, 16, or 24 expressions."""
    all_items = load_all_presets(presets_path)

    if count == 8:
        # High frequency curated 8 items
        selected_ids = [
            "01_hello",
            "03_goodnight",
            "04_laugh",
            "06_cry",
            "09_acknowledged",
            "11_thanks",
            "13_yay",
            "16_love",
        ]
        item_map = {item.id: item for item in all_items}
        return [item_map[i] for i in selected_ids if i in item_map]
    elif count == 16:
        return all_items[:16]
    elif count == 24:
        return all_items[:24]
    else:
        raise ValueError(f"Count must be 8, 16, or 24, got {count}")
