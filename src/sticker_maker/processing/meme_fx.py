"""Meme / abstract-image overlay engine (梗图 · 抽象图).

Deterministic, multilingual overlays drawn on top of (or behind) the AI-drawn character:
AI thinking spinner, prohibition sign, caution tape, ban stamp, system dialog, IM chat bubble,
group notice, label chip, progress bar, glitch big text, classic Impact top/bottom text,
top caption bar, speed lines, light rays, glass cracks, smoke, battery, typing indicator,
read receipt, sparkles, question marks, mute badge — plus frame filters such as deep-fry,
glitch, 电子包浆 (patina), grayscale, hue cycle, vignette, high contrast and posterize.

The character's own motion always comes from AI keyframes; these overlays are props/UI/effects.
"""

from __future__ import annotations

import io
import math
import random
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from ..i18n import get_language_info, resolve_localized_text
from ..schemas import MemeElement, MemeSpec
from ..styles import hex_to_rgba
from .typography import BASE_CANVAS, draw_text_layout, fit_text

RGBA = Tuple[int, int, int, int]
Box = Tuple[float, float, float, float]

_IMPACT_CANDIDATES = (
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/Library/Fonts/Impact.ttf",
    "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
    "C:\\Windows\\Fonts\\impact.ttf",
)


@lru_cache(maxsize=1)
def impact_font_path() -> Optional[str]:
    for p in _IMPACT_CANDIDATES:
        if Path(p).exists():
            return p
    return None


def element_text(el: MemeElement, field: str, language: str) -> str:
    """Element text in exactly the sticker language (never falls back to another language)."""
    texts = getattr(el, field) or {}
    text, exact = resolve_localized_text(texts, language, allow_english_fallback=False)
    if not exact:
        return ""
    if el.value is not None and "{value}" in text:
        v = el.value
        text = text.replace("{value}", str(int(v)) if float(v).is_integer() else f"{v:g}")
    return text


def _color(el: MemeElement, default: str) -> RGBA:
    return hex_to_rgba(el.color or default)


def _draw_text_box(
    layer: Image.Image,
    text: str,
    language: str,
    box: Box,
    fill: RGBA,
    stroke: Optional[RGBA] = None,
    stroke_ratio: float = 0.0,
    max_lines: int = 2,
    start_ratio: float = 0.8,
    user_font: Optional[str] = None,
    align: str = "center",
) -> Tuple[int, int, int, int]:
    x0, y0, x1, y1 = box
    if not text or x1 - x0 < 4 or y1 - y0 < 4:
        return (int(x0), int(y0), int(x0), int(y0))
    s = layer.width / BASE_CANVAS
    layout = fit_text(
        text, language, max_width=x1 - x0, max_height=y1 - y0,
        start_size=max(8, int((y1 - y0) * start_ratio)),
        min_size=max(7, int(7 * s)), max_lines=max_lines, user_font=user_font, stroke_ratio=stroke_ratio,
    )
    top = y0 + ((y1 - y0) - layout.height) / 2.0
    return draw_text_layout(layer, layout, (x0 + x1) / 2.0, top, fill, stroke, align=align, left_x=x0)


def _anchor_point(position: str, w: int, h: int, head: Tuple[float, float], char_box: Box) -> Tuple[float, float]:
    cx0, cy0, cx1, cy1 = char_box
    return {
        "head": (head[0], cy0 + (cy1 - cy0) * 0.06),
        "top": (w * 0.5, h * 0.13),
        "bottom": (w * 0.5, h * 0.84),
        "center": (w * 0.5, h * 0.5),
        "top-left": (w * 0.20, h * 0.17),
        "top-right": (w * 0.80, h * 0.17),
        "bottom-left": (w * 0.22, h * 0.80),
        "bottom-right": (w * 0.78, h * 0.80),
        "cross": (w * 0.5, h * 0.55),
        "full": (w * 0.5, h * 0.5),
    }.get(position, (w * 0.5, h * 0.13))


def _rotate_layer(layer: Image.Image, angle: float, center: Tuple[float, float]) -> Image.Image:
    if abs(angle) < 0.01:
        return layer
    return layer.rotate(angle, resample=Image.Resampling.BICUBIC, center=center)


def _scale_layer(layer: Image.Image, scale: float, center: Tuple[float, float]) -> Image.Image:
    if abs(scale - 1.0) < 1e-3:
        return layer
    w, h = layer.size
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    scaled = layer.resize((nw, nh), Image.Resampling.BICUBIC)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(scaled, (int(round(center[0] - center[0] * scale)), int(round(center[1] - center[1] * scale))), scaled)
    return out


def _phase(idx: int, total: int) -> float:
    return 2 * math.pi * idx / float(max(1, total))


# ---------------------------------------------------------------------------
# Element renderers: each returns an RGBA layer (canvas size)
# ---------------------------------------------------------------------------


