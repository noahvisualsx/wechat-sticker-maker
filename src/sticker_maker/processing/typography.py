"""Multilingual sticker typography: per-script font fallback, emoji, line wrapping with
CJK kinsoku / word / Thai-cluster rules, auto-fit, and stroked caption rendering.

All sizes in style presets are expressed for a 240px canvas and are scaled automatically,
so the same layout renders crisply on 240px WeChat stickers and 720px+ master frames.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont

from ..config import get_default_font_path
from ..i18n import (
    RAQM_AVAILABLE,
    SCRIPT_FONT_CANDIDATES,
    char_script,
    font_chain_for_script,
    font_has_glyph,
    get_language_info,
    normalize_language,
)
from ..schemas import StylePreset
from ..styles import hex_to_rgba, resolve_style_preset

logger = logging.getLogger(__name__)

BASE_CANVAS = 240.0

# Characters that must not start a line (CJK kinsoku shori) / must not end a line.
_NO_LINE_START = set("、。，．,.!！?？:：;；)）]］}｝」』】〉》〕〙〗〟’”ー～〜…‥々ゝゞヽヾぁぃぅぇぉっゃゅょゎゕゖァィゥェォッャュョヮヵヶ%％♪♡")
_NO_LINE_END = set("([（［{｛「『【〈《〔〘〖〝‘“#＃$＄￥¥")
_THAI_COMBINING = set(chr(c) for c in [0x0E31, *range(0x0E34, 0x0E3B), *range(0x0E47, 0x0E4F)])
_EMOJI_NATIVE_SIZES = (160, 137, 109, 96, 64, 48, 40, 32, 20)

_warned_shaping = False


# ---------------------------------------------------------------------------
# Font loading
# ---------------------------------------------------------------------------


@lru_cache(maxsize=512)
def _truetype(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    kwargs = {}
    if RAQM_AVAILABLE:
        kwargs["layout_engine"] = ImageFont.Layout.RAQM
    return ImageFont.truetype(path, max(1, int(size)), index=index, **kwargs)


def load_font(font_path: Optional[str] = None, size: int = 24) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a TrueType font (user font → system CJK font → PIL default)."""
    candidates = []
    if font_path and Path(font_path).exists():
        candidates.append(font_path)
    sys_font = get_default_font_path()
    if sys_font:
        candidates.append(sys_font)
    for p in candidates:
        try:
            return _truetype(p, size, 0)
        except Exception as e:  # pragma: no cover - depends on host fonts
            logger.warning("Could not load font at %s: %s", p, e)
    logger.warning("No TrueType font found; falling back to default PIL font.")
    return ImageFont.load_default()


def _is_emoji_font(path: str) -> bool:
    return path in SCRIPT_FONT_CANDIDATES["emoji"]


@lru_cache(maxsize=64)
def _emoji_native_font(path: str) -> Optional[ImageFont.FreeTypeFont]:
    for s in _EMOJI_NATIVE_SIZES:
        try:
            return ImageFont.truetype(path, s)
        except Exception:
            continue
    return None


