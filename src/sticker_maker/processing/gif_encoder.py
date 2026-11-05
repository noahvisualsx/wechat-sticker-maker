"""GIF frame synthesis, encoding, and transparency optimization."""

from __future__ import annotations

import math
from pathlib import Path
from typing import List, Sequence, Tuple
from PIL import Image, ImageDraw


def synthesize_motion_frames(
    base_img: Image.Image,
    motion_type: str = "wave_hand",
    frames: int = 8,
) -> List[Image.Image]:
    """Generate subtle keyframe transformations from a base image to maintain strict identity stability."""
    base_rgba = base_img.convert("RGBA")
    w, h = base_rgba.size
    result_frames: List[Image.Image] = []

    for i in range(frames):
        # Create a new transparent frame
        frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        t = i / float(frames)
        phase = 2.0 * math.pi * t

        # Subtle bobbing / floating
        if motion_type in ("cheer_jump", "laugh_bounce"):
            dy = -abs(math.sin(phase)) * (h * 0.05)
            dx = 0
            scale_fac = 1.0 + 0.03 * math.sin(phase)
        elif motion_type in ("head_tilt", "sleepy_nod"):
            dy = math.sin(phase) * (h * 0.02)
            dx = math.sin(phase) * (w * 0.02)
            scale_fac = 1.0
        elif motion_type == "heart_beat":
            dy = 0
            dx = 0
            scale_fac = 1.0 + 0.04 * (math.sin(phase * 2) if math.sin(phase * 2) > 0 else 0)
        else:
            # Default subtle breathing / bobbing
            dy = math.sin(phase) * (h * 0.02)
            dx = 0
            scale_fac = 1.0 + 0.01 * math.sin(phase)

        # Scale and paste base
        if scale_fac != 1.0:
            sw = max(1, int(round(w * scale_fac)))
            sh = max(1, int(round(h * scale_fac)))
            scaled = base_rgba.resize((sw, sh), Image.Resampling.BILINEAR)
            px = int((w - sw) / 2.0 + dx)
            py = int((h - sh) / 2.0 + dy)
            frame.paste(scaled, (px, py), scaled)
        else:
            frame.paste(base_rgba, (int(dx), int(dy)), base_rgba)

        # Draw motion accents (e.g. blushing, hearts, sweatdrops, tears)
        draw = ImageDraw.Draw(frame)
        if "blush" in motion_type:
            # Pulsing blush
            blush_alpha = int(120 + 100 * math.sin(phase))
            cx, cy = w // 2, h // 2 + int(dy)
            draw.ellipse([cx - 40, cy + 10, cx - 20, cy + 25], fill=(247, 189, 201, blush_alpha))
            draw.ellipse([cx + 20, cy + 10, cx + 40, cy + 25], fill=(247, 189, 201, blush_alpha))
        elif "tear" in motion_type:
            # Falling teardrop
            cx, cy = w // 2, h // 2 + int(dy)
            tear_y = cy + int((i % 4) * (h * 0.06))
            draw.ellipse([cx - 30, tear_y, cx - 22, tear_y + 12], fill=(120, 180, 255, 200))
        elif "heart" in motion_type:
            # Small floating hearts
            heart_scale = 1.0 + 0.3 * math.sin(phase)
            cx, cy = int(w * 0.75), int(h * 0.3 + dy)
            draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 105, 180, 220))

        result_frames.append(frame)

    return result_frames


def _convert_rgba_to_gif_palette(img: Image.Image) -> Image.Image:
    """Convert RGBA image to P mode with a dedicated transparent color at index 0."""
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")

    # Quantize RGB with adaptive palette of up to 254 colors, reserving 0 for transparent
    rgb = rgba.convert("RGB")
    p_img = rgb.quantize(colors=254, method=Image.Quantize.FASTOCTREE)

    # Shift palette entries by 1 so index 0 is free for transparency
    palette = p_img.getpalette()[: 254 * 3]
    # Transparent color at index 0 (set to black or white, won't be drawn)
    new_palette = [0, 0, 0] + palette + [0] * (768 - 3 - len(palette))

    # Shift pixel indices by 1
    if hasattr(p_img, "get_flattened_data"):
        p_data = list(p_img.get_flattened_data())
    else:
        p_data = list(p_img.getdata())

    if hasattr(alpha, "get_flattened_data"):
        alpha_data = list(alpha.get_flattened_data())
    else:
        alpha_data = list(alpha.getdata())

    new_data = []
    for p_val, a_val in zip(p_data, alpha_data):
        if a_val < 128:
            new_data.append(0)
        else:
            new_data.append(min(255, p_val + 1))

    res = Image.new("P", img.size)
    res.putpalette(new_palette)
    res.putdata(new_data)
    res.info["transparency"] = 0
    return res


def encode_gif(
    frames: Sequence[Image.Image],
    output_path: Path,
    frame_duration_ms: int = 180,
    loop: int = 0,
) -> Path:
    """Encode a sequence of RGBA frames into a looping transparent GIF."""
    if len(frames) < 2:
        raise ValueError("GIF requires at least 2 frames for animation")

    paletted_frames = [_convert_rgba_to_gif_palette(f) for f in frames]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(".tmp.gif")

    paletted_frames[0].save(
        tmp_path,
        format="GIF",
        save_all=True,
        append_images=paletted_frames[1:],
        duration=[frame_duration_ms] * len(paletted_frames),
        loop=loop,
        disposal=2,  # Restore to background
        transparency=0,
        optimize=True,
    )

    tmp_path.replace(output_path)
    return output_path
