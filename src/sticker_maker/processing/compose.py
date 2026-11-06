"""Sticker frame composition: place AI-drawn character keyframes into the canvas, reserve space
for captions / speech bubbles, add die-cut border, and overlay multilingual text per frame.

Python never re-draws or warps the character: AI keyframes are only cleaned, uniformly
scaled, and registered on a stable lower-torso anchor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from PIL import Image

from ..schemas import MemeSpec, StylePreset, TextSpec
from ..styles import resolve_style_preset
from .alpha import apply_die_cut_border, remove_matte_background
from .bubbles import (
    BubbleGeometry,
    bubble_animation_params,
    composite_bubble,
    plan_bubble,
    render_bubble,
)
from .meme_fx import MemeRenderer, reserve_top_ratio
from .typography import BASE_CANVAS, add_caption_to_image


@dataclass
class CharRegion:
    max_w: float
    max_h: float
    center_x: float
    bottom_y: float


def default_region(canvas: Tuple[int, int], has_caption: bool = True) -> CharRegion:
    w, h = canvas
    if has_caption:
        return CharRegion(w * 0.78, h * 0.74, w * 0.5, h * 0.81)
    return CharRegion(w * 0.90, h * 0.90, w * 0.5, h * 0.97)


def compute_char_region(
    canvas: Tuple[int, int],
    spec: Optional[TextSpec],
    bubble: Optional[BubbleGeometry] = None,
) -> CharRegion:
    w, h = canvas
    has_caption = bool(spec and spec.has_caption)
    region = default_region(canvas, has_caption)
    if bubble is None:
        return region
    ox0, oy0, ox1, oy1 = bubble.outer
    top_limit = oy1 - h * 0.10
    max_h = max(h * 0.50, min(region.max_h, region.bottom_y - top_limit))
    if bubble.side == "left":
        shift = min(max(0.0, (ox1 - w * 0.30) * 0.35), w * 0.12)
    else:
        shift = -min(max(0.0, (w * 0.70 - ox0) * 0.35), w * 0.12)
    return CharRegion(min(region.max_w, w * 0.82), max_h, w * 0.5 + shift, region.bottom_y)


def _torso_center_x(alpha: Image.Image) -> float:
    cw, ch = alpha.size
    if cw <= 1 or ch <= 1:
        return cw / 2.0
    y0 = int(ch * 0.65)
    xs: List[int] = []
    step = max(1, (ch - y0) // 12)
    px = alpha.load()
    for y in range(y0, ch, step):
        for x in range(cw):
            if px[x, y] > 128:
                xs.append(x)
    return sum(xs) / float(len(xs)) if len(xs) >= 6 else cw / 2.0


def crop_characters(raw_frames: Sequence[Image.Image], clean: bool = True) -> List[Image.Image]:
    """Remove matte background (optional) and crop every keyframe to its alpha bounding box."""
    crops: List[Image.Image] = []
    for frame in raw_frames:
        rgba = frame.convert("RGBA")
        if clean:
            rgba = remove_matte_background(rgba)
        bbox = rgba.getchannel("A").getbbox()
        crops.append(rgba.crop(bbox) if bbox else Image.new("RGBA", (8, 8), (0, 0, 0, 0)))
    return crops


def auto_bubble_side(crop: Image.Image) -> str:
    """Put the bubble on the side opposite to a raised hand / extended limb."""
    cw = crop.width
    torso = _torso_center_x(crop.getchannel("A"))
    offset = (cw / 2.0 - torso) / float(max(1, cw))
    if offset > 0.04:
        return "left"  # silhouette extends to the right → bubble on the left
    if offset < -0.04:
        return "right"
    return "left"


def place_characters(
    crops: Sequence[Image.Image],
    canvas: Tuple[int, int],
    region: CharRegion,
    die_cut_border_px: int = 0,
) -> List[Image.Image]:
    """Uniformly scale (based on frame 0) and register crops on a fixed lower-torso anchor."""
    tw, th = canvas
    s = tw / BASE_CANVAS
    if not crops:
        return []
    ref = crops[0]
    base_scale = min(region.max_w / float(max(1, ref.width)), region.max_h / float(max(1, ref.height)))
    target_h = max(16, int(round(ref.height * base_scale)))
    border_px = int(round(die_cut_border_px * s))

    placed: List[Image.Image] = []
    for crop in crops:
        cw, ch = crop.size
        scale = target_h / float(max(1, ch))
        if cw * scale > tw * 0.92:
            scale = (tw * 0.92) / float(cw)
        nw, nh = max(1, int(round(cw * scale))), max(1, int(round(ch * scale)))
        scaled = crop.resize((nw, nh), Image.Resampling.LANCZOS)
        torso = _torso_center_x(scaled.getchannel("A"))
        edge = int(4 * s)
        px = int(round(region.center_x - torso))
        px = max(edge, min(tw - nw - edge, px))
        py = max(edge, int(round(region.bottom_y - nh)))
        canvas_img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        canvas_img.paste(scaled, (px, py), scaled)
        placed.append(apply_die_cut_border(canvas_img, border_px=border_px) if border_px > 0 else canvas_img)
    return placed


def expand_loop(frames: Sequence[Image.Image], target_frames: int) -> List[Image.Image]:
    """Expand N unique keyframes to target_frames with a smooth ping-pong cycle."""
    n = len(frames)
    if n == 0:
        return []
    if n == 1:
        return [frames[0].copy() for _ in range(max(1, target_frames))]
    if target_frames <= n:
        return [frames[i].copy() for i in range(target_frames)]
    cycle = list(range(n)) + list(range(n - 2, 0, -1))
    return [frames[cycle[i % len(cycle)]].copy() for i in range(target_frames)]


def _character_head_point(frame: Image.Image) -> Tuple[float, float]:
    """Head crown centre: alpha centroid of the top 22% of the silhouette (ignores raised hands lower down)."""
    alpha = frame.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        return frame.width / 2.0, frame.height / 2.0
    x0, y0, x1, y1 = bbox
    band = alpha.crop((x0, y0, x1, y0 + max(2, int((y1 - y0) * 0.22))))
    px = band.load()
    bw, bh = band.size
    xs = 0.0
    n = 0
    step = max(1, bw // 160)
    for yy in range(0, bh, max(1, bh // 24)):
        for xx in range(0, bw, step):
            if px[xx, yy] > 128:
                xs += xx
                n += 1
    cx = x0 + xs / n if n else (x0 + x1) / 2.0
    return cx, y0 + (y1 - y0) * 0.20


def compose_sticker_frames(
    raw_frames: Sequence[Image.Image],
    spec: Optional[TextSpec],
    style: Optional[str | StylePreset] = None,
    canvas_size: Tuple[int, int] = (720, 720),
    target_frames: int = 1,
    font_path: Optional[str] = None,
    clean: bool = True,
    die_cut_border_px: Optional[int] = None,
    meme: Optional[MemeSpec] = None,
) -> List[Image.Image]:
    """Full composition for one sticker: AI keyframes → layout → border → meme background →
    caption → bubble → meme overlays → meme filters.

    Returns ``target_frames`` RGBA frames (1 for static stickers).
    """
    preset = style if isinstance(style, StylePreset) else resolve_style_preset(style or "real-cutout")
    border = preset.die_cut_border_px if die_cut_border_px is None else die_cut_border_px
    crops = crop_characters(raw_frames, clean=clean)
    if not crops:
        raise ValueError("No keyframes supplied")

    bubble_geom: Optional[BubbleGeometry] = None
    bubble_text = spec.bubble_text if spec is not None else ""
    if spec is not None and spec.has_bubble and spec.bubble_animation == "dots":
        bubble_text = bubble_text.rstrip(".。…") + "..."
    if spec is not None and spec.has_bubble:
        side = {"top-left": "left", "top-right": "right"}.get(spec.bubble_position) or auto_bubble_side(crops[0])
        bubble_geom = plan_bubble(
            canvas_size,
            bubble_text,
            spec.language,
            spec.bubble_shape,
            side,
            preset,
            font_path,
            max_w_ratio=0.56 if spec.has_caption else 0.60,
            max_h_ratio=0.34 if spec.has_caption else 0.40,
        )

    region = compute_char_region(canvas_size, spec, bubble_geom)
    reserve = reserve_top_ratio(meme)
    if reserve > 0:
        h = canvas_size[1]
        if not (spec and spec.has_caption):
            region.bottom_y = h * 0.98
        region.max_h = min(region.max_h, region.bottom_y - h * (reserve + 0.02))
    keyframes = place_characters(crops, canvas_size, region, border)
    frames = expand_loop(keyframes, target_frames)

    # Static text overlay rendered once (caption is identical on every frame)
    caption_layer: Optional[Image.Image] = None
    if spec is not None and spec.has_caption:
        caption_layer = add_caption_to_image(
            Image.new("RGBA", canvas_size, (0, 0, 0, 0)),
            spec.caption,
            font_path=font_path,
            style=preset,
            language=spec.language,
        )

    bubble_cache: dict = {}
    tail_target = _character_head_point(keyframes[0]) if bubble_geom is not None else None
    total = len(frames)
    meme_r: Optional[MemeRenderer] = None
    if meme is not None and (meme.elements or meme.filters or meme.background):
        bbox = keyframes[0].getchannel("A").getbbox() or (0, 0, canvas_size[0], canvas_size[1])
        meme_r = MemeRenderer(
            meme, canvas_size, _character_head_point(keyframes[0]), bbox,
            spec.language if spec else "zh-CN", font_path,
            caption_safe=bool(spec and spec.has_caption),
        )
    out: List[Image.Image] = []
    for idx, frame in enumerate(frames):
        if meme_r is not None:
            back = meme_r.back(idx, total)
            if back is not None:
                frame = Image.alpha_composite(back, frame)
        if caption_layer is not None:
            frame = Image.alpha_composite(frame, caption_layer)
        if bubble_geom is not None:
            anim = spec.bubble_animation if total > 1 else "none"
            scale, dy_ratio, reveal = bubble_animation_params(anim, idx, total)
            max_chars = None
            n_chars = sum(len(l.text) for l in bubble_geom.text_layout.lines)
            if reveal is not None:
                max_chars = max(1, int(round(n_chars * reveal)))
            elif anim == "dots":
                max_chars = n_chars - 3 + (idx % 3) + 1
            key = max_chars
            if key not in bubble_cache:
                bubble_cache[key] = render_bubble(bubble_geom, tail_target, preset, max_chars=max_chars)
            frame = composite_bubble(frame, bubble_cache[key], bubble_geom, scale=scale, dy=dy_ratio * canvas_size[1])
        if meme_r is not None:
            frame = meme_r.front(frame, idx, total)
            frame = meme_r.finish(frame, idx, total)
        out.append(frame)
    return out
