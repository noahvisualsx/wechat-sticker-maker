"""Transparency handling, background removal, and edge safety margins."""

from __future__ import annotations

from PIL import Image


def ensure_alpha_channel(img: Image.Image) -> Image.Image:
    """Ensure image is RGBA."""
    if img.mode != "RGBA":
        return img.convert("RGBA")
    return img


def remove_matte_background(
    img: Image.Image,
    threshold: int = 245,
    feather: int = 10,
) -> Image.Image:
    """If image has no transparency (or mostly opaque background), keyed out near-white background."""
    img = ensure_alpha_channel(img)
    # Check if already has transparent pixels
    alpha_extrema = img.getchannel("A").getextrema()
    if alpha_extrema[0] < 10:
        # Already has meaningful transparency
        return img

    # Key out near-white background (RGB all >= threshold)
    r, g, b, a = img.split()
    r_data = r.load()
    g_data = g.load()
    b_data = b.load()
    a_data = a.load()

    w, h = img.size
    for y in range(h):
        for x in range(w):
            rv, gv, bv = r_data[x, y], g_data[x, y], b_data[x, y]
            min_val = min(rv, gv, bv)
            if min_val >= threshold:
                # Fully transparent
                a_data[x, y] = 0
            elif min_val > (threshold - feather):
                # Smooth feather
                ratio = (min_val - (threshold - feather)) / float(feather)
                a_data[x, y] = int(255 * (1.0 - ratio))

    return Image.merge("RGBA", (r, g, b, a))


def apply_safe_margin(img: Image.Image, margin_px: int = 2) -> Image.Image:
    """Ensure character does not bleed into the very outer 2px boundary for WeChat stickers."""
    img = ensure_alpha_channel(img)
    w, h = img.size
    if w <= margin_px * 2 or h <= margin_px * 2:
        return img

    # Clear alpha at the 2px perimeter
    r, g, b, a = img.split()
    a_data = a.load()

    for x in range(w):
        for y in range(margin_px):
            a_data[x, y] = 0
            a_data[x, h - 1 - y] = 0
    for y in range(h):
        for x in range(margin_px):
            a_data[x, y] = 0
            a_data[w - 1 - x, y] = 0

    return Image.merge("RGBA", (r, g, b, a))
