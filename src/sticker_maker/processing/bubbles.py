"""Comic speech-bubble renderer for static and animated stickers.

Shapes: round, oval, thought (cloud + trailing dots), shout (spiky burst), rect (narration box),
heart, whisper (dashed outline). Bubbles auto-size to multilingual text, sit in an upper corner,
and point their tail at the character's head. Everything is resolution independent (sizes are
specified for a 240px canvas and scaled).
"""

from __future__ import annotations

import math
import zlib
from dataclasses import dataclass
from typing import List, Optional, Tuple

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from ..schemas import StylePreset
from ..styles import hex_to_rgba, resolve_style_preset
from .typography import BASE_CANVAS, TextLayout, draw_text_layout, fit_text

BUBBLE_SHAPES: Tuple[str, ...] = ("round", "oval", "thought", "shout", "rect", "heart", "whisper")

_SHAPE_DEFAULT_FILL = {
    "shout": "#FFF6C9",
    "heart": "#FFE3EC",
    "whisper": "#F6F6FF",
}

# (width factor, height factor, pad_x@240, pad_y@240, outer extra ratio)
_SHAPE_METRICS = {
    "round": (1.0, 1.0, 10.0, 7.0, 0.0),
    "rect": (1.0, 1.0, 9.0, 7.0, 0.0),
    "whisper": (1.0, 1.0, 10.0, 7.0, 0.0),
    "oval": (1.28, 1.42, 6.0, 5.0, 0.0),
    "thought": (1.26, 1.40, 7.0, 6.0, 0.10),
    "shout": (1.30, 1.46, 6.0, 5.0, 0.22),
    "heart": (1.62, 1.95, 4.0, 4.0, 0.0),
}

Box = Tuple[float, float, float, float]


@dataclass
class BubbleColors:
    fill: Tuple[int, int, int, int]
    outline: Tuple[int, int, int, int]
    text: Tuple[int, int, int, int]
    outline_px: float


@dataclass
class BubbleGeometry:
    canvas: Tuple[int, int]
    shape: str
    side: str  # left | right
    body: Box
    outer: Box
    text_layout: TextLayout
    text_center: Tuple[float, float]  # (center_x, top_y)


def bubble_colors(style: Optional[str | StylePreset], shape: str, canvas_w: int) -> BubbleColors:
    preset = style if isinstance(style, StylePreset) else resolve_style_preset(style or "real-cutout")
    b = preset.bubble
    fill = b.fill or _SHAPE_DEFAULT_FILL.get(shape, "#FFFFFF")
    outline = b.outline or preset.typography.text_color
    text = b.text_color or preset.typography.text_color
    return BubbleColors(
        hex_to_rgba(fill),
        hex_to_rgba(outline),
        hex_to_rgba(text),
        max(1.0, b.outline_width * canvas_w / BASE_CANVAS),
    )


def plan_bubble(
    canvas_size: Tuple[int, int],
    text: str,
    language: str = "zh-CN",
    shape: str = "round",
    side: str = "left",
    style: Optional[str | StylePreset] = None,
    font_path: Optional[str] = None,
    max_w_ratio: float = 0.58,
    max_h_ratio: float = 0.40,
) -> BubbleGeometry:
    """Fit text and compute the bubble body/outer boxes in the chosen upper corner."""
    if shape not in BUBBLE_SHAPES:
        shape = "round"
    preset = style if isinstance(style, StylePreset) else resolve_style_preset(style or "real-cutout")
    w, h = canvas_size
    s = w / BASE_CANVAS
    fw, fh, padx, pady, extra = _SHAPE_METRICS[shape]
    padx *= s
    pady *= s
    colors = bubble_colors(preset, shape, w)
    margin = 3.0 * s + colors.outline_px

    max_outer_w = w * max_w_ratio
    max_outer_h = h * max_h_ratio
    max_body_w = max_outer_w / (1.0 + 2 * extra)
    max_body_h = max_outer_h / (1.0 + 2 * extra)
    text_max_w = max(20.0, (max_body_w - 2 * padx) / fw)
    text_max_h = max(14.0, (max_body_h - 2 * pady) / fh)

    long_latin = len(text) > 12 and " " in text
    start = int(round(preset.bubble.font_size * s))
    single = None
    if "\n" not in text:
        single = fit_text(text, language, max_width=text_max_w, max_height=text_max_h, start_size=start,
                          min_size=max(int(9 * s), int(start * 0.72)), max_lines=1, user_font=font_path)
        if len(single.lines) != 1 or single.width > text_max_w + 1:
            single = None
    layout = single or fit_text(
        text,
        language,
        max_width=text_max_w,
        max_height=text_max_h,
        start_size=int(round(preset.bubble.font_size * s)),
        min_size=int(round(9 * s)),
        max_lines=4 if long_latin else 3,
        user_font=font_path,
    )

    body_w = max(60.0 * s, layout.width * fw + 2 * padx)
    body_h = max((46.0 if fw > 1.0 else 36.0) * s, layout.height * fh + 2 * pady)
    if shape == "heart":
        body_w = max(body_w, body_h * 1.08)
    body_w = min(body_w, max_body_w)
    body_h = min(body_h, max_body_h)

    ox = body_w * extra
    oy = body_h * extra
    outer_w = body_w + 2 * ox
    if side == "right":
        outer_x1 = w - margin
        outer_x0 = outer_x1 - outer_w
    else:
        outer_x0 = margin
        outer_x1 = outer_x0 + outer_w
    outer_y0 = margin
    outer_y1 = outer_y0 + body_h + 2 * oy
    body = (outer_x0 + ox, outer_y0 + oy, outer_x1 - ox, outer_y1 - oy)

    cx = (body[0] + body[2]) / 2.0
    if shape == "heart":
        text_top = body[1] + (body[3] - body[1]) * 0.40 - layout.height / 2.0
    else:
        text_top = (body[1] + body[3]) / 2.0 - layout.height / 2.0
    return BubbleGeometry(canvas_size, shape, side, body, (outer_x0, outer_y0, outer_x1, outer_y1), layout, (cx, text_top))