def _spinner(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cx, cy = _anchor_point(el.position, w, h, head, char_box)
    r = 20 * s * el.size
    n = 12
    step = 360.0 / n * 2
    rot = (idx / float(max(1, total))) * step if el.animate == "rotate" else 0.0
    color = _color(el, "#5B8DEF")
    d = ImageDraw.Draw(layer)
    for pass_i, (col, extra) in enumerate((((255, 255, 255, 235), 2.6 * s), (color, 0.0))):
        for i in range(n):
            a = math.radians(rot + i * 360.0 / n)
            length = r if i % 2 == 0 else r * 0.72
            r0 = r * 0.10
            x0, y0 = cx + math.cos(a) * r0, cy + math.sin(a) * r0
            x1, y1 = cx + math.cos(a) * length, cy + math.sin(a) * length
            width = max(2, int(3.6 * s + extra))
            d.line([(x0, y0), (x1, y1)], fill=col, width=width)
            rr = width / 2.0
            d.ellipse([x1 - rr, y1 - rr, x1 + rr, y1 + rr], fill=col)
    return layer


def _prohibition(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cx, cy = _anchor_point(el.position, w, h, head, char_box)
    r = 30 * s * el.size
    red = _color(el, "#E02424")
    d = ImageDraw.Draw(layer)
    ring = 6.5 * s * el.size
    d.ellipse([cx - r - 2 * s, cy - r - 2 * s, cx + r + 2 * s, cy + r + 2 * s], fill=(255, 255, 255, 255))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 240), outline=red, width=int(ring))
    a = math.radians(45)
    inner = r - ring / 2
    d.line(
        [(cx - math.cos(a) * inner, cy - math.sin(a) * inner), (cx + math.cos(a) * inner, cy + math.sin(a) * inner)],
        fill=red, width=int(ring),
    )
    text = element_text(el, "text", language)
    if text:
        _draw_text_box(layer, text, language, (cx - r * 2.2, cy + r + 2 * s, cx + r * 2.2, cy + r + 30 * s * el.size),
                       red, (255, 255, 255, 255), 0.14, max_lines=2, user_font=font)
    if el.animate == "pulse":
        layer = _scale_layer(layer, 1.0 + 0.08 * math.sin(_phase(idx, total)), (cx, cy))
    return layer


