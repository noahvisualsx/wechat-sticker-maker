"""Source image validation and character identity analysis."""

from __future__ import annotations

import base64
import hashlib
import json
import logging
from pathlib import Path
from typing import List, Optional
import requests
from PIL import Image, ImageOps

from .config import AppSettings
from .schemas import CharacterBible, RenderStyle, sanitize_id
from .styles import resolve_style_preset

logger = logging.getLogger(__name__)


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def normalize_source_image(source_path: Path, target_path: Path) -> Path:
    """Validate, fix EXIF orientation, and normalize source image to PNG."""
    if not source_path.exists():
        raise FileNotFoundError(f"Source image not found: {source_path}")

    try:
        with Image.open(source_path) as img:
            # Fix EXIF orientation if present
            transposed = ImageOps.exif_transpose(img)
            if transposed is None:
                transposed = img.copy()
            # Ensure RGBA or RGB
            if transposed.mode not in ("RGB", "RGBA"):
                transposed = transposed.convert("RGBA")
            target_path.parent.mkdir(parents=True, exist_ok=True)
            transposed.save(target_path, format="PNG")
    except Exception as e:
        raise ValueError(f"Cannot decode or process source image {source_path}: {e}") from e

    return target_path


def extract_dominant_palette(image_path: Path, count: int = 3) -> List[str]:
    """Extract dominant hex colors from the central subject of the source image."""
    default_palette = ["#FFF6EA", "#F7BDC9", "#987C7B"]
    try:
        with Image.open(image_path) as img:
            rgba = img.convert("RGBA")
            w, h = rgba.size
            # Crop central 70% region to focus on the main subject
            margin_x, margin_y = int(w * 0.15), int(h * 0.15)
            if w > 20 and h > 20:
                rgba = rgba.crop((margin_x, margin_y, w - margin_x, h - margin_y))
            rgba.thumbnail((128, 128))

            # Filter out transparent pixels
            pixels = [
                (r, g, b)
                for r, g, b, a in (
                    rgba.get_flattened_data() if hasattr(rgba, "get_flattened_data") else rgba.getdata()
                )
                if a >= 128
            ]
            if not pixels:
                return default_palette

            sample_img = Image.new("RGB", (len(pixels), 1))
            sample_img.putdata(pixels)
            quantized = sample_img.quantize(colors=max(count + 2, 5), method=Image.Quantize.FASTOCTREE)
            palette_raw = quantized.getpalette() or []
            color_counts = sorted(quantized.getcolors() or [], key=lambda x: x[0], reverse=True)

            hex_colors: List[str] = []
            for _, idx in color_counts:
                base = idx * 3
                if base + 2 < len(palette_raw):
                    r, g, b = palette_raw[base], palette_raw[base + 1], palette_raw[base + 2]
                    hex_str = f"#{r:02X}{g:02X}{b:02X}"
                    if hex_str not in hex_colors:
                        hex_colors.append(hex_str)
                if len(hex_colors) >= count:
                    break

            return hex_colors if hex_colors else default_palette
    except Exception as e:
        logger.debug("Palette extraction fallback: %s", e)
        return default_palette


def analyze_character_with_vision(
    source_image: Path,
    api_key: str,
    base_url: str = "https://api.openai.com/v1",
    vision_model: str = "gpt-4o-mini",
    timeout: int = 45,
) -> Optional[dict]:
    """Use OpenAI Vision model to extract observable character traits for CharacterBible."""
    if not api_key:
        return None

    try:
        b64_img = base64.b64encode(source_image.read_bytes()).decode("ascii")
        url = f"{base_url.rstrip('/')}/chat/completions"
        system_prompt = (
            "You are a real-person portrait identity analyzer for a sticker maker. "
            "Inspect the person in the photo and return strict JSON with keys: "
            "'subject_type' (always 'human-portrait'), "
            "'identity_facts' (array of 4 concise observable visual facts: hairstyle/hair color, facial bone structure & eye/brow shape, skin tone, outfit/glasses/accessories), "
            "and 'locked_attributes' (array of 4 attributes that must remain photorealistic and identical across all stickers). "
            "Only describe clearly visible traits. Never infer sensitive personal attributes."
        )
        payload = {
            "model": vision_model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this reference image for sticker character consistency."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_img}"}},
                    ],
                },
            ],
            "max_tokens": 350,
        }
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=timeout,
        )
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        logger.warning("Vision analysis returned status %s; using local fallback.", resp.status_code)
    except Exception as e:
        logger.warning("Vision character analysis skipped (%s); using local fallback.", e)
    return None


def create_or_load_character_bible(
    source_image: Path,
    output_dir: Path,
    character_id: Optional[str] = None,
    subject_type: Optional[str] = None,
    custom_facts: Optional[list[str]] = None,
    allow_cloud_upload: bool = True,
    use_vision: bool = False,
    style: str = "real-cutout",
) -> CharacterBible:
    """Build or load CharacterBible specification with real SHA-256, palette, and style preset."""
    style_preset = resolve_style_preset(style)
    char_json_path = output_dir / "character.json"
    if char_json_path.exists():
        with char_json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            bible = CharacterBible(**data)
            if bible.render_style.style_id != style_preset.id:
                bible.render_style.style_id = style_preset.id
                bible.render_style.outline = style_preset.outline
                bible.render_style.lighting = style_preset.lighting
                with char_json_path.open("w", encoding="utf-8") as fw:
                    json.dump(bible.model_dump(), fw, indent=2, ensure_ascii=False)
            return bible

    sha256 = compute_sha256(source_image)
    extracted_palette = extract_dominant_palette(source_image, count=2)
    # Blend extracted subject colors with style preset accent color
    palette = list(dict.fromkeys(extracted_palette + style_preset.default_palette))[:3]

    vision_data = None
    if use_vision and allow_cloud_upload:
        settings = AppSettings()
        if settings.openai_api_key:
            vision_data = analyze_character_with_vision(
                source_image=source_image,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                vision_model=settings.sticker_vision_model,
            )

    resolved_subject = "human-portrait"
    cid = sanitize_id(character_id or f"{resolved_subject}-{sha256[:8]}")

    facts = (
        custom_facts
        or (vision_data.get("identity_facts") if vision_data else None)
        or [
            "Photorealistic real-person face with natural expressive eyes, nose, and lips",
            "Distinctive hairstyle, hairline, and hair texture from reference photo",
            "Authentic human skin tone and facial bone structure",
            "Consistent outfit and accessories from reference photo",
        ]
    )

    locked = (
        (vision_data.get("locked_attributes") if vision_data else None)
        or [
            "Real-person facial identity, bone structure, and eye shape",
            "Authentic photographic skin texture (no 2D cartoonizing)",
            "Hairstyle, parting, and hair color",
            "Outfit and accessories",
        ]
    )

    bible = CharacterBible(
        character_id=cid,
        source_sha256=sha256,
        subject_type=resolved_subject,
        identity_facts=facts,
        locked_attributes=locked,
        allowed_variation=[
            "Real-person facial expressions and mouth shapes",
            "Natural eye blinking, winking, and gaze direction",
            "Small head angles and tilts",
            "Hand and arm gestures",
        ],
        render_style=RenderStyle(
            style_id=style_preset.id,
            outline=style_preset.outline,
            palette=palette,
            lighting=style_preset.lighting,
            composition="single-character-centered",
        ),
        master_anchor=str(output_dir / "work" / "character-anchor.png"),
        reference_image=str(source_image),
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    with char_json_path.open("w", encoding="utf-8") as f:
        json.dump(bible.model_dump(), f, indent=2, ensure_ascii=False)

    return bible
