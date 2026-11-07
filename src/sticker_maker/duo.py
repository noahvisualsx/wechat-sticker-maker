"""Two-person (Duo) real-person sticker catalog and prompt builder.

Covers 108 built-in real-person interaction presets across three categories:
- ``besties`` (闺蜜互动 · 36 套)
- ``couple``  (情侣互动 · 36 套)
- ``yuri``    (百合/双女主互动 · 36 套)
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from .prompts import REAL_PERSON_HARD_LOCK, composition_hint
from .schemas import CharacterBible, ExpressionItem
from .styles import resolve_style_preset

REAL_PERSON_NEGATIVE = (
    "No 2D cartoon, no anime, no flat vector illustration, no 3D doll, no panda/animal head, "
    "no face swapping, no extra limbs, no text, no letters, no speech bubbles."
)

DUO_CATEGORIES = ("besties", "couple", "yuri", "yaoi", "rivals", "family")

DUO_CATEGORY_LABELS: Dict[str, Dict[str, str]] = {
    "besties": {
        "zh": "闺蜜互动",
        "en": "Besties",
        "ko": "절친 케미",
        "ja": "親友・女子会",
        "desc_zh": "贴脸自拍、合体比心、干杯奶茶、吃瓜八卦、夸夸抱抱等 36 款真人闺蜜互动",
    },
    "couple": {
        "zh": "情侣互动",
        "en": "Couple",
        "ko": "커플 달달",
        "ja": "カップル・恋人",
        "desc_zh": "摸头杀、背后抱、捏脸宠溺、额头贴贴、围巾共戴等 36 款真人情侣互动",
    },
    "yuri": {
        "zh": "百合双女主",
        "en": "Yuri / GL",
        "ko": "백합 / 트윈 여주",
        "ja": "百合・双女主",
        "desc_zh": "挑下巴对视、壁咚心动、十指紧扣、姐姐贴贴、宿命感双女主等 36 款真人百合互动",
    },
    "yaoi": {
        "zh": "双男主/兄弟耽美",
        "en": "Yaoi / BL / Bromance",
        "ko": "벨 / 브로맨스",
        "ja": "BL・双男主・相棒",
        "desc_zh": "指尖拽领带对视、西装背靠背、单手撑墙耳语、雨夜共撑黑伞等 20 款真人双男主互动",
    },
    "rivals": {
        "zh": "欢喜冤家/相爱相杀",
        "en": "Playful Rivals",
        "ko": "앙숙 케미 / 티격태격",
        "ja": "喧嘩するほど仲がいい",
        "desc_zh": "互相扯脸颊、石头剪刀布弹脑门、偷喝奶茶、吵完秒和好等 20 款真人相爱相杀互动",
    },
    "family": {
        "zh": "亲子/姐弟兄妹萌娃",
        "en": "Family & Siblings",
        "ko": "가족 / 남매 / 귀요미",
        "ja": "家族・姉弟・キッズ",
        "desc_zh": "大小同款托腮、姐姐护短、宠溺捏脸、发红包摸头等 20 款真人家庭温情互动",
    },
}

_DUO_ALIASES: Dict[str, str] = {
    "besties": "besties", "bestie": "besties", "friends": "besties", "bff": "besties",
    "闺蜜": "besties", "姐妹": "besties", "好朋友": "besties",
    "couple": "couple", "couples": "couple", "lovers": "couple", "romance": "couple",
    "情侣": "couple", "恋爱": "couple", "对象": "couple", "cp": "couple",
    "yuri": "yuri", "gl": "yuri", "girls-love": "yuri", "wlw": "yuri",
    "百合": "yuri", "双女主": "yuri", "姐姐": "yuri", "姬": "yuri",
    "yaoi": "yaoi", "bl": "yaoi", "bromance": "yaoi", "boys-love": "yaoi",
    "双男主": "yaoi", "耽美": "yaoi", "兄弟": "yaoi",
    "rivals": "rivals", "rival": "rivals", "enemies": "rivals", "bicker": "rivals",
    "欢喜冤家": "rivals", "冤家": "rivals", "相爱相杀": "rivals", "互怼": "rivals", "损友": "rivals",
    "family": "family", "siblings": "family", "kids": "family", "parent": "family",
    "亲子": "family", "姐弟": "family", "兄妹": "family", "萌娃": "family", "家人": "family",
}


def get_default_duo_path() -> Path:
    repo_root = Path(__file__).resolve().parent.parent.parent
    ref_path = repo_root / "references" / "duo-presets.json"
    if ref_path.exists():
        return ref_path
    raise FileNotFoundError("duo-presets.json not found in references/")


def normalize_duo_category(cat: str) -> str:
    key = cat.strip()
    resolved = _DUO_ALIASES.get(key) or _DUO_ALIASES.get(key.lower())
    if not resolved:
        raise ValueError(
            f"Unknown duo category '{cat}'. Use one of: besties (闺蜜), couple (情侣), yuri (百合)"
        )
    return resolved


@lru_cache(maxsize=2)
def load_duo_presets(path: Path | None = None) -> List[ExpressionItem]:
    """Load all 108 built-in real-person duo interaction presets."""
    p = path or get_default_duo_path()
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    items = [ExpressionItem(**raw) for raw in data]
    seen = set()
    for it in items:
        if it.id in seen:
            raise ValueError(f"Duplicate duo preset id: {it.id}")
        seen.add(it.id)
        it.captions.setdefault("zh-CN", it.caption)
    return items


def list_duo_presets(
    category: Optional[str] = None,
    path: Path | None = None,
) -> List[ExpressionItem]:
    items = list(load_duo_presets(path))
    if category:
        wanted = {
            normalize_duo_category(c)
            for c in category.replace("，", ",").split(",")
            if c.strip()
        }
        items = [it for it in items if it.category in wanted]
    return items


def plan_duo_expressions(
    count: int = 16,
    categories: Optional[Sequence[str]] = None,
    duo_ids: Optional[Sequence[str]] = None,
    path: Path | None = None,
) -> List[ExpressionItem]:
    """Select ``count`` duo interaction presets across besties / couple / yuri."""
    all_items = load_duo_presets(path)
    by_id = {it.id: it for it in all_items}
    selected: List[ExpressionItem] = []

    for did in duo_ids or []:
        if did not in by_id:
            raise ValueError(f"Unknown duo preset id: {did}")
        if by_id[did] not in selected:
            selected.append(by_id[did])

    if categories:
        wanted = [normalize_duo_category(c) for c in categories if c and c.strip()]
        pool = [it for it in all_items if it.category in wanted and it not in selected]
    else:
        pool = [it for it in all_items if it not in selected]

    # Round-robin across categories for balanced variety
    buckets: Dict[str, List[ExpressionItem]] = {}
    order: List[str] = []
    for it in pool:
        if it.category not in buckets:
            buckets[it.category] = []
            order.append(it.category)
        buckets[it.category].append(it)

    while len(selected) < count and any(buckets.values()):
        for cat in order:
            if buckets[cat] and len(selected) < count:
                selected.append(buckets[cat].pop(0))

    if len(selected) < count:
        rest = [it for it in all_items if it not in selected]
        selected.extend(rest[: count - len(selected)])
    return selected[:count]


def build_duo_static_prompt(
    bible_a: CharacterBible,
    item: ExpressionItem,
    partner_facts: Optional[List[str]] = None,
    style: Optional[str] = None,
    text_layout: str = "caption",
) -> str:
    """Build a static two-person real-portrait sticker prompt preserving BOTH real people."""
    style_id = style or bible_a.render_style.style_id
    preset = resolve_style_preset(style_id)
    facts_a = ", ".join(bible_a.identity_facts) if bible_a.identity_facts else "exact same real person as Reference Photo 1"
    facts_b = (
        ", ".join(partner_facts)
        if partner_facts
        else "exact same real person as Reference Photo 2 (or twin/partner real person if single reference)"
    )
    comp_hint = composition_hint(text_layout)
    return (
        f"Create a TWO-PERSON photorealistic real-person chat sticker (真人双人互动表情包: {DUO_CATEGORY_LABELS.get(item.category, {}).get('zh', item.category)}). "
        f"{REAL_PERSON_HARD_LOCK} "
        f"Style ID: {preset.id} ({preset.display_name}). {preset.prompt_lock} "
        f"Person A identity lock: {facts_a}. "
        f"Person B identity lock: {facts_b}. "
        f"Interaction & expression ({item.name_zh or item.caption}): {item.static_pose}. "
        f"Lighting: {preset.lighting}. "
        f"Composition: {comp_hint} Both people framed waist-up/chest-up together as one cohesive sticker silhouette on a transparent background. "
        f"Negative constraints: {REAL_PERSON_NEGATIVE} {preset.negative_extra}"
    )


def build_duo_sprite_sheet_prompt(
    bible_a: CharacterBible,
    item: ExpressionItem,
    partner_facts: Optional[List[str]] = None,
    style: Optional[str] = None,
    text_layout: str = "caption",
) -> str:
    """Build a 2x2 4-frame action sprite sheet prompt for a two-person real-portrait interaction."""
    style_id = style or bible_a.render_style.style_id
    preset = resolve_style_preset(style_id)
    facts_a = ", ".join(bible_a.identity_facts) if bible_a.identity_facts else "exact same real person as Reference Photo 1"
    facts_b = (
        ", ".join(partner_facts)
        if partner_facts
        else "exact same real person as Reference Photo 2"
    )
    poses = item.motion.keyframe_poses or [item.static_pose] * 4
    while len(poses) < 4:
        poses.append(poses[-1])
    return (
        f"Create a 2x2 ANIMATION SPRITE SHEET (4 equal quadrants: top-left=Frame 1, top-right=Frame 2, "
        f"bottom-left=Frame 3, bottom-right=Frame 4) for a TWO-PERSON real-person animated sticker "
        f"({item.name_zh or item.caption}). "
        f"{REAL_PERSON_HARD_LOCK} "
        f"Style ID: {preset.id} ({preset.display_name}). {preset.prompt_lock} "
        f"Person A identity lock: {facts_a}. Person B identity lock: {facts_b}. "
        f"Frame 1 (top-left): {poses[0]} "
        f"Frame 2 (top-right): {poses[1]} "
        f"Frame 3 (bottom-left): {poses[2]} "
        f"Frame 4 (bottom-right): {poses[3]} "
        f"Keep camera angle, head scale, and lower-torso baseline identical across all 4 quadrants. "
        f"Negative constraints: {REAL_PERSON_NEGATIVE} {preset.negative_extra}"
    )