def _hazard_tape(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    band_h = int(30 * s * el.size)
    tape = Image.new("RGBA", (int(w * 1.6), band_h), (0, 0, 0, 0))
    td = ImageDraw.Draw(tape)
    yellow = _color(el, "#FFD21F")
    if el.animate == "flash" and idx % 2 == 1:
        yellow = tuple(min(255, int(c * 0.82)) if i < 3 else c for i, c in enumerate(yellow))  # type: ignore[assignment]
    td.rectangle([0, 0, tape.width, band_h], fill=yellow)
    stripe_h = max(3, int(band_h * 0.16))
    step = max(6, int(10 * s))
    for edge_y in (0, band_h - stripe_h):
        for x in range(-band_h, tape.width + band_h, step * 2):
            td.polygon([(x, edge_y + stripe_h), (x + step, edge_y + stripe_h), (x + step + stripe_h, edge_y), (x + stripe_h, edge_y)], fill=(20, 20, 20, 255))
    text = element_text(el, "text", language)
    if text:
        margin = int(tape.width * 0.19)
        _draw_text_box(tape, text, language, (margin, stripe_h, tape.width - margin, band_h - stripe_h),
                       (15, 15, 15, 255), None, 0.0, max_lines=1, start_ratio=0.95, user_font=font)
    angle = el.angle if el.angle else (-7.0 if el.position == "cross" else -3.0)
    rotated = tape.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    cy = {"top": h * 0.12, "bottom": h * 0.86, "cross": h * 0.55, "center": h * 0.5}.get(el.position, h * 0.86)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.paste(rotated, (int(w / 2 - rotated.width / 2), int(cy - rotated.height / 2)), rotated)
    return layer


def _grunge_mask(size: Tuple[int, int], seed: int, density: float = 0.10) -> Image.Image:
    rnd = random.Random(seed)
    mask = Image.new("L", size, 255)
    d = ImageDraw.Draw(mask)
    w, h = size
    for _ in range(int(w * h * density / 40)):
        x, y = rnd.randrange(w), rnd.randrange(h)
        r = rnd.uniform(0.6, 2.4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=0)
    return mask


def _stamp(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    text = element_text(el, "text", language) or "BANNED"
    red = _color(el, "#D7263D")
    sw, sh = int(w * 0.50 * el.size), int(h * 0.20 * el.size)
    stamp = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(stamp)
    bw = max(3, int(3.4 * s * el.size))
    d.rounded_rectangle([bw, bw, sw - bw, sh - bw], radius=int(8 * s), outline=red, width=bw)
    d.rounded_rectangle([bw * 2.4, bw * 2.4, sw - bw * 2.4, sh - bw * 2.4], radius=int(5 * s), outline=red, width=max(1, bw // 2))
    _draw_text_box(stamp, text, language, (bw * 3.8, bw * 3.4, sw - bw * 3.8, sh - bw * 3.4), red, None, 0.0, max_lines=1, start_ratio=1.0, user_font=font)
    stamp.putalpha(ImageChops.multiply(stamp.getchannel("A"), _grunge_mask(stamp.size, 1234)))
    angle = el.angle if el.angle else -14.0
    rotated = stamp.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    cx, cy = _anchor_point(el.position if el.position != "top" else "center", w, h, head, char_box)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.paste(rotated, (int(cx - rotated.width / 2), int(cy - rotated.height / 2)), rotated)
    if el.animate == "slam" and total > 1:
        curve = [2.0, 1.35, 0.94, 1.0]
        sc = curve[idx] if idx < len(curve) else 1.0
        layer = _scale_layer(layer, sc, (cx, cy))
        if idx == 0:
            layer.putalpha(layer.getchannel("A").point(lambda v: int(v * 0.55)))
    return layer


def _icon(d: ImageDraw.ImageDraw, kind: str, cx: float, cy: float, r: float, s: float) -> None:
    if kind == "warning":
        d.polygon([(cx, cy - r), (cx + r * 1.05, cy + r * 0.85), (cx - r * 1.05, cy + r * 0.85)], fill=(255, 196, 0, 255))
        d.line([(cx, cy - r * 0.35), (cx, cy + r * 0.30)], fill=(30, 30, 30, 255), width=max(2, int(r * 0.22)))
        d.ellipse([cx - r * 0.11, cy + r * 0.48, cx + r * 0.11, cy + r * 0.70], fill=(30, 30, 30, 255))
    elif kind in ("error", "ban"):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(229, 57, 53, 255))
        if kind == "error":
            k = r * 0.45
            d.line([(cx - k, cy - k), (cx + k, cy + k)], fill="white", width=max(2, int(r * 0.24)))
            d.line([(cx - k, cy + k), (cx + k, cy - k)], fill="white", width=max(2, int(r * 0.24)))
        else:
            d.ellipse([cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62], outline="white", width=max(2, int(r * 0.2)))
            k = r * 0.44
            d.line([(cx - k, cy - k), (cx + k, cy + k)], fill="white", width=max(2, int(r * 0.2)))
    elif kind == "question":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(66, 133, 244, 255))
    else:  # info
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(66, 133, 244, 255))
        d.line([(cx, cy - r * 0.05), (cx, cy + r * 0.5)], fill="white", width=max(2, int(r * 0.22)))
        d.ellipse([cx - r * 0.12, cy - r * 0.5, cx + r * 0.12, cy - r * 0.26], fill="white")


def _dialog(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bw, bh = w * 0.82 * el.size, h * 0.34 * el.size
    cx, cy = _anchor_point(el.position if el.position != "top" else "bottom", w, h, head, char_box)
    cy = min(cy, h - bh / 2 - 4 * s)
    x0, y0, x1, y1 = cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([x0, y0 + 3 * s, x1, y1 + 3 * s], radius=int(10 * s), fill=(0, 0, 0, 70))
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(4 * s)))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(10 * s), fill=(255, 255, 255, 250), outline=(200, 200, 208, 255), width=max(1, int(s)))
    title_h = bh * 0.26
    d.rounded_rectangle([x0, y0, x1, y0 + title_h], radius=int(10 * s), fill=(242, 243, 247, 255))
    d.rectangle([x0, y0 + title_h * 0.5, x1, y0 + title_h], fill=(242, 243, 247, 255))
    title = element_text(el, "title", language)
    icon = el.icon or "warning"
    ir = title_h * 0.30
    _icon(d, icon, x0 + 12 * s + ir, y0 + title_h / 2, ir, s)
    _draw_text_box(layer, title, language, (x0 + 18 * s + 2 * ir, y0 + 2 * s, x1 - 8 * s, y0 + title_h - 2 * s),
                   (40, 40, 48, 255), None, 0.0, 1, 0.85, font, align="left")
    btn = element_text(el, "button", language)
    btn_h = bh * 0.22
    msg_box = (x0 + 10 * s, y0 + title_h + 4 * s, x1 - 10 * s, y1 - (btn_h + 8 * s if btn else 6 * s))
    _draw_text_box(layer, element_text(el, "text", language), language, msg_box, (30, 30, 36, 255), None, 0.0, 3, 0.62, font)
    if btn:
        bwid = bw * 0.34
        bx0, by0 = cx - bwid / 2, y1 - btn_h - 5 * s
        d.rounded_rectangle([bx0, by0, bx0 + bwid, by0 + btn_h], radius=int(btn_h / 2), fill=_color(el, "#3B82F6"))
        _draw_text_box(layer, btn, language, (bx0 + 4 * s, by0 + 1 * s, bx0 + bwid - 4 * s, by0 + btn_h - 1 * s),
                       (255, 255, 255, 255), None, 0.0, 1, 0.8, font)
    if el.animate == "shake" and total > 1:
        dx = int(round(math.sin(_phase(idx, total) * 2) * 2 * s))
        layer = ImageChops.offset(layer, dx, 0)
    return layer