@lru_cache(maxsize=1024)
def _render_emoji(path: str, text: str, target_px: int) -> Optional[Image.Image]:
    font = _emoji_native_font(path)
    if font is None:
        return None
    size = font.size
    canvas = Image.new("RGBA", (size * (len(text) + 1) * 2, size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    try:
        d.text((size // 2, size // 2), text, font=font, embedded_color=True)
    except Exception:
        return None
    bbox = canvas.getbbox()
    if not bbox:
        return None
    crop = canvas.crop(bbox)
    scale = target_px / float(max(1, crop.height))
    return crop.resize((max(1, int(crop.width * scale)), max(1, target_px)), Image.Resampling.LANCZOS)


# ---------------------------------------------------------------------------
# Run segmentation (per-character font fallback)
# ---------------------------------------------------------------------------


@dataclass
class TextRun:
    text: str
    path: Optional[str]
    index: int
    script: str
    kind: str = "text"  # text | emoji


def _resolve_script_for_language(script: str, language: str) -> str:
    info = get_language_info(language)
    cjk_lang = info.script in ("jpan", "hant", "kore", "hans")
    if script in ("han", "cjk-punct"):
        return info.script if cjk_lang else "hans"
    if script == "kana":
        return "jpan"
    if script == "latin" and cjk_lang:
        # CJK fonts include Latin glyphs; keep "OK啦" visually consistent in one typeface
        return info.script
    return script


@lru_cache(maxsize=8192)
def _font_for_char(ch: str, script: str, user_font: Optional[str]) -> Tuple[Optional[str], int]:
    for path, idx in font_chain_for_script(script, user_font):
        if script == "emoji" or char_script(ch) in ("emoji", "emoji-mod"):
            if _is_emoji_font(path):
                return path, idx
            continue
        if _is_emoji_font(path):
            continue
        if font_has_glyph(path, idx, ch):
            return path, idx
    fallback = get_default_font_path()
    return (fallback, 0) if fallback else (None, 0)


@lru_cache(maxsize=4096)
def _font_for_group(group: str, script: str, user_font: Optional[str]) -> Tuple[Optional[str], int]:
    """First font in the script chain that covers every character of the group (or (None, 0))."""
    for path, idx in font_chain_for_script(script, user_font):
        if _is_emoji_font(path):
            continue
        if all(font_has_glyph(path, idx, c) for c in group if not c.isspace()):
            return path, idx
    return None, 0


def segment_runs(text: str, language: str = "zh-CN", user_font: Optional[str] = None) -> List[TextRun]:
    """Split text into runs that share one font.

    Characters are grouped by resolved script (spaces/digits/punctuation join their neighbours),
    each group gets the first font covering the whole group, and only uncovered groups fall back
    to per-character font selection. Emoji are rendered with a colour emoji font.
    """
    language = normalize_language(language)
    lang_script = get_language_info(language).script
    raw = [char_script(ch) for ch in text]

    first_real = next((s for s in raw if s not in ("neutral", "mark", "emoji-mod", "emoji")), lang_script)
    current_text_script = _resolve_script_for_language(first_real, language)
    resolved: List[str] = []
    for s in raw:
        if s in ("emoji", "emoji-mod"):
            resolved.append("emoji")
        elif s in ("neutral", "mark"):
            resolved.append(current_text_script)
        else:
            current_text_script = _resolve_script_for_language(s, language)
            resolved.append(current_text_script)

    # Group contiguous characters by resolved script
    groups: List[Tuple[str, str]] = []
    for ch, sc in zip(text, resolved):
        if groups and groups[-1][1] == sc:
            groups[-1] = (groups[-1][0] + ch, sc)
        else:
            groups.append((ch, sc))

    runs: List[TextRun] = []

    def push(chunk: str, path: Optional[str], idx: int, sc: str, kind: str) -> None:
        if runs and runs[-1].path == path and runs[-1].index == idx and runs[-1].kind == kind:
            runs[-1].text += chunk
        else:
            runs.append(TextRun(chunk, path, idx, sc, kind))

    for chunk, sc in groups:
        if sc == "emoji":
            path, idx = _font_for_char(chunk[0], "emoji", user_font)
            if path and _is_emoji_font(path):
                push(chunk, path, idx, sc, "emoji")
            continue  # drop emoji if no colour emoji font exists (avoids tofu boxes)
        path, idx = _font_for_group(chunk, sc, user_font)
        if path:
            push(chunk, path, idx, sc, "text")
            continue
        for ch in chunk:
            cpath, cidx = _font_for_char(ch, sc, user_font)
            push(ch, cpath, cidx, sc, "text")
    return runs


# ---------------------------------------------------------------------------
# Measuring & drawing runs
# ---------------------------------------------------------------------------


def _direction_for(run: TextRun) -> Optional[str]:
    if run.script in ("arabic", "hebrew") and RAQM_AVAILABLE:
        return "rtl"
    return None


def _visual_text(run: TextRun) -> str:
    global _warned_shaping
    if run.script in ("arabic", "hebrew") and not RAQM_AVAILABLE:
        if run.script == "arabic" and not _warned_shaping:
            logger.warning("libraqm not available: Arabic/Persian text cannot be joined correctly.")
            _warned_shaping = True
        return run.text[::-1]
    return run.text


def _run_font(run: TextRun, size: int) -> Optional[ImageFont.FreeTypeFont]:
    if not run.path:
        return None
    try:
        return _truetype(run.path, size, run.index)
    except Exception:
        return None


def _measure_run(run: TextRun, size: int) -> Tuple[float, int, int]:
    """Return (advance_width, ascent, descent) of a run at the given pixel size."""
    if run.kind == "emoji":
        img = _render_emoji(run.path or "", run.text, int(size * 0.95))
        w = img.width if img is not None else size * len(run.text)
        return float(w) + size * 0.06, int(size * 0.88), int(size * 0.14)
    font = _run_font(run, size)
    if font is None:
        fb = ImageFont.load_default()
        return float(fb.getlength(run.text)), size, 0
    direction = _direction_for(run)
    try:
        width = font.getlength(_visual_text(run), direction=direction) if direction else font.getlength(_visual_text(run))
    except Exception:
        width = font.getlength(_visual_text(run))
    ascent, descent = font.getmetrics()
    return float(width), ascent, descent


@dataclass
class LineLayout:
    text: str
    runs: List[TextRun]
    width: float
    ascent: int
    descent: int

    @property
    def height(self) -> int:
        return self.ascent + self.descent


@dataclass
class TextLayout:
    lines: List[LineLayout]
    size: int
    line_gap: int
    stroke_width: int
    language: str
    direction: str = "ltr"

    @property
    def width(self) -> int:
        if not self.lines:
            return 0
        return int(max(l.width for l in self.lines)) + 2 * self.stroke_width

    @property
    def height(self) -> int:
        if not self.lines:
            return 0
        return sum(l.height for l in self.lines) + self.line_gap * (len(self.lines) - 1) + 2 * self.stroke_width


def _layout_line(text: str, language: str, size: int, user_font: Optional[str]) -> LineLayout:
    runs = segment_runs(text, language, user_font)
    width = 0.0
    asc = 0
    desc = 0
    for r in runs:
        w, a, d = _measure_run(r, size)
        width += w
        asc = max(asc, a)
        desc = max(desc, d)
    if not runs:
        asc, desc = int(size * 0.88), int(size * 0.14)
    return LineLayout(text, runs, width, asc, desc)


@lru_cache(maxsize=16384)
def _text_width(text: str, language: str, size: int, user_font: Optional[str]) -> float:
    return _layout_line(text, language, size, user_font).width


# ---------------------------------------------------------------------------
# Tokenization & wrapping
# ---------------------------------------------------------------------------


def _tokenize(paragraph: str, language: str) -> List[str]:
    info = get_language_info(language)
    has_cjk = any(char_script(c) in ("han", "kana", "cjk-punct") for c in paragraph)
    mode = info.wrap
    if mode == "space" and has_cjk and " " not in paragraph.strip():
        mode = "cjk"
    if mode == "space" and info.script == "kore" and " " not in paragraph.strip():
        mode = "cjk"  # long Korean phrase without spaces: allow syllable breaks

    tokens: List[str] = []
    if mode == "space":
        word = ""
        for ch in paragraph:
            word += ch
            if ch == " ":
                tokens.append(word)
                word = ""
        if word:
            tokens.append(word)
        return tokens

    if mode == "thai":
        for ch in paragraph:
            if tokens and (ch in _THAI_COMBINING or ch in _NO_LINE_START):
                tokens[-1] += ch
            else:
                tokens.append(ch)
        return tokens

    # CJK: one token per character, Latin words kept intact, kinsoku punctuation glued
    buf = ""
    for ch in paragraph:
        sc = char_script(ch)
        if sc in ("latin", "cyrillic", "greek") or (ch.isdigit()):
            buf += ch
            continue
        if buf:
            tokens.append(buf)
            buf = ""
        if tokens and (ch in _NO_LINE_START or sc in ("mark", "emoji-mod")):
            tokens[-1] += ch
        elif tokens and tokens[-1] and tokens[-1][-1] in _NO_LINE_END:
            tokens[-1] += ch
        else:
            tokens.append(ch)
    if buf:
        if tokens and buf and all(c in _NO_LINE_START for c in buf):
            tokens[-1] += buf
        else:
            tokens.append(buf)
    return tokens


class _WordTooLong(Exception):
    pass


def _greedy_wrap(tokens: List[str], max_width: float, measure, allow_break: bool = True) -> List[str]:
    lines: List[str] = []
    cur = ""
    for tok in tokens:
        candidate = cur + tok
        if not cur or measure(candidate.rstrip()) <= max_width:
            cur = candidate
            continue
        lines.append(cur.rstrip())
        cur = tok.lstrip() if tok.strip() else ""
    if cur.strip():
        lines.append(cur.rstrip())
    # Break any single overlong token character-by-character
    final: List[str] = []
    for line in lines:
        if measure(line) <= max_width or len(line) <= 1:
            final.append(line)
            continue
        if not allow_break:
            raise _WordTooLong(line)
        piece = ""
        for ch in line:
            if piece and measure(piece + ch) > max_width:
                final.append(piece)
                piece = ch
            else:
                piece += ch
        if piece:
            final.append(piece)
    return final


def wrap_text(
    text: str,
    language: str,
    size: int,
    max_width: float,
    user_font: Optional[str] = None,
    balance: bool = True,
    allow_word_break: bool = True,
) -> List[str]:
    """Wrap text into lines that fit max_width using language-aware break rules.

    With ``allow_word_break=False`` a word wider than the line raises ``_WordTooLong`` so callers
    can shrink the font instead of splitting the word.
    """
    language = normalize_language(language)

    def measure(s: str) -> float:
        return _text_width(s, language, size, user_font)

    lines: List[str] = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            continue
        tokens = _tokenize(paragraph, language)
        para_lines = _greedy_wrap(tokens, max_width, measure, allow_word_break)
        if balance and len(para_lines) >= 2:
            # Shrink width while line count stays the same → visually balanced lines
            lo, hi = max_width * 0.45, max_width
            best = para_lines
            for _ in range(8):
                mid = (lo + hi) / 2.0
                try:
                    trial = _greedy_wrap(tokens, mid, measure, allow_break=False)
                except _WordTooLong:
                    lo = mid
                    continue
                if len(trial) <= len(para_lines):
                    best = trial
                    hi = mid
                else:
                    lo = mid
            para_lines = best
        lines.extend(para_lines)
    return lines


def fit_text(
    text: str,
    language: str = "zh-CN",
    max_width: float = 216,
    max_height: float = 80,
    start_size: int = 26,
    min_size: int = 12,
    max_lines: int = 2,
    user_font: Optional[str] = None,
    stroke_ratio: float = 0.0,
    line_gap_ratio: float = 0.10,
) -> TextLayout:
    """Find the largest font size whose wrapped text fits inside (max_width × max_height)."""
    language = normalize_language(language)
    info = get_language_info(language)
    size = max(min_size, int(start_size))
    best: Optional[TextLayout] = None
    step = max(1, int(round(start_size / 26.0)))
    while size >= min_size:
        stroke = int(round(size * stroke_ratio))
        avail_w = max(8.0, max_width - 2 * stroke)
        last_chance = size - step < min_size
        try:
            lines = wrap_text(text, language, size, avail_w, user_font, allow_word_break=last_chance)
        except _WordTooLong:
            size -= step
            continue
        layout = TextLayout(
            [_layout_line(l, language, size, user_font) for l in lines],
            size,
            int(round(size * line_gap_ratio)),
            stroke,
            language,
            info.direction,
        )
        best = layout
        if len(lines) <= max_lines and layout.width <= max_width + 1 and layout.height <= max_height + 1:
            return layout
        size -= step
    return best or TextLayout([], min_size, 0, 0, language, info.direction)


def draw_text_layout(
    img: Image.Image,
    layout: TextLayout,
    center_x: float,
    top_y: float,
    fill: Tuple[int, int, int, int],
    stroke_fill: Optional[Tuple[int, int, int, int]] = None,
    align: str = "center",
    left_x: Optional[float] = None,
    max_chars: Optional[int] = None,
) -> Tuple[int, int, int, int]:
    """Draw a laid-out text block. ``max_chars`` reveals only the first N characters (typewriter)."""
    draw = ImageDraw.Draw(img)
    y = top_y + layout.stroke_width
    remaining = max_chars if max_chars is not None else 10**9
    x_min, y_min, x_max, y_max = 10**9, 10**9, -10**9, -10**9
    for line in layout.lines:
        if align == "left" and left_x is not None:
            x = left_x + layout.stroke_width
        else:
            x = center_x - line.width / 2.0
        baseline = y + line.ascent
        runs = list(reversed(line.runs)) if layout.direction == "rtl" else line.runs
        for run in runs:
            if remaining <= 0:
                break
            text = run.text if len(run.text) <= remaining else run.text[:remaining]
            remaining -= len(text)
            sub = TextRun(text, run.path, run.index, run.script, run.kind)
            w, a, _ = _measure_run(sub, layout.size)
            if run.kind == "emoji":
                em = _render_emoji(run.path or "", text, int(layout.size * 0.95))
                if em is not None:
                    py = int(round(baseline - a))
                    img.alpha_composite(em, (int(round(x)), max(0, py))) if img.mode == "RGBA" else img.paste(em, (int(x), py), em)
            else:
                font = _run_font(sub, layout.size)
                if font is not None:
                    kwargs = {}
                    direction = _direction_for(sub)
                    if direction:
                        kwargs["direction"] = direction
                    draw.text(
                        (x, baseline),
                        _visual_text(sub),
                        font=font,
                        fill=fill,
                        anchor="ls",
                        stroke_width=layout.stroke_width,
                        stroke_fill=stroke_fill if layout.stroke_width > 0 else None,
                        **kwargs,
                    )
            x_min = min(x_min, int(x))
            x_max = max(x_max, int(x + w))
            x += w
        y_min = min(y_min, int(y))
        y_max = max(y_max, int(y + line.height))
        y += line.height + layout.line_gap
    return x_min, y_min, x_max, y_max


# ---------------------------------------------------------------------------
# Backwards-compatible helpers + caption API
# ---------------------------------------------------------------------------


def calculate_text_layout(
    draw: ImageDraw.ImageDraw,
    caption: str,
    font_path: Optional[str],
    max_width: int,
    start_font_size: int = 26,
    min_font_size: int = 14,
    language: str = "zh-CN",
) -> Tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont, list[str]]:
    """Legacy API: return (font, lines) for a caption fitted to max_width (≤2 lines)."""
    layout = fit_text(
        caption,
        language,
        max_width=max_width,
        max_height=10**6,
        start_size=start_font_size,
        min_size=min_font_size,
        max_lines=2,
        user_font=font_path,
    )
    return load_font(font_path, layout.size), [l.text for l in layout.lines]


def caption_block_height(canvas_w: int, caption: str, language: str = "zh-CN", style: Optional[str] = None) -> int:
    preset = resolve_style_preset(style or "real-cutout")
    scale = canvas_w / BASE_CANVAS
    layout = fit_text(
        caption,
        language,
        max_width=canvas_w - 24 * scale,
        max_height=canvas_w * 0.36,
        start_size=int(round(preset.typography.start_font_size * scale)),
        min_size=int(round(11 * scale)),
        max_lines=3,
        stroke_ratio=preset.typography.stroke_width / float(max(1, preset.typography.start_font_size)),
    )
    return layout.height


def add_caption_to_image(
    img: Image.Image,
    caption: str,
    font_path: Optional[str] = None,
    text_color: Optional[Tuple[int, int, int, int]] = None,
    stroke_color: Optional[Tuple[int, int, int, int]] = None,
    stroke_width: Optional[int] = None,
    bottom_margin: int = 12,
    style: Optional[str | StylePreset] = None,
    language: str = "zh-CN",
) -> Image.Image:
    """Render a high-contrast stroked caption at the bottom centre (any language, auto-wrapped).

    ``bottom_margin`` and the style font sizes are expressed for a 240px canvas and scaled.
    Only one language is ever rendered per sticker.
    """
    if not caption:
        return img

    preset = style if isinstance(style, StylePreset) else resolve_style_preset(style or "real-cutout")
    typo = preset.typography
    fill = text_color if text_color is not None else hex_to_rgba(typo.text_color)
    stroke_fill = stroke_color if stroke_color is not None else hex_to_rgba(typo.stroke_color)
    base_stroke = stroke_width if stroke_width is not None else typo.stroke_width

    result = img.convert("RGBA")
    w, h = result.size
    scale = w / BASE_CANVAS
    max_w = w - 24 * scale
    stroke_ratio = base_stroke / float(max(1, typo.start_font_size))
    y_bottom = h - bottom_margin * scale

    if caption:
        info = get_language_info(language)
        max_lines = 3 if info.wrap == "space" and len(caption) > 14 else 2
        main = fit_text(
            caption,
            language,
            max_width=max_w,
            max_height=h * 0.36,
            start_size=int(round(typo.start_font_size * scale)),
            min_size=int(round(11 * scale)),
            max_lines=max_lines,
            user_font=font_path,
            stroke_ratio=stroke_ratio,
        )
        top = y_bottom - main.height
        draw_text_layout(result, main, w / 2.0, top, fill, stroke_fill)

    return result
