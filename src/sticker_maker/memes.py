"""One-shot meme maker (梗图) for Codex/CLI: user or AI image(s) + meme template → PNG / GIF."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Sequence

from PIL import Image

from .planner import MEME_CATEGORY_LABELS, get_item_by_id, load_meme_templates, localize_meme, resolve_text_spec
from .processing.alpha import apply_safe_margin
from .processing.compose import compose_sticker_frames
from .processing.encoders import save_animated, save_static
from .processing.gif_encoder import slice_sprite_sheet
from .schemas import ExpressionItem, JobConfig

# Friendly names → template ids (the user can say "Claude 梗图", "中国IP", "封号" ...)
MEME_ALIASES: Dict[str, str] = {
    "claude": "m01_ai_thinking",
    "ai-thinking": "m01_ai_thinking",
    "thinking": "m01_ai_thinking",
    "正在思考": "m01_ai_thinking",
    "思考中": "m01_ai_thinking",
    "china-ip": "m02_china_ip_blocked",
    "中国ip": "m02_china_ip_blocked",
    "禁止靠近": "m02_china_ip_blocked",
    "ban": "m03_ban_threat",
    "封号": "m03_ban_threat",
    "封你号": "m03_ban_threat",
    "再说话封你号": "m03_ban_threat",
    "banned": "m04_account_banned",
    "deep-thinking": "m05_deep_thinking",
    "深度思考": "m05_deep_thinking",
    "rate-limit": "m06_rate_limited",
    "cpu": "m07_cpu_burning",
    "refuse": "m08_refuse",
    "muted": "m09_muted",
    "禁言": "m09_muted",
    "404": "m12_404_brain",
    "deepfry": "m14_shock_deepfried",
    "震惊": "m14_shock_deepfried",
    "我悟了": "m15_enlightened",
    "裂开": "m16_cracked",
    "精神状态": "m17_mental_state",
    "包浆": "m18_patina",
    "黑白梗图": "m19_panda_head",
    "真人黑白": "m19_panda_head",
    "panda": "m19_panda_head",
    "熊猫头": "m19_panda_head",
    "impact": "m20_impact_classic",
}


def resolve_meme_id(name: str) -> str:
    key = name.strip()
    low = key.lower()
    if low in MEME_ALIASES:
        return MEME_ALIASES[low]
    if key in MEME_ALIASES:
        return MEME_ALIASES[key]
    ids = [m.id for m in load_meme_templates()]
    if key in ids:
        return key
    prefix = [i for i in ids if i.startswith(key) or i.split("_", 1)[0] == key]
    if len(prefix) == 1:
        return prefix[0]
    raise ValueError(f"Unknown meme template '{name}'. Run `wechat-sticker-maker memes` to list templates.")


def list_memes(language: str = "zh-CN", category: Optional[str] = None) -> List[ExpressionItem]:
    items = load_meme_templates()
    if category:
        cats = {c.strip() for c in category.split(",")}
        items = [m for m in items if m.category in cats]
    return items


def make_meme(
    template: str,
    images: Sequence[Path] = (),
    sprite_sheet: Optional[Path] = None,
    gif_output: Optional[Path] = None,
    png_output: Optional[Path] = None,
    language: str = "zh-CN",
    text: Optional[str] = None,
    style: str = "real-cutout",
    size: int = 240,
    frames: int = 8,
    frame_duration_ms: int = 150,
    color: Optional[str] = None,
    font_path: Optional[str] = None,
    master_size: int = 720,
) -> Dict[str, Path]:
    """Render a meme template over the given character image(s).

    - 1 image → static PNG; if the template has animated overlays (spinner, dots, glitch...) a GIF
      with overlay-only animation is also produced.
    - 2–8 images or a 2×2 sprite sheet (AI-drawn action frames) → full character animation GIF.
    """
    item = get_item_by_id(resolve_meme_id(template))
    job = JobConfig(
        job_id="meme", source_image="-", output_dir="-", language=language, style=style,
        platforms=["generic"], count=1, meme_texts={item.id: text} if text else None,
    )
    spec = resolve_text_spec(item, job)
    meme = localize_meme(item, job)
    from .planner import language_issues

    issues = language_issues([item], job)
    if issues:
        raise ValueError("Single-language check failed: " + "; ".join(issues))
    if meme is not None and color:
        meme = meme.model_copy(deep=True)
        for el in meme.elements:
            if el.type in ("spinner", "stamp", "prohibition", "big_text", "progress"):
                el.color = color

    raw: List[Image.Image] = []
    if sprite_sheet is not None:
        with Image.open(sprite_sheet) as sh:
            raw = slice_sprite_sheet(sh)
    for p in images:
        with Image.open(p) as im:
            raw.append(im.convert("RGBA"))
    if not raw:
        raise ValueError("Provide at least one image (--image) or a sprite sheet (--sprite-sheet)")

    canvas = (master_size, master_size)
    outputs: Dict[str, Path] = {}
    out_size = (size, size)

    if png_output is not None:
        static = compose_sticker_frames(raw[:1], spec, style, canvas, 1, font_path, meme=meme)[0]
        final = apply_safe_margin(static.resize(out_size, Image.Resampling.LANCZOS), 2)
        save_static(final, png_output, "png", 5_000_000)
        outputs["png"] = png_output

    overlay_animated = bool(meme and (any(e.animate != "none" for e in meme.elements) or {"glitch", "hue_cycle"} & set(meme.filters)))
    overlay_animated = overlay_animated or spec.bubble_animation in ("dots", "pop", "typewriter", "bob")
    if gif_output is not None and (len(raw) > 1 or overlay_animated):
        anim = compose_sticker_frames(raw, spec, style, canvas, frames, font_path, meme=meme)
        fitted = [apply_safe_margin(f.resize(out_size, Image.Resampling.LANCZOS), 2) for f in anim]
        save_animated(fitted, gif_output, "gif", frame_duration_ms, 5_000_000 if size > 240 else 500_000, loop=0)
        outputs["gif"] = gif_output
    return outputs


def meme_category_label(cat: str) -> str:
    lab = MEME_CATEGORY_LABELS.get(cat, {"zh": cat, "en": cat})
    return f"{lab['zh']} / {lab['en']}"