def _chat(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    text = element_text(el, "text", language)
    max_w = w * 0.70 * el.size
    layout = fit_text(text, language, max_width=max_w - 20 * s, max_height=h * 0.28, start_size=int(17 * s * el.size),
                      min_size=int(9 * s), max_lines=3, user_font=font)
    bw = layout.width + 20 * s
    bh = layout.height + 14 * s
    right = el.position in ("bottom-right", "top-right", "right")
    cy = _anchor_point(el.position, w, h, head, char_box)[1]
    y0 = min(max(4 * s, cy - bh / 2), h - bh - 4 * s)
    x0 = (w - bw - 12 * s) if right else 12 * s
    fill = _color(el, "#95EC69" if right else "#FFFFFF")
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=int(7 * s), fill=fill, outline=(0, 0, 0, 40), width=max(1, int(s)))
    ty = y0 + min(bh * 0.5, 14 * s)
    if right:
        d.polygon([(x0 + bw - 1, ty - 5 * s), (x0 + bw + 7 * s, ty), (x0 + bw - 1, ty + 5 * s)], fill=fill)
    else:
        d.polygon([(x0 + 1, ty - 5 * s), (x0 - 7 * s, ty), (x0 + 1, ty + 5 * s)], fill=fill)
    draw_text_layout(layer, layout, x0 + bw / 2, y0 + 7 * s, (25, 25, 25, 255), None)
    return layer


def _pill(layer: Image.Image, text: str, language: str, cy: float, fill: RGBA, color: RGBA, s: float, font, height: float, max_w: float, icon_spinner: bool = False) -> Box:
    w = layer.width
    layout = fit_text(text, language, max_width=max_w - 22 * s, max_height=height, start_size=int(height * 0.62),
                      min_size=int(7 * s), max_lines=1, user_font=font)
    extra = height * 0.9 if icon_spinner else 0
    pw = layout.width + 18 * s + extra
    x0 = (w - pw) / 2
    y0 = cy - height / 2
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x0, y0, x0 + pw, y0 + height], radius=int(height / 2), fill=fill)
    if icon_spinner:
        icx, icy, ir = x0 + 9 * s + height * 0.32, cy, height * 0.30
        for i in range(8):
            a = math.radians(i * 45)
            d.line([(icx + math.cos(a) * ir * 0.35, icy + math.sin(a) * ir * 0.35), (icx + math.cos(a) * ir, icy + math.sin(a) * ir)],
                   fill=color, width=max(1, int(1.6 * s)))
    draw_text_layout(layer, layout, x0 + extra + (pw - extra) / 2, cy - layout.height / 2, color, None)
    return (x0, y0, x0 + pw, y0 + height)


