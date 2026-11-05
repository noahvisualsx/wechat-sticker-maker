"""File size optimization for PNG and GIF stickers."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageSequence


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
    """Optimize GIF file in-place if larger than max_bytes."""
    size = path.stat().st_size
    if size <= max_bytes:
        return size

    with Image.open(path) as img:
        frames = [f.copy().convert("RGBA") for f in ImageSequence.Iterator(img)]
        duration = img.info.get("duration", 180)
        loop = img.info.get("loop", 0)

    # Re-encode with fewer colors (e.g. 128 colors)
    reduced_frames = []
    for f in frames:
        p_frame = f.quantize(colors=128, method=Image.Quantize.FASTOCTREE)
        reduced_frames.append(p_frame)

    tmp = path.with_suffix(".opt.gif")
    reduced_frames[0].save(
        tmp,
        format="GIF",
        save_all=True,
        append_images=reduced_frames[1:],
        duration=duration,
        loop=loop,
        disposal=2,
        optimize=True,
    )

    if tmp.stat().st_size < size:
        tmp.replace(path)

    return path.stat().st_size
