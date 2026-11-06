"""Transparency handling, background removal, and edge safety margins."""

from __future__ import annotations

from collections import deque
from PIL import Image, ImageFilter


def ensure_alpha_channel(img: Image.Image) -> Image.Image:
    """Ensure image is RGBA."""
    if img.mode != "RGBA":
        return img.convert("RGBA")
    return img


def remove_matte_background(
    img: Image.Image,
    threshold: int = 240,
    feather: int = 12,
) -> Image.Image:
    """Key out exterior connected near-white/matte background using border-seeded flood-fill.

    Unlike global thresholding, border-seeded BFS preserves white fur, eyes, and clothing
    inside the character silhouette while cleanly removing opaque background corners.
    """
    img = ensure_alpha_channel(img)
    # Check if already has meaningful transparent pixels
    alpha_extrema = img.getchannel("A").getextrema()
    if alpha_extrema[0] < 10:
        return img

    r, g, b, a = img.split()
    r_data = r.load()
    g_data = g.load()
    b_data = b.load()
    a_data = a.load()

    w, h = img.size
    visited = bytearray(w * h)
    queue: deque[tuple[int, int]] = deque()

    def is_bg_candidate(x: int, y: int) -> bool:
        rv, gv, bv = r_data[x, y], g_data[x, y], b_data[x, y]
        return min(rv, gv, bv) >= (threshold - feather)

    # Seed from border pixels that look like matte background
    for x in range(w):
        for y in (0, h - 1):
            idx = y * w + x
            if not visited[idx] and is_bg_candidate(x, y):
                visited[idx] = 1
                queue.append((x, y))
    for y in range(1, h - 1):
        for x in (0, w - 1):
            idx = y * w + x
            if not visited[idx] and is_bg_candidate(x, y):
                visited[idx] = 1
                queue.append((x, y))

    # Flood-fill connected exterior background
    while queue:
        cx, cy = queue.popleft()
        rv, gv, bv = r_data[cx, cy], g_data[cx, cy], b_data[cx, cy]
        min_val = min(rv, gv, bv)

        if min_val >= threshold:
            a_data[cx, cy] = 0
            # Only expand further from solid background pixels
            for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                if 0 <= nx < w and 0 <= ny < h:
                    nidx = ny * w + nx
                    if not visited[nidx] and is_bg_candidate(nx, ny):
                        visited[nidx] = 1
                        queue.append((nx, ny))
        elif min_val > (threshold - feather):
            # Feather edge pixel smoothly without expanding into character interior
            ratio = (min_val - (threshold - feather)) / float(feather)
            a_data[cx, cy] = int(255 * (1.0 - ratio))

    return Image.merge("RGBA", (r, g, b, a))


def apply_die_cut_border(
    img: Image.Image,
    border_px: int = 4,
    border_color: tuple[int, int, int, int] = (255, 255, 255, 255),
) -> Image.Image:
    """Add a smooth WeChat-style white die-cut sticker border around the subject silhouette.

    Essential for real-person photo cutout stickers so hair and clothing stand out cleanly
    against both light and dark WeChat chat backgrounds.
    """
    if border_px <= 0:
        return ensure_alpha_channel(img)

    rgba = ensure_alpha_channel(img)
    alpha = rgba.getchannel("A")
    if alpha.getextrema()[1] == 0:
        return rgba

    # Fast smooth dilation: gaussian blur + soft threshold (≈ border_px outward, rounded corners).
    # Equivalent to a circular MaxFilter but O(n) instead of O(n·k²), important at 720px masters.
    solid = alpha.point(lambda p: 255 if p > 24 else 0)
    sigma = max(0.6, float(border_px) / 2.2)
    blurred = solid.filter(ImageFilter.GaussianBlur(radius=sigma))
    border_alpha = blurred.point(lambda v: 0 if v <= 3 else (255 if v >= 12 else int((v - 3) * 255 / 9)))

    border_layer = Image.new("RGBA", rgba.size, border_color[:3] + (0,))
    border_layer.putalpha(border_alpha)
    return Image.alpha_composite(border_layer, rgba)


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