def _notice(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cy = _anchor_point(el.position, w, h, head, char_box)[1]
    _pill(layer, element_text(el, "text", language), language, cy, (0, 0, 0, 92), (255, 255, 255, 255), s, font, 20 * s * el.size, w * 0.92)
    return layer


def _chip(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cy = _anchor_point(el.position, w, h, head, char_box)[1]
    _pill(layer, element_text(el, "text", language), language, cy, (244, 244, 247, 245), (90, 90, 100, 255), s, font,
          21 * s * el.size, w * 0.92, icon_spinner=True)
    return layer


def _progress(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cy = _anchor_point(el.position if el.position != "top" else "bottom", w, h, head, char_box)[1]
    bw, bh = w * 0.78 * el.size, 13 * s * el.size
    x0, y0 = (w - bw) / 2, cy
    value = (el.value if el.value is not None else 99) / 100.0
    if el.animate == "progress" and total > 1:
        value = value * min(1.0, (idx + 1) / max(1.0, total * 0.75))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x0 - 2 * s, y0 - 2 * s, x0 + bw + 2 * s, y0 + bh + 2 * s], radius=int(bh), fill=(255, 255, 255, 240), outline=(60, 60, 70, 255), width=max(1, int(1.5 * s)))
    if value > 0:
        d.rounded_rectangle([x0, y0, x0 + max(bh, bw * value), y0 + bh], radius=int(bh / 2), fill=_color(el, "#22C55E"))
    label = element_text(el, "text", language)
    pct = f"{int(round(value * 100))}%"
    _draw_text_box(layer, f"{label} {pct}".strip(), language, (x0, y0 - 24 * s, x0 + bw, y0 - 3 * s),
                   (30, 30, 36, 255), (255, 255, 255, 255), 0.14, 1, 0.9, font)
    return layer


def _big_text(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    text = element_text(el, "text", language) or "404"
    cx, cy = _anchor_point(el.position, w, h, head, char_box)
    bh = h * 0.30 * el.size
    color = _color(el, "#111827")
    latin = all(ord(c) < 0x2E80 for c in text)
    _draw_text_box(layer, text, language, (w * 0.04, cy - bh / 2, w * 0.96, cy + bh / 2), color, (255, 255, 255, 255), 0.06,
                   1, 1.0, impact_font_path() if latin else font)
    if el.animate == "glitch":
        rnd = random.Random(idx * 97 + 13)
        r, g, b, a = layer.split()
        off = int((2 + rnd.random() * 4) * s)
        red = Image.merge("RGBA", (r, Image.new("L", r.size, 0), Image.new("L", r.size, 0), a))
        cyan = Image.merge("RGBA", (Image.new("L", r.size, 0), g, b, a))
        layer = Image.alpha_composite(ImageChops.offset(red, off, 0), ImageChops.offset(cyan, -off, 0))
        layer = Image.alpha_composite(layer, Image.merge("RGBA", (r, g, b, a.point(lambda v: v // 2))))
    return layer


def _impact(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    info = get_language_info(language)
    top = element_text(el, "text", language)
    bottom = element_text(el, "title", language)
    use_impact = info.script in ("latin", "cyrillic", "greek")
    f = impact_font_path() if use_impact else font
    if use_impact:
        top, bottom = top.upper(), bottom.upper()
    fill = _color(el, "#FFFFFF")
    if top:
        _draw_text_box(layer, top, language, (w * 0.04, h * 0.02, w * 0.96, h * 0.22), fill, (0, 0, 0, 255), 0.12, 2, 0.9, f)
    if bottom:
        _draw_text_box(layer, bottom, language, (w * 0.04, h * 0.76, w * 0.96, h * 0.97), fill, (0, 0, 0, 255), 0.12, 2, 0.9, f)
    return layer


def top_bar_height(h: int) -> int:
    return int(h * 0.22)


def _top_bar(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bh = top_bar_height(h)
    ImageDraw.Draw(layer).rectangle([0, 0, w, bh], fill=_color(el, "#FFFFFF"))
    _draw_text_box(layer, element_text(el, "text", language), language, (w * 0.05, bh * 0.10, w * 0.95, bh * 0.92),
                   (20, 20, 20, 255), None, 0.0, 2, 0.62, font)
    return layer


def _speed_lines(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = _anchor_point(el.position if el.position not in ("top", "full") else "center", w, h, head, char_box)
    rnd = random.Random(7 + (idx if el.animate in ("shake", "flash") else 0))
    color = _color(el, "#111111")
    outer = math.hypot(w, h)
    n = 64
    for i in range(n):
        a = 2 * math.pi * (i + rnd.random() * 0.6) / n
        inner = outer * (0.24 + rnd.random() * 0.12) * el.size
        spread = 0.012 + rnd.random() * 0.02
        p1 = (cx + math.cos(a - spread) * outer, cy + math.sin(a - spread) * outer)
        p2 = (cx + math.cos(a + spread) * outer, cy + math.sin(a + spread) * outer)
        p0 = (cx + math.cos(a) * inner, cy + math.sin(a) * inner)
        d.polygon([p0, p1, p2], fill=color[:3] + (200,))
    return layer


def _light_rays(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = head[0], (char_box[1] + char_box[3]) / 2.0
    color = _color(el, "#FFE27A")
    n = 16
    rot = (idx / float(max(1, total))) * (360.0 / n * 2) if el.animate in ("rotate", "twinkle", "pulse") else 0.0
    outer = math.hypot(w, h)
    for i in range(0, n * 2, 2):
        a0 = math.radians(rot + i * 180.0 / n)
        a1 = math.radians(rot + (i + 1) * 180.0 / n)
        d.polygon([(cx, cy), (cx + math.cos(a0) * outer, cy + math.sin(a0) * outer), (cx + math.cos(a1) * outer, cy + math.sin(a1) * outer)],
                  fill=color[:3] + (150,))
    glow = Image.new("L", (w, h), 0)
    gr = min(w, h) * 0.30 * el.size
    ImageDraw.Draw(glow).ellipse([cx - gr, cy - gr, cx + gr, cy + gr], fill=210)
    glow = glow.filter(ImageFilter.GaussianBlur(gr * 0.5))
    halo = Image.new("RGBA", (w, h), (255, 255, 240, 0))
    halo.putalpha(glow)
    return Image.alpha_composite(layer, halo)


def _crack(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = random.Random(42)
    cx, cy = head[0], char_box[1] + (char_box[3] - char_box[1]) * 0.32
    segs = []
    for i in range(9):
        a = 2 * math.pi * i / 9 + rnd.uniform(-0.25, 0.25)
        x, y = cx, cy
        pts = [(x, y)]
        length = min(w, h) * rnd.uniform(0.30, 0.62) * el.size
        n = 6
        for k in range(n):
            a += rnd.uniform(-0.35, 0.35)
            x += math.cos(a) * length / n
            y += math.sin(a) * length / n
            pts.append((x, y))
            if rnd.random() < 0.3:
                bx = x + math.cos(a + 0.9) * length / n * 0.8
                by = y + math.sin(a + 0.9) * length / n * 0.8
                segs.append([(x, y), (bx, by)])
        segs.append(pts)
    for pts in segs:
        d.line(pts, fill=(40, 40, 50, 200), width=max(2, int(2.6 * s)))
    for pts in segs:
        d.line(pts, fill=(255, 255, 255, 240), width=max(1, int(1.1 * s)))
    return layer


def _smoke(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    hx, top = head[0], char_box[1]
    color = _color(el, "#9CA3AF")
    for k in range(3):
        t = ((idx / float(max(1, total))) + k / 3.0) % 1.0 if el.animate == "drift" else k / 3.0
        y = top - t * h * 0.16
        x = hx + (k - 1) * 18 * s + math.sin(t * 6.28) * 5 * s
        r = (9 + t * 10) * s * el.size
        alpha = int(220 * (1 - t * 0.7))
        for dx, dy, rr in ((0, 0, 1.0), (-0.7, 0.2, 0.7), (0.7, 0.25, 0.75)):
            rad = r * rr
            d.ellipse([x + dx * r - rad, y + dy * r - rad, x + dx * r + rad, y + dy * r + rad], fill=color[:3] + (alpha,))
    return layer


def _battery(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cx, cy = _anchor_point(el.position if el.position != "top" else "top-right", w, h, head, char_box)
    bw, bh = 46 * s * el.size, 22 * s * el.size
    x0, y0 = cx - bw / 2, cy - bh / 2
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=int(4 * s), fill=(255, 255, 255, 235), outline=(30, 30, 30, 255), width=max(2, int(2.4 * s)))
    d.rectangle([x0 + bw, cy - bh * 0.22, x0 + bw + 4 * s, cy + bh * 0.22], fill=(30, 30, 30, 255))
    v = (el.value if el.value is not None else 1) / 100.0
    if el.animate == "flash" and idx % 2:
        v = 0
    fill_w = max(2 * s, (bw - 6 * s) * v)
    d.rectangle([x0 + 3 * s, y0 + 3 * s, x0 + 3 * s + fill_w, y0 + bh - 3 * s], fill=_color(el, "#EF4444" if v < 0.2 else "#22C55E"))
    label = element_text(el, "text", language) or f"{int(round(v * 100))}%"
    _draw_text_box(layer, label, language, (cx - bw * 1.4, y0 + bh + 2 * s, cx + bw * 1.4, y0 + bh + 22 * s * el.size),
                   (220, 38, 38, 255), (255, 255, 255, 255), 0.14, 1, 0.9, font)
    return layer


def _typing(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    base = element_text(el, "text", language) or "…"
    base = base.rstrip(".…。")
    dots = (idx % 3) + 1 if el.animate == "dots" and total > 1 else 3
    cy = _anchor_point(el.position if el.position != "top" else "top", w, h, head, char_box)[1]
    _pill(layer, base + "." * dots + " " * (3 - dots), language, cy, (255, 255, 255, 235), (110, 110, 120, 255), s, font, 20 * s * el.size, w * 0.92)
    return layer


def _read_receipt(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cx, cy = _anchor_point(el.position if el.position != "top" else "bottom-right", w, h, head, char_box)
    _draw_text_box(layer, element_text(el, "text", language) or "Read", language, (cx - 50 * s, cy - 10 * s, cx + 50 * s, cy + 10 * s),
                   _color(el, "#6B7280"), (255, 255, 255, 255), 0.18, 1, 0.9, font)
    return layer


def _star(d: ImageDraw.ImageDraw, x: float, y: float, r: float, color: RGBA) -> None:
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.32
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    d.polygon(pts, fill=color)


def _sparkles(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = char_box
    spots = [(x0 - 6 * s, y0 + 20 * s), (x1 + 4 * s, y0 + 10 * s), (x1 - 4 * s, (y0 + y1) / 2), (x0 + 8 * s, (y0 + y1) / 2 + 10 * s), ((x0 + x1) / 2 + 40 * s, y0 - 4 * s)]
    color = _color(el, "#FFD54A")
    for k, (x, y) in enumerate(spots):
        tw = 0.55 + 0.45 * math.sin(_phase(idx, total) + k * 1.7) if el.animate == "twinkle" else 1.0
        _star(d, x, y, 9 * s * el.size * tw, color)
    return layer


def _question_marks(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hx, top = head[0], char_box[1]
    colors = [_color(el, "#3B82F6"), hex_to_rgba("#F97316"), hex_to_rgba("#A855F7")]
    for k, dx in enumerate((-40, 0, 40)):
        dy = math.sin(_phase(idx, total) + k * 2.1) * 4 * s if el.animate == "drift" else 0
        cx, cy = hx + dx * s * el.size, top + (8 if k == 1 else 18) * s + dy
        sz = (26 if k == 1 else 20) * s * el.size
        _draw_text_box(layer, "?", "en", (cx - sz, cy - sz, cx + sz, cy + sz), colors[k], (255, 255, 255, 255), 0.16, 1, 1.0, impact_font_path())
    return layer


def _mute(el, w, h, s, head, char_box, language, idx, total, font) -> Image.Image:
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cx, cy = _anchor_point(el.position if el.position != "top" else "top-left", w, h, head, char_box)
    r = 18 * s * el.size
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(239, 68, 68, 255), outline=(255, 255, 255, 255), width=max(2, int(2 * s)))
    k = r * 0.42
    d.rectangle([cx - k, cy - k * 0.45, cx - k * 0.35, cy + k * 0.45], fill="white")
    d.polygon([(cx - k * 0.35, cy - k * 0.45), (cx + k * 0.3, cy - k), (cx + k * 0.3, cy + k), (cx - k * 0.35, cy + k * 0.45)], fill="white")
    d.line([(cx - k * 1.1, cy + k * 1.1), (cx + k * 1.1, cy - k * 1.1)], fill="white", width=max(2, int(2.2 * s)))
    return layer


_RENDERERS = {
    "spinner": _spinner,
    "prohibition": _prohibition,
    "hazard_tape": _hazard_tape,
    "stamp": _stamp,
    "dialog": _dialog,
    "chat": _chat,
    "notice": _notice,
    "chip": _chip,
    "progress": _progress,
    "big_text": _big_text,
    "impact": _impact,
    "top_bar": _top_bar,
    "speed_lines": _speed_lines,
    "light_rays": _light_rays,
    "crack": _crack,
    "smoke": _smoke,
    "battery": _battery,
    "typing": _typing,
    "read_receipt": _read_receipt,
    "sparkles": _sparkles,
    "question_marks": _question_marks,
    "mute": _mute,
}

_BACK_TYPES = {"speed_lines", "light_rays"}


def is_back(el: MemeElement) -> bool:
    return el.layer == "back" or el.type in _BACK_TYPES


_BOTTOM_POSITIONS = {"bottom", "bottom-left", "bottom-right"}
_CAPTION_SENSITIVE = {"notice", "typing", "progress", "dialog", "chat", "hazard_tape", "read_receipt", "prohibition", "battery", "stamp"}


def render_element(
    el: MemeElement,
    canvas: Tuple[int, int],
    head: Tuple[float, float],
    char_box: Box,
    language: str,
    idx: int = 0,
    total: int = 1,
    font_path: Optional[str] = None,
    caption_safe: bool = False,
) -> Image.Image:
    w, h = canvas
    s = w / BASE_CANVAS
    layer = _RENDERERS[el.type](el, w, h, s, head, char_box, language, idx if total > 1 else 0, total, font_path)
    if caption_safe and el.position in _BOTTOM_POSITIONS and el.type in _CAPTION_SENSITIVE:
        shifted = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        shifted.paste(layer, (0, -int(h * 0.17)), layer)
        layer = shifted
    if el.angle and el.type not in ("hazard_tape", "stamp"):
        layer = _rotate_layer(layer, el.angle, _anchor_point(el.position, w, h, head, char_box))
    if el.animate == "flash" and total > 1 and el.type not in ("hazard_tape", "battery") and idx % 2 == 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * 0.45)))
    return layer


# ---------------------------------------------------------------------------
# Frame filters
# ---------------------------------------------------------------------------


def _split_alpha(frame: Image.Image) -> Tuple[Image.Image, Image.Image]:
    rgba = frame.convert("RGBA")
    return rgba.convert("RGB"), rgba.getchannel("A")


def _jpeg(rgb: Image.Image, quality: int) -> Image.Image:
    buf = io.BytesIO()
    rgb.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def apply_filter(frame: Image.Image, name: str, idx: int = 0, total: int = 1) -> Image.Image:
    rgb, alpha = _split_alpha(frame)
    w, h = rgb.size
    if name == "deep_fry":
        rgb = ImageEnhance.Color(rgb).enhance(2.4)
        rgb = ImageEnhance.Contrast(rgb).enhance(1.7)
        rgb = ImageEnhance.Sharpness(rgb).enhance(4.0)
        tint = Image.new("RGB", rgb.size, (255, 120, 0))
        rgb = Image.blend(rgb, tint, 0.12)
        noise = Image.effect_noise(rgb.size, 60).convert("RGB")
        rgb = Image.blend(rgb, noise, 0.10)
        rgb = _jpeg(rgb, 9)
    elif name == "patina":
        small = rgb.resize((max(8, int(w * 0.45)), max(8, int(h * 0.45))), Image.Resampling.BILINEAR)
        for q in (14, 10, 8):
            small = _jpeg(small, q)
        rgb = small.resize((w, h), Image.Resampling.BILINEAR)
        rgb = Image.blend(ImageEnhance.Color(rgb).enhance(0.7), Image.new("RGB", rgb.size, (190, 200, 120)), 0.12)
        rgb = _jpeg(rgb, 12)
    elif name == "glitch":
        rnd = random.Random(idx * 31 + 5)
        r, g, b = rgb.split()
        off = max(2, int(w * (0.008 + rnd.random() * 0.018)))
        rgb = Image.merge("RGB", (ImageChops.offset(r, off, 0), g, ImageChops.offset(b, -off, 0)))
        for _ in range(4):
            y0 = rnd.randrange(0, h)
            hh = rnd.randrange(max(2, h // 60), max(3, h // 14))
            dx = rnd.randrange(-w // 18, w // 18)
            band = rgb.crop((0, y0, w, min(h, y0 + hh)))
            rgb.paste(ImageChops.offset(band, dx, 0), (0, y0))
            ab = alpha.crop((0, y0, w, min(h, y0 + hh)))
            alpha.paste(ImageChops.offset(ab, dx, 0), (0, y0))
        lines = Image.new("L", rgb.size, 0)
        ld = ImageDraw.Draw(lines)
        for y in range(0, h, max(2, h // 120)):
            ld.line([(0, y), (w, y)], fill=28)
        rgb = ImageChops.subtract(rgb, Image.merge("RGB", (lines, lines, lines)))
    elif name == "grayscale":
        rgb = ImageOps.grayscale(rgb).convert("RGB")
    elif name == "hue_cycle":
        shift = int(255 * idx / float(max(1, total))) if total > 1 else 60
        hsv = rgb.convert("HSV")
        hch, sch, vch = hsv.split()
        hch = hch.point(lambda v: (v + shift) % 256)
        sch = sch.point(lambda v: min(255, int(v * 1.35)))
        rgb = Image.merge("HSV", (hch, sch, vch)).convert("RGB")
    elif name == "vignette":
        mask = Image.new("L", rgb.size, 0)
        ImageDraw.Draw(mask).ellipse([-w * 0.15, -h * 0.15, w * 1.15, h * 1.15], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) * 0.12))
        rgb = Image.composite(rgb, ImageEnhance.Brightness(rgb).enhance(0.45), mask)
    elif name == "high_contrast":
        rgb = ImageEnhance.Contrast(ImageOps.autocontrast(rgb, cutoff=1)).enhance(1.45)
    elif name == "posterize":
        rgb = ImageOps.posterize(rgb, 3)
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


# ---------------------------------------------------------------------------
# Public API used by the composer
# ---------------------------------------------------------------------------


class MemeRenderer:
    """Caches static element layers; re-renders only animated ones per frame."""

    def __init__(self, meme: MemeSpec, canvas: Tuple[int, int], head: Tuple[float, float], char_box: Box, language: str, font_path: Optional[str] = None, caption_safe: bool = False):
        self.caption_safe = caption_safe
        self.meme = meme
        self.canvas = canvas
        self.head = head
        self.char_box = char_box
        self.language = language
        self.font_path = font_path
        self._cache: Dict[Tuple[int, int], Image.Image] = {}

    def _layer(self, i: int, el: MemeElement, idx: int, total: int) -> Image.Image:
        animated = el.animate != "none" and total > 1
        key = (i, idx if animated else -1)
        if key not in self._cache:
            self._cache[key] = render_element(el, self.canvas, self.head, self.char_box, self.language, idx, total, self.font_path, self.caption_safe)
        return self._cache[key]

    def back(self, idx: int, total: int) -> Optional[Image.Image]:
        layers = [self._layer(i, el, idx, total) for i, el in enumerate(self.meme.elements) if is_back(el)]
        if not layers:
            return None
        out = Image.new("RGBA", self.canvas, (0, 0, 0, 0))
        for l in layers:
            out = Image.alpha_composite(out, l)
        return out

    def front(self, frame: Image.Image, idx: int, total: int) -> Image.Image:
        for i, el in enumerate(self.meme.elements):
            if not is_back(el):
                frame = Image.alpha_composite(frame, self._layer(i, el, idx, total))
        return frame

    def finish(self, frame: Image.Image, idx: int, total: int) -> Image.Image:
        if self.meme.background:
            bg = Image.new("RGBA", frame.size, hex_to_rgba(self.meme.background))
            frame = Image.alpha_composite(bg, frame)
        for f in self.meme.filters:
            frame = apply_filter(frame, f, idx, total)
        return frame


def reserve_top_ratio(meme: Optional[MemeSpec]) -> float:
    if meme and any(el.type == "top_bar" for el in meme.elements):
        return 0.22
    if meme and any(el.type == "impact" and el.text for el in meme.elements):
        return 0.06
    return 0.0
