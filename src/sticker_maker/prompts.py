"""Prompt assembly and stabilization (exclusively for real-person photorealistic sticker packs)."""

from __future__ import annotations

from typing import Optional
from .schemas import CharacterBible, ExpressionItem
from .styles import resolve_style_preset

REAL_PERSON_HARD_LOCK = (
    "CRITICAL REAL-PERSON RULE: Keep the subject as a photorealistic real human portrait cutout "
    "of the exact same person from the reference photo (authentic facial bone structure, real eyes/nose/lips, "
    "real skin texture, exact hairstyle, and outfit). NEVER cartoonize, NEVER turn the person into 2D anime, "
    "chibi illustration, flat vector art, 3D doll, or animal/panda head."
)


def meme_hint(item: ExpressionItem) -> str:
    """Extra look guidance for meme / abstract templates (UI, text, icons are overlaid later)."""
    if not getattr(item, "meme", None) or not item.meme.style_hint:
        return ""
    return (
        f"[MEME LOOK] {item.meme.style_hint} Keep the subject as the exact same photorealistic real person "
        f"acting out an expressive real-person reaction face. "
        f"Do not draw any text, logos, icons, UI, stamps or signs; those are added afterwards.\n"
    )


def composition_hint(text_layout: Optional[str] = None, bubble_side: Optional[str] = None) -> str:
    """Tell the image model where to leave empty space for deterministic text overlays."""
    side = "upper-left" if bubble_side != "right" else "upper-right"
    if text_layout == "bubble":
        return (
            f"Leave the {side} corner of the canvas empty (about 35% width x 30% height) for a speech bubble "
            f"that will be added later; keep the character slightly offset toward the opposite side. "
            f"Do NOT draw any speech bubble, letters or text yourself."
        )
    if text_layout == "both":
        return (
            f"Leave the {side} corner empty for a speech bubble and reserve the bottom strip for a caption "
            f"(both added later). Do NOT draw any speech bubble, letters or text yourself."
        )
    if text_layout == "none":
        return "The character may fill most of the canvas; no text, letters or speech bubbles."
    return "Reserve lower space for separate typography; do not draw text into image."


def build_anchor_prompt(
    subject_type: str = "human-portrait",
    facts: Optional[list[str]] = None,
    style: str = "real-cutout",
    palette: Optional[list[str]] = None,
) -> str:
    facts_str = "; ".join(facts) if facts else "Photorealistic real-person face and hairstyle from reference photo"
    preset = resolve_style_preset(style)
    effective_palette = palette or preset.default_palette
    palette_note = f" Primary color palette: {', '.join(effective_palette)}." if effective_palette else ""
    neg_extra = f"\n{preset.negative_extra}" if preset.negative_extra else ""
    return (
        f"[IDENTITY LOCK]\n"
        f"Create the master photorealistic real-person portrait anchor ({subject_type}).\n"
        f"{REAL_PERSON_HARD_LOCK}\n"
        f"Observable facts: {facts_str}.\n"
        f"Neutral relaxed front-facing half-body portrait pose, natural pleasant expression.\n\n"
        f"[STYLE LOCK]\n"
        f"Style ID: {preset.id} ({preset.display_name}).\n"
        f"{preset.prompt_lock}\n"
        f"Outline: {preset.outline}. Lighting: {preset.lighting}.{palette_note}\n"
        f"One single real person only, transparent or clean white background, centered composition.\n\n"
        f"[COMPOSITION]\n"
        f"Square canvas. Keep subject inside a safe central area.\n"
        f"No background scenery, no props unless essential.\n"
        f"Do not draw any letters, words, or text.\n\n"
        f"[NEGATIVE]\n"
        f"No 2D cartoon, no anime, no flat vector illustration, no 3D doll, no face swapping,\n"
        f"no extra subjects, no collages, no grid layout, no watermark,\n"
        f"no random outfit changes, no extra limbs, no background scene,\n"
        f"no text, no letters, no speech bubbles.{neg_extra}"
    )