# ---------------------------------------------------------------------------
# Shape masks (drawn at 2x supersampling for anti-aliased edges)
# ---------------------------------------------------------------------------


def _heart_points(box: Box, n: int = 96) -> List[Tuple[float, float]]:
    x0, y0, x1, y1 = box
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        hx = 16 * math.sin(t) ** 3
        hy = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((hx, -hy))
    min_x = min(p[0] for p in pts)
    max_x = max(p[0] for p in pts)
    min_y = min(p[1] for p in pts)
    max_y = max(p[1] for p in pts)
    sx = (x1 - x0) / (max_x - min_x)
    sy = (y1 - y0) / (max_y - min_y)
    return [(x0 + (px - min_x) * sx, y0 + (py - min_y) * sy) for px, py in pts]


def _tail_geometry(geom: BubbleGeometry, target: Tuple[float, float], scale: float) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
    x0, y0, x1, y1 = geom.body
    bw, bh = x1 - x0, y1 - y0
    cx = (x0 + x1) / 2.0
    tx, ty = target
    bx = min(max(cx + (tx - cx) * 0.45, x0 + bw * 0.22), x1 - bw * 0.22)
    inset = min(bh * 0.28, 10 * scale) if geom.shape in ("round", "rect", "whisper") else bh * 0.18
    by = y1 - inset
    dx, dy = tx - bx, ty - by
    dist = math.hypot(dx, dy) or 1.0
    ux, uy = dx / dist, dy / dist
    if uy < 0.35:  # always point downward-ish toward the character
        uy = 0.35
        ux = math.copysign(math.sqrt(1 - uy * uy), ux if ux != 0 else (1 if geom.side == "left" else -1))
    length = min((y1 - by + 15 * scale) / uy, 42 * scale)
    tip = (bx + ux * length, by + uy * length)
    return (bx, by), (ux, uy), tip


def _draw_shape(draw: ImageDraw.ImageDraw, geom: BubbleGeometry, k: float, target: Optional[Tuple[float, float]], scale: float) -> None:
    x0, y0, x1, y1 = (v * k for v in geom.body)
    bw, bh = x1 - x0, y1 - y0
    shape = geom.shape
    if shape in ("round", "whisper"):
        draw.rounded_rectangle([x0, y0, x1, y1], radius=min(bh / 2.0, 20 * scale * k), fill=255)
    elif shape == "rect":
        draw.rounded_rectangle([x0, y0, x1, y1], radius=3 * scale * k, fill=255)
    elif shape == "oval":
        draw.ellipse([x0, y0, x1, y1], fill=255)
    elif shape == "thought":
        draw.ellipse([x0, y0, x1, y1], fill=255)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rx, ry = bw / 2, bh / 2
        r = 0.17 * min(bw, bh)
        n = max(9, int(math.pi * (rx + ry) / (r * 1.25)))
        for i in range(n):
            a = 2 * math.pi * i / n
            px, py = cx + rx * math.cos(a) * 0.96, cy + ry * math.sin(a) * 0.96
            draw.ellipse([px - r, py - r, px + r, py + r], fill=255)
    elif shape == "shout":
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rx, ry = bw / 2, bh / 2
        n = 18
        seed = zlib.crc32(geom.text_layout.lines[0].text.encode("utf-8")) if geom.text_layout.lines else 7
        pts = []
        for i in range(2 * n):
            a = math.pi * i / n
            if i % 2 == 0:
                jitter = 1.20 + 0.10 * (((seed >> (i % 24)) & 3) / 3.0)
                f = jitter
            else:
                f = 0.96
            pts.append((cx + rx * f * math.cos(a), cy + ry * f * math.sin(a)))
        draw.polygon(pts, fill=255)
        draw.ellipse([x0, y0, x1, y1], fill=255)
    elif shape == "heart":
        draw.polygon(_heart_points((x0, y0, x1, y1)), fill=255)

    if target is None or shape in ("heart",):
        return
    (bx, by), (ux, uy), tip = _tail_geometry(geom, target, scale)
    if shape == "thought":
        _, _, _, by1 = geom.body
        for frac, rad in ((0.40, 5.5), (0.70, 3.8), (0.95, 2.4)):
            px = bx + (tip[0] - bx) * frac
            py = by1 + (tip[1] - by1) * frac
            r = rad * scale * k
            draw.ellipse([px * k - r, py * k - r, px * k + r, py * k + r], fill=255)
        return
    half = (6.5 if shape == "shout" else 8.0) * scale
    px_, py_ = -uy, ux
    poly = [
        ((bx + px_ * half) * k, (by + py_ * half) * k),
        ((bx - px_ * half) * k, (by - py_ * half) * k),
        (tip[0] * k, tip[1] * k),
    ]
    draw.polygon(poly, fill=255)


