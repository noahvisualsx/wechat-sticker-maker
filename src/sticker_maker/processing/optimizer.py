"""File size optimization for PNG and GIF stickers."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageSequence

from .gif_encoder import encode_gif


def optimize_png(path: Path, max_bytes: int = 500_000) -> int:
    """Optimize PNG file in-place if larger than max_bytes."""
    size = path.stat().st_size
    if size <= max_bytes:
        return size

    with Image.open(path) as img:
        img_rgba = img.convert("RGBA")
        # Try standard optimization
        tmp = path.with_suffix(".opt.png")
        img_rgba.save(tmp, format="PNG", optimize=True, compress_level=9)
        if tmp.stat().st_size <= max_bytes:
            tmp.replace(path)
            return path.stat().st_size

        # If still too large, quantize to 256-color PNG8 with alpha
        p_img = img_rgba.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
        p_img.save(tmp, format="PNG", optimize=True)
        tmp.replace(path)

    return path.stat().st_size


def optimize_gif(path: Path, max_bytes: int = 500_000) -> int:
    """Optimize GIF file in-place if larger than max_bytes while preserving 1-bit transparency."""
    size = path.stat().st_size
    if size <= max_bytes:
        return size

    with Image.open(path) as img:
        frames = [f.copy().convert("RGBA") for f in ImageSequence.Iterator(img)]
        duration = img.info.get("duration", 180)
        loop = img.info.get("loop", 0)

    tmp = path.with_suffix(".opt.gif")
    for max_colors in (128, 64, 32):
        encode_gif(frames, tmp, frame_duration_ms=duration, loop=loop, max_colors=max_colors)
        new_size = tmp.stat().st_size
        if new_size < size:
            tmp.replace(path)
            size = new_size
        else:
            tmp.unlink(missing_ok=True)
        if size <= max_bytes:
            break

    return path.stat().st_size