def build_static_prompt(
    bible: CharacterBible,
    item: ExpressionItem,
    style: str = "real-cutout",
    text_layout: Optional[str] = None,
) -> str:
    facts_str = "; ".join(bible.identity_facts) if bible.identity_facts else "Preserve real-person identity"
    locked_str = ", ".join(bible.locked_attributes) if bible.locked_attributes else "Real facial structure, skin texture, hairstyle, outfit"
    preset = resolve_style_preset(style)
    palette_str = ", ".join(bible.render_style.palette or preset.default_palette)
    palette_note = f" Color palette: {palette_str}." if palette_str else ""
    neg_extra = f"\n{preset.negative_extra}" if preset.negative_extra else ""

    return (
        f"[IDENTITY LOCK]\n"
        f"Use the supplied photo and canonical real-person portrait anchor.\n"
        f"{REAL_PERSON_HARD_LOCK}\n"
        f"Preserve the exact same real person ({bible.subject_type}): {facts_str}.\n"
        f"Locked attributes: {locked_str}.\n"
        f"Do not redesign, cartoonize, or swap the person's face.\n\n"
        f"[STYLE LOCK]\n"
        f"Style ID: {preset.id} ({preset.display_name}).\n"
        f"{preset.prompt_lock}\n"
        f"Outline: {preset.outline}. Lighting: {preset.lighting}.{palette_note}\n"
        f"One single real person only, transparent or clean white background, centered composition.\n\n"
        f"[ACTION]\n"
        f"Expression ID: {item.id}. Mood: {item.mood}.\n"
        f"Action: {item.static_pose}.\n"
        f"{meme_hint(item)}\n"
        f"[COMPOSITION]\n"
        f"Square canvas. Keep subject inside a safe central area.\n"
        f"{composition_hint(text_layout or item.text_layout)}\n\n"
        f"[NEGATIVE]\n"
        f"No 2D cartoon, no anime, no flat illustration, no 3D doll, no panda/animal head,\n"
        f"no extra subjects, no collages, no grid layout, no watermark,\n"
        f"no random outfit changes, no extra limbs, no background scene,\n"
        f"no letters or words in the raster image.{neg_extra}"
    )


def build_native_gif_prompt(
    bible: CharacterBible,
    item: ExpressionItem,
    style: str = "real-cutout",
) -> str:
    facts_str = "; ".join(bible.identity_facts) if bible.identity_facts else bible.subject_type
    preset = resolve_style_preset(style)
    poses_str = " ".join(item.motion.keyframe_poses) if item.motion.keyframe_poses else ""
    return (
        f"Create a seamless looping real-person portrait sticker animation [Style ID: {preset.id}] of {bible.subject_type}: {facts_str}. "
        f"{REAL_PERSON_HARD_LOCK} {preset.prompt_lock} "
        f"Expression ID: {item.id}. Mood: {item.mood}. "
        f"Movement: {item.motion.type}. Action sequence: {poses_str} "
        f"IMPORTANT: Keep the lower torso and shoulders anchored in place while animating genuine independent "
        f"hand waving/gestures, natural eye blinking/winking, and mouth expression changes. "
        f"Do NOT merely float or bob a rigid static image. "
        f"One centered real person, stable photographic facial identity, transparent or clean empty background, "
        f"no text, no watermark. {preset.negative_extra}"
    )


