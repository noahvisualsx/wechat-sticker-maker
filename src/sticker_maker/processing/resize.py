"""High-quality resizing and asset adaptation."""

from __future__ import annotations

from typing import Optional
from PIL import Image, ImageDraw

from ..styles import hex_to_rgba, resolve_style_preset


def fit_and_pad(
    img: Image.Image,
    target_size: tuple[int, int],
    resample: Image.Resampling = Image.Resampling.LANCZOS,
) -> Image.Image:
    """Proportionally scale image to fit within target_size and center on transparent canvas."""
    tw, th = target_size
    img = img.convert("RGBA")
    w, h = img.size

    scale = min(tw / float(w), th / float(h))
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))

    resized = img.resize((new_w, new_h), resample=resample)
    canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))

    offset_x = (tw - new_w) // 2
    offset_y = (th - new_h) // 2
    canvas.paste(resized, (offset_x, offset_y), resized)
    return canvas


def resize_sticker(img: Image.Image, size: tuple[int, int] = (240, 240)) -> Image.Image:
    """Downscale to 240x240 sticker standard."""
    return fit_and_pad(img, size)


def create_thumbnail(img: Image.Image, size: tuple[int, int] = (120, 120)) -> Image.Image:
    """Downscale to 120x120 thumbnail standard."""
    return fit_and_pad(img, size)


def create_icon(img: Image.Image, size: tuple[int, int] = (50, 50)) -> Image.Image:
    """Downscale to 50x50 icon standard."""
    return fit_and_pad(img, size)


def create_banner(
    img: Image.Image,
    size: tuple[int, int] = (750, 400),
    style: Optional[str] = None,
) -> Image.Image:
    """Adapt sticker visual to 750x400 banner standard with style-aware theme background."""
    tw, th = size
    preset = resolve_style_preset(style or "real-cutout")
    bg_rgba = hex_to_rgba(preset.banner_bg)
    canvas = Image.new("RGBA", (tw, th), bg_rgba)
    draw = ImageDraw.Draw(canvas)

    # Draw subtle style accent circles in banner background
    if preset.default_palette:
        accent_color = hex_to_rgba(preset.default_palette[min(1, len(preset.default_palette) - 1)], alpha=45)
        draw.ellipse([-60, -60, 220, 220], fill=accent_color)
        draw.ellipse([tw - 200, th - 180, tw + 60, th + 60], fill=accent_color)

    # Character placed at center
    char_size = (360, 360)
    scaled_char = fit_and_pad(img, char_size)
    offset_x = (tw - 360) // 2
    offset_y = (th - 360) // 2
    canvas.paste(scaled_char, (offset_x, offset_y), scaled_char)
    return canvas
