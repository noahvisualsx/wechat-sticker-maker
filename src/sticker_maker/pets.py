"""Real-Pet (`pet-portrait`) sticker catalog and photorealistic prompt builder.

Covers 40 built-in real-pet photographic sticker presets across four categories:
- ``cat_boss``     (猫主子高冷与日常 · 10 款)
- ``dog_happy``    (快乐修勾热情日常 · 10 款)
- ``pet_meme``     (萌宠打工与热梗 · 10 款)
- ``pet_festival`` (萌宠祝福与社交 · 10 款)
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from .prompts import CLEAN_BACKGROUND_HARD_LOCK, composition_hint
from .schemas import CharacterBible, ExpressionItem
from .styles import resolve_style_preset

REAL_PET_HARD_LOCK = (
    "CRITICAL REAL-PET PHOTOGRAPHIC LOCK: The subject MUST remain the exact same REAL, "
    "photorealistic pet (cat/dog/animal) from the reference photo, faithfully preserving its "
    "exact breed, coat pattern, fur color and markings, eye color, ear shape, muzzle proportions, "
    "natural animal limb/paw anatomy (strictly <=4 legs/paws, max 2 front paws visible in half-body pose), "
    "and realistic individual fur strands. Strictly forbid turning the pet into a 2D cartoon, "
    "anime mascot, flat vector illustration, 3D plastic toy, or bipedal humanoid furry."
)

REAL_PET_NEGATIVE = (
    "No 2D cartoon, no anime mascot, no flat vector illustration, no 3D doll, no human hands or body "
    "replacing pet paws, no extra paws/limbs, no stretched muzzle, no grey-white checkerboard grid, "
    "no text, no letters, no speech bubbles."
)

PET_CATEGORIES = ("cat_boss", "dog_happy", "pet_meme", "pet_festival")

PET_CATEGORY_LABELS: Dict[str, Dict[str, str]] = {
    "cat_boss": {
        "zh": "猫主子日常",
        "en": "Cat Boss Daily",
        "ko": "고양이 주인님",
        "ja": "猫さまの日常",
        "desc_zh": "蔑视眼神、飞机耳哈气、踩奶营业、农民揣手手、暗中观察、讨罐罐等 10 款实拍猫主子表情",
    },
    "dog_happy": {
        "zh": "快乐修勾日常",
        "en": "Happy Puppy Daily",
        "ko": "해피 강아지",
        "ja": "わんこの日常",
        "desc_zh": "歪头杀、吐舌傻笑、飞奔接下班、飞机耳认错、守饭碗、湿漉漉大眼睛等 10 款实拍修勾表情",
    },
    "pet_meme": {
        "zh": "萌宠打工与梗图",
        "en": "Pet Work & Memes",
        "ko": "반려동물 직장인 짤",
        "ja": "ペット仕事＆ネタ",
        "desc_zh": "戴眼镜盯电脑、爪爪敲键盘、瘫平摆烂、墨镜大佬、抱紧小鱼干、瞳孔地震等 10 款萌宠热梗",
    },
    "pet_festival": {
        "zh": "萌宠祝福与社交",
        "en": "Pet Greetings & Blessings",
        "ko": "반려동물 인사 & 축하",
        "ja": "ペット挨拶＆お祝い",
        "desc_zh": "红围巾拜年、作揖讨红包、生日小寿星、早安打工人、盖小被子晚安、送花花等 10 款萌宠社交表情",
    },
}

_PET_ALIASES: Dict[str, str] = {
    "cat_boss": "cat_boss", "cat": "cat_boss", "cats": "cat_boss", "kitty": "cat_boss",
    "猫": "cat_boss", "猫主子": "cat_boss", "猫主子日常": "cat_boss", "猫咪": "cat_boss", "喵": "cat_boss",
    "dog_happy": "dog_happy", "dog": "dog_happy", "dogs": "dog_happy", "puppy": "dog_happy",
    "狗": "dog_happy", "修勾": "dog_happy", "快乐修勾": "dog_happy", "快乐修勾日常": "dog_happy", "小狗": "dog_happy", "汪": "dog_happy",
    "pet_meme": "pet_meme", "meme": "pet_meme", "work": "pet_meme",
    "萌宠梗图": "pet_meme", "萌宠打工与梗图": "pet_meme", "打工宠": "pet_meme", "宠物梗": "pet_meme",
    "pet_festival": "pet_festival", "festival": "pet_festival", "greeting": "pet_festival",
    "萌宠祝福": "pet_festival", "萌宠祝福与社交": "pet_festival", "宠物拜年": "pet_festival", "宠物日常": "pet_festival",
}


def get_default_pet_path() -> Path:
    repo_root = Path(__file__).resolve().parent.parent.parent
    ref_path = repo_root / "references" / "pet-presets.json"
    if ref_path.exists():
        return ref_path
    raise FileNotFoundError("pet-presets.json not found in references/")


def normalize_pet_category(cat: str) -> str:
    key = cat.strip()
    resolved = _PET_ALIASES.get(key) or _PET_ALIASES.get(key.lower())
    if not resolved:
        raise ValueError(
            f"Unknown pet category '{cat}'. Use one of: cat_boss (猫主子), dog_happy (快乐修勾), pet_meme (萌宠梗图), pet_festival (萌宠祝福)"
        )
    return resolved


@lru_cache(maxsize=2)
def load_pet_presets(path: Path | None = None) -> List[ExpressionItem]:
    """Load all 40 built-in real-pet photographic sticker presets."""
    p = path or get_default_pet_path()
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    items = [ExpressionItem(**raw) for raw in data]
    seen = set()
    for it in items:
        if it.id in seen:
            raise ValueError(f"Duplicate pet preset id: {it.id}")
        seen.add(it.id)
        it.captions.setdefault("zh-CN", it.caption)
    return items


def list_pet_presets(
    category: Optional[str] = None,
    path: Path | None = None,
) -> List[ExpressionItem]:
    items = list(load_pet_presets(path))
    if category:
        wanted = {
            normalize_pet_category(c)
            for c in category.replace("，", ",").split(",")
            if c.strip()
        }
        items = [it for it in items if it.category in wanted]
    return items


def plan_pet_expressions(
    count: int = 16,
    categories: Optional[Sequence[str]] = None,
    pet_ids: Optional[Sequence[str]] = None,
    path: Path | None = None,
) -> List[ExpressionItem]:
    """Select ``count`` real-pet presets across cat_boss / dog_happy / pet_meme / pet_festival."""
    all_items = load_pet_presets(path)
    by_id = {it.id: it for it in all_items}
    selected: List[ExpressionItem] = []

    for pid in pet_ids or []:
        if pid not in by_id:
            raise ValueError(f"Unknown pet preset id: {pid}")
        if by_id[pid] not in selected:
            selected.append(by_id[pid])

    if categories:
        wanted = [normalize_pet_category(c) for c in categories if c and c.strip()]
        pool = [it for it in all_items if it.category in wanted and it not in selected]
    else:
        pool = [it for it in all_items if it not in selected]

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


def build_pet_static_prompt(
    bible: CharacterBible,
    item: ExpressionItem,
    style: Optional[str] = None,
    text_layout: str = "caption",
) -> str:
    """Build a static real-pet sticker prompt preserving authentic fur, breed, and markings."""
    style_id = style or bible.render_style.style_id
    preset = resolve_style_preset(style_id)
    facts = ", ".join(bible.identity_facts) if bible.identity_facts else "exact same real pet as Reference Photo"
    comp_hint = composition_hint(text_layout)
    return (
        f"Create a photorealistic REAL-PET chat sticker (真宠实拍表情包: {PET_CATEGORY_LABELS.get(item.category, {}).get('zh', item.category)}). "
        f"{REAL_PET_HARD_LOCK} "
        f"Style ID: {preset.id} ({preset.display_name}). {preset.prompt_lock} "
        f"Pet identity lock: {facts}. "
        f"Pet pose & expression ({item.name_zh or item.caption}): {item.static_pose}. "
        f"Lighting: {preset.lighting}. "
        f"Composition: {comp_hint} Single cohesive pet cutout silhouette. {CLEAN_BACKGROUND_HARD_LOCK} "
        f"Negative constraints: {REAL_PET_NEGATIVE} {preset.negative_extra}"
    )


def build_pet_sprite_sheet_prompt(
    bible: CharacterBible,
    item: ExpressionItem,
    style: Optional[str] = None,
    text_layout: str = "caption",
) -> str:
    """Build a 2x2 4-frame action sprite sheet prompt for a real-pet animated sticker."""
    style_id = style or bible.render_style.style_id
    preset = resolve_style_preset(style_id)
    facts = ", ".join(bible.identity_facts) if bible.identity_facts else "exact same real pet as Reference Photo"
    poses = item.motion.keyframe_poses or [item.static_pose] * 4
    while len(poses) < 4:
        poses.append(poses[-1])
    return (
        f"Create a 2x2 ANIMATION SPRITE SHEET (4 equal quadrants: top-left=Frame 1, top-right=Frame 2, "
        f"bottom-left=Frame 3, bottom-right=Frame 4) for a REAL-PET animated sticker "
        f"({item.name_zh or item.caption}). "
        f"{REAL_PET_HARD_LOCK} "
        f"Style ID: {preset.id} ({preset.display_name}). {preset.prompt_lock} "
        f"Pet identity lock: {facts}. "
        f"Frame 1 (top-left): {poses[0]} "
        f"Frame 2 (top-right): {poses[1]} "
        f"Frame 3 (bottom-left): {poses[2]} "
        f"Frame 4 (bottom-right): {poses[3]} "
        f"Each quadrant must show the exact same real pet with consistent body scale and baseline alignment, "
        f"with clean empty separation along the horizontal and vertical centerlines. {CLEAN_BACKGROUND_HARD_LOCK} "
        f"Negative constraints: {REAL_PET_NEGATIVE} {preset.negative_extra}"
    )
