"""High-quality resizing and asset adaptation."""

from __future__ import annotations

from PIL import Image


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


def create_banner(img: Image.Image, size: tuple[int, int] = (750, 400)) -> Image.Image:
    """Adapt sticker visual to 750x400 banner standard."""
    tw, th = size
    canvas = Image.new("RGBA", (tw, th), (255, 248, 240, 255))  # Soft pastel background

    # Character placed on right or center
    char_size = (360, 360)
    scaled_char = fit_and_pad(img, char_size)
    offset_x = (tw - 360) // 2
    offset_y = (th - 360) // 2
    canvas.paste(scaled_char, (offset_x, offset_y), scaled_char)
    return canvas
