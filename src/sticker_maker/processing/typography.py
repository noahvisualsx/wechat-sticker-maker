"""Chinese caption typography and text overlay."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from ..config import get_default_font_path

logger = logging.getLogger(__name__)


def load_font(font_path: Optional[str] = None, size: int = 24) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a truetype font, with fallback to system Chinese fonts or default."""
    candidates = []
    if font_path and Path(font_path).exists():
        candidates.append(font_path)

    sys_font = get_default_font_path()
    if sys_font:
        candidates.append(sys_font)

    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception as e:
            logger.warning("Could not load font at %s: %s", p, e)

    # Fallback to default
    logger.warning("No Chinese TrueType font found; falling back to default PIL font.")
    return ImageFont.load_default()


def calculate_text_layout(
    draw: ImageDraw.ImageDraw,
    caption: str,
    font_path: Optional[str],
    max_width: int,
    start_font_size: int = 26,
    min_font_size: int = 14,
) -> Tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont, list[str]]:
    """Determine best font size and line split to fit text within max_width."""
    font_size = start_font_size
    while font_size >= min_font_size:
        font = load_font(font_path, font_size)
        bbox = draw.textbbox((0, 0), caption, font=font)
        text_w = bbox[2] - bbox[0]
        if text_w <= max_width:
            return font, [caption]
        font_size -= 2

    # If still too wide, try splitting in 2 lines if caption length > 4
    if len(caption) >= 4:
        mid = len(caption) // 2
        lines = [caption[:mid], caption[mid:]]
        font_size = start_font_size - 4
        while font_size >= min_font_size:
            font = load_font(font_path, font_size)
            max_line_w = max(
                draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0]
                for line in lines
            )
            if max_line_w <= max_width:
                return font, lines
            font_size -= 2

    # Ultimate fallback with min size
    font = load_font(font_path, min_font_size)
    return font, [caption]


def add_caption_to_image(
    img: Image.Image,
    caption: str,
    font_path: Optional[str] = None,
    text_color: Tuple[int, int, int, int] = (40, 40, 40, 255),
    stroke_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    stroke_width: int = 3,
    bottom_margin: int = 12,
) -> Image.Image:
    """Render high-contrast captioned text at the bottom center of an image."""
    if not caption:
        return img

    result = img.convert("RGBA")
    w, h = result.size
    draw = ImageDraw.Draw(result)

    max_text_width = w - 24
    font, lines = calculate_text_layout(draw, caption, font_path, max_text_width)

    # Compute total text block height
    line_bboxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    line_heights = [b[3] - b[1] for b in line_bboxes]
    line_widths = [b[2] - b[0] for b in line_bboxes]
    line_spacing = 4
    total_text_h = sum(line_heights) + line_spacing * (len(lines) - 1)

    # Position text starting near bottom
    start_y = h - bottom_margin - total_text_h

    current_y = start_y
    for i, line in enumerate(lines):
        line_w = line_widths[i]
        line_x = (w - line_w) // 2
        # Adjust for bbox offset
        bbox = line_bboxes[i]
        adj_x = line_x - bbox[0]
        adj_y = current_y - bbox[1]

        # Draw stroke and fill
        draw.text(
            (adj_x, adj_y),
            line,
            font=font,
            fill=text_color,
            stroke_width=stroke_width,
            stroke_fill=stroke_color,
        )
        current_y += line_heights[i] + line_spacing

    return result