def render_bubble(
    geom: BubbleGeometry,
    tail_target: Optional[Tuple[float, float]] = None,
    style: Optional[str | StylePreset] = None,
    max_chars: Optional[int] = None,
) -> Image.Image:
    """Render the bubble (shape + outline + text) into a transparent canvas-sized RGBA layer."""
    w, h = geom.canvas
    s = w / BASE_CANVAS
    colors = bubble_colors(style, geom.shape, w)
    k = 2  # supersampling factor

    mask2 = Image.new("L", (w * k, h * k), 0)
    _draw_shape(ImageDraw.Draw(mask2), geom, k, tail_target, s)

    # Fast anti-aliased dilation for the outline: gaussian blur + soft threshold
    sigma = max(0.8, colors.outline_px * k / 2.0)
    blurred = mask2.filter(ImageFilter.GaussianBlur(radius=sigma))
    outline2 = blurred.point(lambda v: 0 if v <= 2 else (255 if v >= 14 else int((v - 2) * 255 / 12)))

    fill_mask = mask2.resize((w, h), Image.Resampling.BOX)
    outline_mask = outline2.resize((w, h), Image.Resampling.BOX)

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if geom.shape == "whisper":
        ring = ImageChops.subtract(outline_mask, fill_mask)
        dashes = Image.new("L", (w, h), 0)
        dd = ImageDraw.Draw(dashes)
        step = max(4, int(7 * s))
        for off in range(-h, w + h, step * 2):
            dd.line([(off, 0), (off + h, h)], fill=255, width=step)
        ring = ImageChops.multiply(ring, dashes)
        layer.paste(colors.outline[:3] + (255,), (0, 0, w, h), ring)
    else:
        layer.paste(colors.outline[:3] + (255,), (0, 0, w, h), outline_mask)
    layer.paste(colors.fill[:3] + (255,), (0, 0, w, h), fill_mask)

    cx, top = geom.text_center
    draw_text_layout(layer, geom.text_layout, cx, top, colors.text, None, max_chars=max_chars)
    return layer


def composite_bubble(frame: Image.Image, layer: Image.Image, geom: BubbleGeometry, scale: float = 1.0, dy: float = 0.0) -> Image.Image:
    """Alpha-composite a bubble layer onto a frame, optionally scaled about the bubble centre (pop-in)."""
    base = frame.convert("RGBA")
    if abs(scale - 1.0) < 1e-3 and abs(dy) < 0.5:
        return Image.alpha_composite(base, layer)
    w, h = layer.size
    ox0, oy0, ox1, oy1 = geom.outer
    pad = int(60 * w / BASE_CANVAS)
    crop_box = (
        max(0, int(ox0) - pad),
        max(0, int(oy0) - pad),
        min(w, int(ox1) + pad),
        min(h, int(oy1) + pad),
    )
    crop = layer.crop(crop_box)
    cw, ch = crop.size
    nw, nh = max(1, int(cw * scale)), max(1, int(ch * scale))
    scaled = crop.resize((nw, nh), Image.Resampling.LANCZOS)
    bcx = (geom.body[0] + geom.body[2]) / 2.0
    bcy = (geom.body[1] + geom.body[3]) / 2.0
    rel_x = (bcx - crop_box[0]) * scale
    rel_y = (bcy - crop_box[1]) * scale
    px = int(round(bcx - rel_x))
    py = int(round(bcy - rel_y + dy))
    tmp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    tmp.paste(scaled, (px, py), scaled)
    return Image.alpha_composite(base, tmp)


def bubble_animation_params(animation: str, idx: int, total: int) -> Tuple[float, float, Optional[float]]:
    """Return (scale, dy_ratio, reveal_fraction) for a frame of a bubble animation."""
    if animation == "pop":
        curve = [0.55, 1.10, 1.0]
        return (curve[idx] if idx < len(curve) else 1.0), 0.0, None
    if animation == "bob":
        return 1.0, math.sin(2 * math.pi * idx / max(1, total)) * 0.006, None
    if animation == "typewriter":
        reveal_frames = max(1, int(total * 0.6))
        return 1.0, 0.0, min(1.0, (idx + 1) / float(reveal_frames))
    return 1.0, 0.0, None