def build_sprite_sheet_prompt(
    bible: CharacterBible,
    item: ExpressionItem,
    style: str = "real-cutout",
    text_layout: Optional[str] = None,
) -> str:
    """Build a prompt for Codex's built-in image generator / GPT Image to draw a 2x2 4-frame
    sequential real-person action sprite sheet where the AI draws real waving hands, blinking eyes, and expressions."""
    facts_str = "; ".join(bible.identity_facts) if bible.identity_facts else "Preserve real-person identity"
    locked_str = ", ".join(bible.locked_attributes) if bible.locked_attributes else "Real facial structure, skin texture, hairstyle, outfit"
    preset = resolve_style_preset(style)
    poses = item.motion.keyframe_poses or [
        f"Frame 1 (Top-Left): Base pose ({item.static_pose}), eyes open looking at viewer, lower torso anchored.",
        f"Frame 2 (Top-Right): Mid-action ({item.motion.type}), hand waving/moving to new angle, natural eye blink (eyelids closed/curved), lower torso anchored.",
        f"Frame 3 (Bottom-Left): Peak action ({item.motion.type}), hand at full wave/gesture extension, eyes open with expressive smile/mood, lower torso anchored.",
        f"Frame 4 (Bottom-Right): Smooth return pose toward Frame 1, soft wink or gentle head tilt, lower torso anchored.",
    ]
    poses_block = "\n".join(f"- {p}" for p in poses[:4])

    return (
        f"[IDENTITY & STYLE LOCK]\n"
        f"Style ID: {preset.id} ({preset.display_name}). {preset.prompt_lock}\n"
        f"{REAL_PERSON_HARD_LOCK}\n"
        f"Preserve the exact same real person ({bible.subject_type}): {facts_str}.\n"
        f"Locked attributes: {locked_str}.\n\n"
        f"[2x2 ANIMATION SPRITE SHEET LAYOUT]\n"
        f"Generate a 2x2 4-frame sequential photorealistic real-person animation sprite sheet on a clean solid white or transparent background "
        f"(Top-Left=Frame 1, Top-Right=Frame 2, Bottom-Left=Frame 3, Bottom-Right=Frame 4). "
        f"Each quadrant contains the exact same real person at the exact same scale, centered in its quadrant, "
        f"performing genuine multi-frame real-person action for '{item.mood}' ({item.motion.type}):\n"
        f"{poses_block}\n\n"
        f"{meme_hint(item)}"
        f"[MOTION CONSTRAINTS]\n"
        f"Keep the lower torso, hairstyle, and clothing identical across all 4 frames while the AI clearly draws "
        f"different hand wave positions, natural eye blinking/closed-eye frames, head tilt, and mouth changes across the 4 panels. "
        f"NEVER turn the person into a 2D cartoon or anime character. "
        f"No grid border lines, no dividing lines, no text, no letters, no watermark.\n"
        f"Per-panel composition: {composition_hint(text_layout or item.text_layout)}"
    )


def build_keyframe_prompt(
    bible: CharacterBible,
    item: ExpressionItem,
    frame_idx: int,
    total_frames: int,
    frame_desc: Optional[str] = None,
    style: str = "real-cutout",
    text_layout: Optional[str] = None,
) -> str:
    base = build_static_prompt(bible, item, style=style, text_layout=text_layout)
    if not frame_desc and item.motion.keyframe_poses:
        pose_idx = frame_idx % len(item.motion.keyframe_poses)
        frame_desc = item.motion.keyframe_poses[pose_idx]
    delta_note = frame_desc or f"Frame {frame_idx + 1} of {total_frames} in cyclical motion {item.motion.type}."
    return (
        f"{base}\n\n"
        f"[ANIMATION KEYFRAME CONSTRAINT]\n"
        f"{delta_note}\n"
        f"Reference Frame 1 strictly: keep the exact same real-person photographic facial identity, outfit, scale, and lower torso position, "
        f"and redraw ONLY the active gesture (waving hand/arm angle), eye blink state (open vs closed/smiling eyes), "
        f"and facial expression for this keyframe."
    )


def build_keyframe_sequence_prompts(
    bible: CharacterBible,
    item: ExpressionItem,
    style: str = "real-cutout",
    num_keyframes: int = 4,
    text_layout: Optional[str] = None,
) -> list[str]:
    """Return a list of per-keyframe AI generation prompts for multi-pass Codex image generation."""
    poses = item.motion.keyframe_poses or []
    total = max(2, num_keyframes)
    return [
        build_keyframe_prompt(
            bible=bible,
            item=item,
            frame_idx=idx,
            total_frames=total,
            frame_desc=poses[idx % len(poses)] if poses else None,
            style=style,
            text_layout=text_layout,
        )
        for idx in range(total)
    ]
