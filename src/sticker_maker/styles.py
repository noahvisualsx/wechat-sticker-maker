"""Pluggable style preset catalog and custom style loader."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Dict, List, Tuple

from .schemas import StylePreset, TypographyStyle


def get_default_styles_path() -> Path:
    repo_root = Path(__file__).resolve().parent.parent.parent
    ref_path = repo_root / "references" / "style-presets.json"
    if ref_path.exists():
        return ref_path
    raise FileNotFoundError("style-presets.json not found in references/")


@lru_cache(maxsize=4)
def load_style_presets(styles_path: Path | None = None) -> Dict[str, StylePreset]:
    """Load and validate all built-in style presets from references/style-presets.json."""
    path = styles_path or get_default_styles_path()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    presets: Dict[str, StylePreset] = {}
    for raw in data:
        preset = StylePreset(**raw)
        if preset.id in presets:
            raise ValueError(f"Duplicate style preset ID: {preset.id}")
        presets[preset.id] = preset
    return presets


STYLE_REGIONS = ("通用", "韩系", "日系", "中式")

_REGION_ALIASES = {
    "通用": "通用", "general": "通用", "common": "通用", "basic": "通用",
    "韩系": "韩系", "韩": "韩系", "韩国": "韩系", "kr": "韩系", "ko": "韩系", "korea": "韩系", "korean": "韩系",
    "日系": "日系", "日": "日系", "日本": "日系", "jp": "日系", "ja": "日系", "japan": "日系", "japanese": "日系",
    "中式": "中式", "中": "中式", "中系": "中式", "国风": "中式", "中国": "中式", "cn": "中式", "zh": "中式",
    "china": "中式", "chinese": "中式",
}


def normalize_region(region: str) -> str:
    """Map a region name / alias (韩系, kr, japanese, 国风 ...) to one of STYLE_REGIONS."""
    key = region.strip()
    resolved = _REGION_ALIASES.get(key) or _REGION_ALIASES.get(key.lower())
    if not resolved:
        raise ValueError(f"Unknown style region '{region}'. Use one of: {', '.join(STYLE_REGIONS)}")
    return resolved


def list_style_presets(styles_path: Path | None = None, region: str | None = None) -> List[StylePreset]:
    """Return ordered list of built-in style presets, optionally filtered by region (韩系/日系/中式/通用)."""
    presets = list(load_style_presets(styles_path).values())
    if region:
        wanted = {normalize_region(r) for r in region.replace("，", ",").split(",") if r.strip()}
        presets = [p for p in presets if p.region in wanted]
    return presets


DEFAULT_STYLE_ID = "real-cutout"


def resolve_style_preset(style_name_or_path: str = DEFAULT_STYLE_ID) -> StylePreset:
    """Resolve a real-person style preset by ID, custom JSON file path, or real-person fallback."""
    if not style_name_or_path:
        style_name_or_path = DEFAULT_STYLE_ID

    # 1. Check built-in real-person catalog
    presets = load_style_presets()
    if style_name_or_path in presets:
        return presets[style_name_or_path]

    # 2. Check if user passed a path to a custom style JSON file
    candidate_path = Path(style_name_or_path)
    if candidate_path.suffix.lower() == ".json" and candidate_path.exists():
        with candidate_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        return StylePreset(**raw)

    # 3. Dynamic fallback for custom free-form real-person style strings
    return StylePreset(
        id=style_name_or_path,
        display_name=style_name_or_path,
        category="真人专属",
        description=f"用户自定义真人贴纸风格：{style_name_or_path}",
        prompt_lock=(
            f"Photorealistic real-person portrait sticker cutout ({style_name_or_path}) of the exact same person "
            f"from the reference photo, preserving true facial bone structure, real skin texture, hairstyle, and outfit."
        ),
        negative_extra="NEVER cartoonize, NEVER turn into 2D anime, flat illustration, or 3D doll.",
        outline="die-cut-white-border",
        lighting="studio-portrait",
        default_palette=["#FFE5D9", "#F4A261", "#3D405B"],
        banner_bg="#F8F9FA",
        die_cut_border_px=4,
        prefer_keyframes=True,
        typography=TypographyStyle(),
    )


def hex_to_rgba(hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    """Convert a #RRGGBB or #RGB hex string into an (R, G, B, A) tuple."""
    clean = hex_color.strip().lstrip("#")
    if len(clean) == 3:
        clean = "".join(c * 2 for c in clean)
    if len(clean) != 6:
        return (40, 40, 40, alpha)
    try:
        r = int(clean[0:2], 16)
        g = int(clean[2:4], 16)
        b = int(clean[4:6], 16)
        return (r, g, b, alpha)
    except ValueError:
        return (40, 40, 40, alpha)


REGION_DEFAULT_LANGUAGE = {
    "韩系": "ko",
    "日系": "ja",
    "中式": "zh-CN",
    "通用": "en",
}


def infer_language_for_style(style_name_or_path: str = DEFAULT_STYLE_ID) -> str:
    """Return the natural single language associated with a style's region (ko/ja/zh-CN/en)."""
    presets = load_style_presets()
    if style_name_or_path in presets:
        return REGION_DEFAULT_LANGUAGE.get(presets[style_name_or_path].region, "zh-CN")
    lower = (style_name_or_path or "").lower()
    if lower.startswith("kr-"):
        return "ko"
    if lower.startswith("jp-"):
        return "ja"
    if lower.startswith("cn-"):
        return "zh-CN"
    preset = resolve_style_preset(style_name_or_path)
    return REGION_DEFAULT_LANGUAGE.get(preset.region, "zh-CN")
