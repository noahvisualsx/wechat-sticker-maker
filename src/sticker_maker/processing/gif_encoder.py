"""AI keyframe & 2x2 action sprite-sheet assembler and transparent GIF encoder.

All character motion (waving hands, blinking eyes, nodding, facial expressions) is drawn by
the AI image generator (Codex built-in image generation / GPT Image) across multiple keyframes
or a 2x2 action sprite sheet. Python only slices, removes the background, aligns the lower-torso
baseline, adds die-cut borders, multilingual captions / speech bubbles, and encodes animations.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import List, Optional, Sequence, Tuple
from PIL import Image, ImageDraw, ImageSequence

from ..schemas import TextSpec
from ..styles import resolve_style_preset
from .alpha import apply_safe_margin
from .compose import (
    CharRegion,
    compose_sticker_frames,
    crop_characters,
    default_region,
    expand_loop,
    place_characters,
)
from .typography import add_caption_to_image


def align_ai_keyframes(
    raw_frames: Sequence[Image.Image],
    target_size: Tuple[int, int] = (240, 240),
    die_cut_border_px: int = 0,
    target_frames: int = 8,
    region: Optional[CharRegion] = None,
    clean: bool = True,
) -> List[Image.Image]:
    """Clean, scale-normalize and baseline-align AI-generated keyframes (no text overlay).

    The character's lower torso stays anchored while AI-drawn hands, eyes and expressions animate.
    ``die_cut_border_px`` is expressed for a 240px canvas and scaled to ``target_size``.
    """
    if not raw_frames:
        raise ValueError("raw_frames must contain at least 1 keyframe image")
    crops = crop_characters(raw_frames, clean=clean)
    keyframes = place_characters(crops, target_size, region or default_region(target_size, True), die_cut_border_px)
    return expand_loop(keyframes, target_frames)


def slice_sprite_sheet(sheet_img: Image.Image, rows: int = 2, cols: int = 2) -> List[Image.Image]:
    """Slice a rows×cols action sheet (row-major order) and trim inner seams."""
    rgba = sheet_img.convert("RGBA")
    sw, sh = rgba.size
    cw, ch = sw // cols, sh // rows
    seam = max(2, min(sw, sh) // 200)
    cells: List[Image.Image] = []
    for r in range(rows):
        for c in range(cols):
            cells.append(rgba.crop((c * cw + seam, r * ch + seam, (c + 1) * cw - seam, (r + 1) * ch - seam)))
    return cells


def slice_and_align_sprite_sheet(
    sheet_img: Image.Image,
    target_size: Tuple[int, int] = (240, 240),
    die_cut_border_px: int = 0,
    target_frames: int = 8,
) -> List[Image.Image]:
    """Slice a 2x2 4-frame AI animation sprite sheet, align lower-torso anchors, ping-pong loop."""
    return align_ai_keyframes(
        slice_sprite_sheet(sheet_img),
        target_size=target_size,
        die_cut_border_px=die_cut_border_px,
        target_frames=target_frames,
    )


def build_text_spec(
    caption: str = "",
    language: str = "zh-CN",
    bubble_text: str = "",
    bubble_shape: str = "round",
    bubble_position: str = "auto",
    bubble_animation: str = "none",
    text_layout: Optional[str] = None,
) -> TextSpec:
    """Convenience builder used by CLI/Codex helpers."""
    if text_layout is None or text_layout == "auto":
        if bubble_text and caption:
            text_layout = "both"
        elif bubble_text:
            text_layout = "bubble"
        elif caption:
            text_layout = "caption"
        else:
            text_layout = "none"
    return TextSpec(
        language=language,
        layout=text_layout,
        caption=caption,
        bubble_text=bubble_text,
        bubble_shape=bubble_shape,
        bubble_position=bubble_position,
        bubble_animation=bubble_animation,
    )


def _finalize_and_encode(
    frames: List[Image.Image],
    gif_output_path: Path,
    static_output_path: Optional[Path],
    target_size: Tuple[int, int],
    frame_duration_ms: int,
    loop: int,
) -> Path:
    final = [apply_safe_margin(f.resize(target_size, Image.Resampling.LANCZOS) if f.size != target_size else f, 2) for f in frames]
    if static_output_path is not None:
        static_output_path.parent.mkdir(parents=True, exist_ok=True)
        final[0].save(static_output_path, format="PNG")
    return encode_gif(final, gif_output_path, frame_duration_ms=frame_duration_ms, loop=loop)


def assemble_gif_from_sprite_sheet(
    sheet_path: Path,
    gif_output_path: Path,
    caption: str = "",
    style: str = "real-cutout",
    static_output_path: Optional[Path] = None,
    font_path: Optional[str] = None,
    frame_duration_ms: int = 150,
    loop: int = 0,
    target_frames: int = 8,
    target_size: Tuple[int, int] = (240, 240),
    language: str = "zh-CN",
    bubble_text: str = "",
    bubble_shape: str = "round",
    bubble_position: str = "auto",
    bubble_animation: str = "none",
    text_layout: Optional[str] = None,
    master_size: int = 720,
) -> Path:
    """One-step helper for Codex: 2x2 AI action sheet → aligned frames + caption/bubble → GIF (+PNG)."""
    with Image.open(sheet_path) as sheet_img:
        cells = slice_sprite_sheet(sheet_img)
    spec = build_text_spec(
        caption, language, bubble_text, bubble_shape, bubble_position, bubble_animation,
        text_layout,
    )
    frames = compose_sticker_frames(cells, spec, style, (master_size, master_size), target_frames, font_path)
    return _finalize_and_encode(frames, gif_output_path, static_output_path, target_size, frame_duration_ms, loop)


def assemble_gif_from_keyframe_files(
    frame_paths: Sequence[Path],
    gif_output_path: Path,
    caption: str = "",
    style: str = "real-cutout",
    static_output_path: Optional[Path] = None,
    font_path: Optional[str] = None,
    frame_duration_ms: int = 150,
    loop: int = 0,
    target_frames: int = 8,
    target_size: Tuple[int, int] = (240, 240),
    language: str = "zh-CN",
    bubble_text: str = "",
    bubble_shape: str = "round",
    bubble_position: str = "auto",
    bubble_animation: str = "none",
    text_layout: Optional[str] = None,
    master_size: int = 720,
) -> Path:
    """One-step helper for Codex: 2–8 AI keyframe PNGs → aligned frames + caption/bubble → GIF (+PNG)."""
    raw_imgs: List[Image.Image] = []
    for p in frame_paths:
        with Image.open(p) as img:
            raw_imgs.append(img.convert("RGBA"))
    spec = build_text_spec(
        caption, language, bubble_text, bubble_shape, bubble_position, bubble_animation,
        text_layout,
    )
    frames = compose_sticker_frames(raw_imgs, spec, style, (master_size, master_size), target_frames, font_path)
    return _finalize_and_encode(frames, gif_output_path, static_output_path, target_size, frame_duration_ms, loop)


def synthesize_motion_frames(
    base_img: Image.Image,
    motion_type: str = "wave_hand",
    frames: int = 8,
) -> List[Image.Image]:
    """Emergency-only fallback when no AI keyframes exist: adds small corner mood accents without
    distorting, floating, or re-drawing the character. Never used when AI frames are available."""
    base_rgba = base_img.convert("RGBA")
    w, h = base_rgba.size
    s = w / 240.0
    result_frames: List[Image.Image] = []

    for i in range(frames):
        phase = 2.0 * math.pi * i / float(max(1, frames))
        frame = base_rgba.copy()
        draw = ImageDraw.Draw(frame)
        ax = int(w * 0.80)
        ay = int(h * 0.20 - math.sin(phase) * 5.0 * s)
        r = max(3, int((5 + 2 * math.sin(phase)) * s))
        if "tear" in motion_type or "sweat" in motion_type or "cry" in motion_type:
            drop_y = int(h * 0.24 + (i % 4) * 5 * s)
            draw.ellipse([ax - 4 * s, drop_y, ax + 4 * s, drop_y + 10 * s], fill=(100, 185, 255, 225))
        elif "steam" in motion_type or "shock" in motion_type or "rage" in motion_type:
            draw.line([(ax - r, ay), (ax + r, ay)], fill=(235, 70, 70, 230), width=max(2, int(2 * s)))
            draw.line([(ax, ay - r), (ax, ay + r)], fill=(235, 70, 70, 230), width=max(2, int(2 * s)))
        else:
            draw.ellipse([ax - r, ay - r, ax + r, ay + r], fill=(255, 195, 110, 220))
        result_frames.append(frame)

    return result_frames


def _convert_rgba_to_gif_palette(img: Image.Image, max_colors: int = 254) -> Image.Image:
    """Convert RGBA image to P mode with a dedicated transparent color at index 0 (vectorized)."""
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")

    colors = max(2, min(254, max_colors))
    matte = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(matte, rgba).convert("RGB")
    p_img = composited.quantize(colors=colors, method=Image.Quantize.FASTOCTREE)

    raw_palette = p_img.getpalette() or []
    palette = raw_palette[: colors * 3]
    new_palette = [0, 0, 0] + palette + [0] * max(0, 768 - 3 - len(palette))

    indices = Image.frombytes("L", p_img.size, p_img.tobytes())
    shifted = indices.point(lambda v: min(255, v + 1))
    opaque = alpha.point(lambda a: 255 if a >= 128 else 0)
    merged = Image.composite(shifted, Image.new("L", p_img.size, 0), opaque)

    res = Image.frombytes("P", img.size, merged.tobytes())
    res.putpalette(new_palette[:768])
    res.info["transparency"] = 0
    return res


def encode_gif(
    frames: Sequence[Image.Image],
    output_path: Path,
    frame_duration_ms: int = 150,
    loop: int = 0,
    max_colors: int = 254,
) -> Path:
    """Encode a sequence of RGBA frames into a looping transparent GIF."""
    if len(frames) < 2:
        raise ValueError("GIF requires at least 2 frames for animation")

    paletted_frames = [_convert_rgba_to_gif_palette(f, max_colors=max_colors) for f in frames]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(".tmp.gif")

    paletted_frames[0].save(
        tmp_path,
        format="GIF",
        save_all=True,
        append_images=paletted_frames[1:],
        duration=[frame_duration_ms] * len(paletted_frames),
        loop=loop,
        disposal=2,
        transparency=0,
        optimize=True,
    )

    tmp_path.replace(output_path)
    return output_path


def add_animated_caption_to_frames(
    frames: Sequence[Image.Image],
    caption: str,
    font_path: Optional[str] = None,
    style: Optional[str] = None,
    motion_type: str = "",
    language: str = "zh-CN",
) -> List[Image.Image]:
    """Render a stable caption (any language) at the same position on every frame."""
    if not frames:
        return []
    preset = resolve_style_preset(style or "real-cutout")
    cap_anim = preset.caption_animation
    total = max(1, len(frames))
    result: List[Image.Image] = []
    cache: dict = {}
    for idx, f in enumerate(frames):
        phase = 2.0 * math.pi * (idx / float(total))
        bottom_margin = 12
        if cap_anim == "bounce":
            bottom_margin = 12 + int(round(abs(math.sin(phase)) * 3))
        elif cap_anim == "shake":
            bottom_margin = 12 + (2 if idx % 2 == 0 else 0)
        elif cap_anim == "pulse":
            bottom_margin = 12 + int(round(math.sin(phase) * 1))
        key = (bottom_margin, f.size)
        if key not in cache:
            cache[key] = add_caption_to_image(
                Image.new("RGBA", f.size, (0, 0, 0, 0)),
                caption,
                font_path=font_path,
                bottom_margin=bottom_margin,
                style=preset,
                language=language,
            )
        result.append(apply_safe_margin(Image.alpha_composite(f.convert("RGBA"), cache[key]), 2))
    return result


def load_gif_frames(raw_gif_path: Path) -> Tuple[List[Image.Image], int]:
    with Image.open(raw_gif_path) as img:
        duration = int(img.info.get("duration", 150) or 150)
        frames = [f.copy().convert("RGBA") for f in ImageSequence.Iterator(img)]
    return frames, duration


def postprocess_raw_gif(
    raw_gif_path: Path,
    output_path: Path,
    caption: str,
    font_path: Optional[str] = None,
    target_size: Tuple[int, int] = (240, 240),
    frame_duration_ms: Optional[int] = None,
    loop: int = 0,
    style: Optional[str] = None,
    text_spec: Optional[TextSpec] = None,
) -> Path:
    """Post-process a raw provider GIF: clean background, align, die-cut border, caption/bubble, encode."""
    raw_frames, orig_duration = load_gif_frames(raw_gif_path)
    spec = text_spec or build_text_spec(caption=caption)
    master = max(target_size[0], 480)
    frames = compose_sticker_frames(raw_frames, spec, style, (master, master), len(raw_frames), font_path)
    final = [apply_safe_margin(f.resize(target_size, Image.Resampling.LANCZOS), 2) for f in frames]
    return encode_gif(final, output_path, frame_duration_ms=frame_duration_ms or orig_duration or 150, loop=loop)
