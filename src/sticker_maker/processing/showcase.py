"""Social-content showcase renderer for Xiaohongshu / Instagram / TikTok / Douyin / Weibo / X:
3:4 or 4:5 covers, sticker grids, single-sticker pages, 9:16 stories, Weibo nine-grid and
animated grid frames for MP4 videos."""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFilter

from ..schemas import StylePreset
from ..styles import hex_to_rgba, resolve_style_preset
from .typography import draw_text_layout, fit_text


def _mix(c1: Tuple[int, int, int, int], c2: Tuple[int, int, int, int], t: float) -> Tuple[int, int, int, int]:
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))  # type: ignore[return-value]


def _lighten(c: Tuple[int, int, int, int], t: float) -> Tuple[int, int, int, int]:
    return _mix(c, (255, 255, 255, 255), t)


def showcase_background(size: Tuple[int, int], style: Optional[str | StylePreset] = None) -> Image.Image:
    preset = style if isinstance(style, StylePreset) else resolve_style_preset(style or "kawaii-flat")
    w, h = size
    top = hex_to_rgba(preset.banner_bg)
    pal = preset.default_palette or ["#F7BDC9"]
    accent = hex_to_rgba(pal[min(1, len(pal) - 1)])
    bottom = _lighten(accent, 0.55)
    grad = Image.new("RGBA", (1, 256))
    for y in range(256):
        grad.putpixel((0, y), _mix(top, bottom, y / 255.0))
    bg = grad.resize((w, h), Image.Resampling.BICUBIC)
    deco = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(deco)
    a1 = _lighten(accent, 0.15)[:3] + (70,)
    r = int(min(w, h) * 0.28)
    d.ellipse([-r // 2, -r // 2, r, r], fill=a1)
    d.ellipse([w - r, h - r, w + r // 2, h + r // 2], fill=a1)
    d.ellipse([int(w * 0.80), int(h * 0.10), int(w * 0.80) + r // 4, int(h * 0.10) + r // 4], fill=a1)
    deco = deco.filter(ImageFilter.GaussianBlur(radius=max(2, min(w, h) // 60)))
    return Image.alpha_composite(bg, deco)


def _paste_fit(canvas: Image.Image, sticker: Image.Image, box: Tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    bw, bh = max(1, x1 - x0), max(1, y1 - y0)
    s = min(bw / float(sticker.width), bh / float(sticker.height))
    nw, nh = max(1, int(sticker.width * s)), max(1, int(sticker.height * s))
    resized = sticker.convert("RGBA").resize((nw, nh), Image.Resampling.LANCZOS)
    canvas.alpha_composite(resized, (x0 + (bw - nw) // 2, y0 + (bh - nh) // 2))


def _card(canvas: Image.Image, box: Tuple[int, int, int, int], radius: int) -> None:
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    off = max(2, radius // 5)
    sd.rounded_rectangle([box[0], box[1] + off, box[2], box[3] + off], radius=radius, fill=(0, 0, 0, 38))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(2, radius // 3)))
    canvas.alpha_composite(shadow)
    ImageDraw.Draw(canvas).rounded_rectangle(box, radius=radius, fill=(255, 255, 255, 235))


def _title(canvas: Image.Image, text: str, language: str, box: Tuple[int, int, int, int], style: StylePreset, font_path: Optional[str]) -> None:
    if not text:
        return
    x0, y0, x1, y1 = box
    layout = fit_text(
        text, language, max_width=x1 - x0, max_height=y1 - y0,
        start_size=int((y1 - y0) * 0.62), min_size=max(10, int((y1 - y0) * 0.2)),
        max_lines=2, user_font=font_path, stroke_ratio=0.08,
    )
    top = y0 + ((y1 - y0) - layout.height) / 2.0
    draw_text_layout(
        canvas, layout, (x0 + x1) / 2.0, top,
        hex_to_rgba(style.typography.text_color), hex_to_rgba(style.typography.stroke_color),
    )


def make_cover(
    size: Tuple[int, int],
    stickers: Sequence[Image.Image],
    title: str,
    subtitle: str = "",
    style: Optional[str | StylePreset] = None,
    language: str = "zh-CN",
    font_path: Optional[str] = None,
) -> Image.Image:
    preset = style if isinstance(style, StylePreset) else resolve_style_preset(style or "kawaii-flat")
    w, h = size
    canvas = showcase_background(size, preset)
    _title(canvas, title, language, (int(w * 0.06), int(h * 0.04), int(w * 0.94), int(h * 0.16)), preset, font_path)
    if subtitle:
        _title(canvas, subtitle, language, (int(w * 0.12), int(h * 0.16), int(w * 0.88), int(h * 0.22)), preset, font_path)
    if stickers:
        _paste_fit(canvas, stickers[0], (int(w * 0.12), int(h * 0.22), int(w * 0.88), int(h * 0.72)))
    small = list(stickers[1:4])
    if small:
        cell = int(w * 0.84 / max(3, len(small)))
        x = int(w * 0.08)
        for st in small:
            _card(canvas, (x + 8, int(h * 0.74), x + cell - 8, int(h * 0.74) + cell - 16), radius=max(8, cell // 10))
            _paste_fit(canvas, st, (x + 16, int(h * 0.74) + 8, x + cell - 16, int(h * 0.74) + cell - 24))
            x += cell
    return canvas.convert("RGB")


def _grid_layout(size: Tuple[int, int], cols: int, rows: int, title_h_ratio: float) -> List[Tuple[int, int, int, int]]:
    w, h = size
    top = int(h * title_h_ratio)
    pad = int(min(w, h) * 0.03)
    cell_w = (w - pad * (cols + 1)) / float(cols)
    cell_h = (h - top - pad * (rows + 1)) / float(rows)
    cell = min(cell_w, cell_h)
    grid_w = cell * cols + pad * (cols - 1)
    grid_h = cell * rows + pad * (rows - 1)
    gx0 = (w - grid_w) / 2.0
    gy0 = top + (h - top - grid_h) / 2.0
    boxes = []
    for r in range(rows):
        for c in range(cols):
            x = gx0 + c * (cell + pad)
            y = gy0 + r * (cell + pad)
            boxes.append((int(x), int(y), int(x + cell), int(y + cell)))
    return boxes


def _grid_base(
    size: Tuple[int, int],
    n_cells: int,
    cols: int,
    rows: int,
    title: str,
    preset: StylePreset,
    language: str,
    font_path: Optional[str],
    background: Optional[Image.Image] = None,
) -> Tuple[Image.Image, List[Tuple[int, int, int, int]]]:
    """Background + title + white rounded cards (shadows blurred once for all cards)."""
    w, h = size
    title_ratio = 0.10 if title else 0.03
    canvas = background.copy() if background is not None else showcase_background(size, preset)
    if title:
        _title(canvas, title, language, (int(w * 0.06), int(h * 0.015), int(w * 0.94), int(h * title_ratio)), preset, font_path)
    boxes = _grid_layout(size, cols, rows, title_ratio)[: max(0, n_cells)]
    if boxes:
        rad = max(8, (boxes[0][2] - boxes[0][0]) // 9)
        shadow = Image.new("RGBA", size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        off = max(2, rad // 5)
        for b in boxes:
            sd.rounded_rectangle([b[0], b[1] + off, b[2], b[3] + off], radius=rad, fill=(0, 0, 0, 38))
        canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(radius=max(2, rad // 3))))
        cd = ImageDraw.Draw(canvas)
        for b in boxes:
            cd.rounded_rectangle(b, radius=rad, fill=(255, 255, 255, 235))
    return canvas, boxes


def _paste_cells(canvas: Image.Image, boxes: Sequence[Tuple[int, int, int, int]], stickers: Sequence[Image.Image]) -> None:
    for box, st in zip(boxes, stickers):
        inset = int((box[2] - box[0]) * 0.06)
        _paste_fit(canvas, st, (box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset))


def make_grid_frames(
    size: Tuple[int, int],
    stickers: Sequence[Image.Image],
    cols: int = 3,
    rows: int = 3,
    title: str = "",
    style: Optional[str | StylePreset] = None,
    language: str = "zh-CN",
    font_path: Optional[str] = None,
    background: Optional[Image.Image] = None,
) -> Image.Image:
    """One grid page (RGBA) of up to cols*rows stickers with white rounded cards."""
    preset = style if isinstance(style, StylePreset) else resolve_style_preset(style or "kawaii-flat")
    canvas, boxes = _grid_base(size, len(stickers), cols, rows, title, preset, language, font_path, background)
    _paste_cells(canvas, boxes, stickers)
    return canvas


def make_grid_pages(
    size: Tuple[int, int],
    stickers: Sequence[Image.Image],
    cols: int = 3,
    rows: int = 3,
    title: str = "",
    style: Optional[str | StylePreset] = None,
    language: str = "zh-CN",
    font_path: Optional[str] = None,
) -> List[Image.Image]:
    per = cols * rows
    pages = []
    n_pages = max(1, int(math.ceil(len(stickers) / float(per))))
    for p in range(n_pages):
        chunk = list(stickers[p * per:(p + 1) * per])
        page_title = title if n_pages == 1 else f"{title} {p + 1}/{n_pages}".strip()
        pages.append(make_grid_frames(size, chunk, cols, rows, page_title, style, language, font_path).convert("RGB"))
    return pages


def make_single_pages(
    size: Tuple[int, int],
    stickers: Sequence[Image.Image],
    style: Optional[str | StylePreset] = None,
    max_items: Optional[int] = None,
) -> List[Image.Image]:
    preset = style if isinstance(style, StylePreset) else resolve_style_preset(style or "kawaii-flat")
    w, h = size
    pages = []
    for st in list(stickers)[: max_items or len(stickers)]:
        canvas = showcase_background(size, preset)
        side = int(min(w, h) * 0.80)
        box = ((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2)
        _card(canvas, box, radius=side // 12)
        inset = side // 14
        _paste_fit(canvas, st, (box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset))
        pages.append(canvas.convert("RGB"))
    return pages


def make_story_pages(
    size: Tuple[int, int],
    stickers: Sequence[Image.Image],
    title: str = "",
    style: Optional[str | StylePreset] = None,
    language: str = "zh-CN",
    font_path: Optional[str] = None,
    max_items: Optional[int] = None,
) -> List[Image.Image]:
    preset = style if isinstance(style, StylePreset) else resolve_style_preset(style or "kawaii-flat")
    w, h = size
    pages = []
    for st in list(stickers)[: max_items or len(stickers)]:
        canvas = showcase_background(size, preset)
        _title(canvas, title, language, (int(w * 0.08), int(h * 0.10), int(w * 0.92), int(h * 0.18)), preset, font_path)
        side = int(w * 0.84)
        _paste_fit(canvas, st, ((w - side) // 2, int(h * 0.26), (w + side) // 2, int(h * 0.26) + side))
        pages.append(canvas.convert("RGB"))
    return pages


def make_nine_grid(
    size: Tuple[int, int],
    stickers: Sequence[Image.Image],
    style: Optional[str | StylePreset] = None,
) -> List[Image.Image]:
    """Weibo-style 九宫格: up to 9 separate square images that tile into a 3×3 post."""
    return make_single_pages(size, list(stickers)[:9], style)


def make_video_grid_frames(
    size: Tuple[int, int],
    animations: Sequence[Sequence[Image.Image]],
    cols: int = 3,
    rows: int = 4,
    title: str = "",
    style: Optional[str | StylePreset] = None,
    language: str = "zh-CN",
    font_path: Optional[str] = None,
) -> List[Image.Image]:
    """Compose one animation cycle of a grid where every cell plays its own sticker animation."""
    anims = [list(a) for a in animations if a][: cols * rows]
    if not anims:
        return []
    preset = style if isinstance(style, StylePreset) else resolve_style_preset(style or "kawaii-flat")
    n = max(len(a) for a in anims)
    base, boxes = _grid_base(size, len(anims), cols, rows, title, preset, language, font_path)
    frames = []
    for i in range(n):
        frame = base.copy()
        _paste_cells(frame, boxes, [a[i % len(a)] for a in anims])
        frames.append(frame)
    return frames
