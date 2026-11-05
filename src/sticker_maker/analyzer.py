"""Source image validation and character identity analysis."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional
from PIL import Image, ImageOps

from .schemas import CharacterBible, RenderStyle, sanitize_id


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


def create_or_load_character_bible(
    source_image: Path,
    output_dir: Path,
    character_id: Optional[str] = None,
    subject_type: str = "pet-cat",
    custom_facts: Optional[list[str]] = None,
) -> CharacterBible:
    """Build or load CharacterBible specification with real SHA-256."""
    char_json_path = output_dir / "character.json"
    if char_json_path.exists():
        with char_json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return CharacterBible(**data)

    # Compute hash of source image
    sha256 = compute_sha256(source_image)
    cid = sanitize_id(character_id or f"{subject_type}-{sha256[:8]}")

    facts = custom_facts or [
        "Cute expressive eyes and friendly face",
        "Distinctive fur or hair patterning",
        "Consistent proportions and silhouette",
        "Round and soft facial features",
    ]

    bible = CharacterBible(
        character_id=cid,
        source_sha256=sha256,
        subject_type=subject_type,
        identity_facts=facts,
        locked_attributes=[
            "Facial structure and eye shape",
            "Color palette and markings pattern",
            "Body proportions",
            "Ear and hair/fur contour",
        ],
        allowed_variation=[
            "Facial expressions and mouth shapes",
            "Small head angles and tilts",
            "Arm and paw gestures",
            "Subtle comic effect props (e.g. sweatdrop, hearts)",
        ],
        render_style=RenderStyle(
            outline="round-uniform",
            palette=["#FFF6EA", "#F7BDC9", "#987C7B"],
            lighting="soft-flat",
            composition="single-character-centered",
        ),
        master_anchor=str(output_dir / "work" / "character-anchor.png"),
        reference_image=str(source_image),
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    with char_json_path.open("w", encoding="utf-8") as f:
        json.dump(bible.model_dump(), f, indent=2, ensure_ascii=False)

    return bible
