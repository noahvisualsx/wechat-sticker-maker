"""Prompt assembly and stabilization (exclusively for real-person photorealistic sticker packs)."""

from __future__ import annotations

from typing import Optional, Sequence
from .schemas import CharacterBible, ExpressionItem
from .styles import resolve_style_preset

REAL_PERSON_HARD_LOCK = (
    "CRITICAL REAL-PERSON RULE: Keep the subject as a photorealistic real human portrait cutout "
    "of the exact same person from the reference photo (authentic facial bone structure, real eyes/nose/lips, "
    "real skin texture, exact hairstyle, and outfit). NEVER cartoonize, NEVER turn the person into 2D anime, "
    "chibi illustration, flat vector art, 3D doll, or animal/panda head."
)

ANATOMY_AND_PROPORTION_HARD_LOCK = (
    "CRITICAL ANATOMY & FACIAL PROPORTION HARD LOCK: "
    "(1) LIMB & HAND TOPOLOGY: Strictly AT MOST 2 arms and 2 hands for one person (1 left arm from left shoulder, "
    "1 right arm from right shoulder). When an arm is raised to touch the head, hair, cheek, or hold a prop, "
    "the sleeve and shoulder on that side MUST lift upward naturally with that arm — NEVER draw BOTH a downward-hanging "
    "sleeve/arm at the side AND a second raised arm emerging from behind the same shoulder (ZERO 3rd hands, ZERO duplicate limbs, "
    "ZERO disembodied floating hands). Every visible hand MUST have natural 5-finger human anatomy (1 thumb + 4 fingers) "
    "connected smoothly to a single wrist. "
    "(2) CRANIOFACIAL ASPECT RATIO LOCK: Preserve the exact natural facial width-to-height ratio (~1:1.25) and midface/chin "
    "proportions from the reference photo — NEVER vertically elongate or stretch the face, nose bridge, philtrum, or chin "
    "('no horse-face stretching'), and NEVER warp or melt eyes/lips. "
    "(3) REAL EYES & SKIN: Express emotion with real human eye muscles and authentic irises — NEVER draw 2D swirl eyes (@_@), "
    "star/heart/coin stickers covering eyeballs, or cartoon lines on skin."
)

DUO_ANATOMY_AND_PROPORTION_LOCK = (
    "CRITICAL TWO-PERSON ANATOMY & PROPORTION HARD LOCK: "
    "(1) STRICT ARM/HAND COUNT: Exactly 2 real people with AT MOST 4 arms and 4 hands in total (strictly max 2 arms per person: "
    "1 left + 1 right). For BOTH Person A and Person B, if an arm is raised (touching hair, cheek, holding phone/cup, waving), "
    "lift that side's sleeve upward — NEVER leave a duplicate hanging sleeve/arm at the side while raising a second arm from "
    "the same shoulder (ZERO 3rd hands, ZERO 5th hands, ZERO disembodied hands on shoulders/waists). "
    "(2) ZERO HORIZONTAL SQUISHING OR VERTICAL FACE STRETCHING: Position Person A and Person B at comfortable three-quarter angles "
    "with 15%-25% natural shoulder overlap in a waist-up/chest-up portrait so BOTH faces keep their full, natural width-to-height "
    "proportions matching their reference photos — NEVER horizontally compress or vertically elongate either person's midface or chin."
)

CLEAN_BACKGROUND_HARD_LOCK = (
    "CLEAN CUTOUT BACKGROUND RULE: Render on a flat solid pure white (#FFFFFF) studio backdrop or true native RGBA alpha=0 "
    "transparency — NEVER draw, paint, or bake a grey-and-white checkerboard transparency grid into the image pixels, "
    "and NEVER draw floating '?'/'!' symbols or background clutter."
)

DEFECT_RETRY_INSTRUCTIONS: dict[str, str] = {
    "baked_checkerboard": (
        "PREVIOUS ATTEMPT REJECTED FOR BAKED-IN CHECKERBOARD: You drew grey-and-white checkerboard squares into the background. "
        "Render ONLY on a completely flat, uniform pure white (#FFFFFF) studio background (or native RGBA alpha=0). "
        "ZERO grey-and-white squares."
    ),
    "third_hand_or_extra_limb": (
        "PREVIOUS ATTEMPT REJECTED FOR EXTRA ARM / 3RD HAND: Count every shoulder, sleeve, arm, and hand carefully! "
        "Each person MUST have AT MOST 2 arms (1 left, 1 right) and AT MOST 2 hands (5 fingers each). "
        "If an arm is raised to touch hair/head/cheek or hold an object, lift that sleeve upward — NEVER draw a downward-hanging "
        "arm/sleeve AND a raised arm on the same side, and NEVER draw disembodied hands."
    ),
    "stretched_or_warped_face": (
        "PREVIOUS ATTEMPT REJECTED FOR STRETCHED / ELONGATED FACE: Lock the exact craniofacial width-to-height ratio of the "
        "reference photo. Keep midface, nose bridge, philtrum, and chin compact and natural — DO NOT vertically stretch or narrow "
        "the face, and overlap shoulders slightly in two-person shots instead of horizontally squishing faces."
    ),
    "floating_island": (
        "PREVIOUS ATTEMPT REJECTED FOR FLOATING DETACHED FRAGMENTS: Keep a single cohesive waist-up portrait silhouette with "
        "ZERO detached floating hands, stray props, background fragments, or drawn '?'/'!'/text symbols."
    ),
    "tiny_subject": (
        "PREVIOUS ATTEMPT REJECTED FOR TINY FULL-BODY FRAMING: Frame as a close chest-up / waist-up portrait where the subject "
        "fills 55%-78% of the canvas height and the head is large and expressive. DO NOT draw a tiny distant or kneeling full-body figure."
    ),
    "hard_edge_clip": (
        "PREVIOUS ATTEMPT REJECTED FOR CROPPED HEAD / HAND AT CANVAS EDGE: Leave at least 5% clean empty margin above the top of "
        "the head and around any raised hand so hair crowns and fingers are completely inside the frame."
    ),
    "cartoon_eyes_or_drift": (
        "PREVIOUS ATTEMPT REJECTED FOR CARTOON FEATURES / IDENTITY DRIFT: Keep 100% photorealistic real human irises, skin texture, "
        "and the exact bone structure of the reference photo. ZERO 2D swirl eyes, ZERO star/heart eye stickers, ZERO anime shading."
    ),
    "sprite_quadrant_mismatch": (
        "PREVIOUS ATTEMPT REJECTED FOR BROKEN 2x2 SPRITE LAYOUT: Place 4 equal-sized waist-up frames cleanly centered in the 4 "
        "quadrants (Top-Left, Top-Right, Bottom-Left, Bottom-Right) with identical head/body scale and clean empty gutter space "
        "along the horizontal and vertical centerlines so nothing bleeds across quadrants."
    ),
}


def build_corrective_retry_prompt(
    base_prompt: str,
    defect_codes: Sequence[str],
    custom_note: str = "",
) -> str:
    """Append targeted red-line retry corrections to ``base_prompt`` after a failed QA check."""
    seen: list[str] = []
    for code in defect_codes:
        key = code.strip()
        if key and key not in seen:
            seen.append(key)
    bullets: list[str] = []
    for code in seen:
        if code in DEFECT_RETRY_INSTRUCTIONS:
            bullets.append(f"- {DEFECT_RETRY_INSTRUCTIONS[code]}")
        elif "third_hand" in code or "limb" in code or "arm" in code:
            bullets.append(f"- {DEFECT_RETRY_INSTRUCTIONS['third_hand_or_extra_limb']}")
        elif "stretch" in code or "face" in code:
            bullets.append(f"- {DEFECT_RETRY_INSTRUCTIONS['stretched_or_warped_face']}")
        elif "checker" in code:
            bullets.append(f"- {DEFECT_RETRY_INSTRUCTIONS['baked_checkerboard']}")
        else:
            bullets.append(f"- Fix detected QA issue '{code}' while strictly obeying all anatomy and real-person locks.")
    if custom_note.strip():
        bullets.append(f"- {custom_note.strip()}")
    if not bullets:
        bullets.append(f"- {DEFECT_RETRY_INSTRUCTIONS['third_hand_or_extra_limb']}")
        bullets.append(f"- {DEFECT_RETRY_INSTRUCTIONS['stretched_or_warped_face']}")
    correction_block = "\n".join(bullets)
    return (
        f"{base_prompt}\n\n"
        f"[CRITICAL RETRY CORRECTION — STRICT QUALITY GATE]\n"
        f"{correction_block}"
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
        f"Neutral relaxed front-facing chest-up/waist-up portrait pose, natural pleasant expression.\n\n"
        f"[ANATOMY & PROPORTION LOCK]\n"
        f"{ANATOMY_AND_PROPORTION_HARD_LOCK}\n\n"
        f"[STYLE LOCK]\n"
        f"Style ID: {preset.id} ({preset.display_name}).\n"
        f"{preset.prompt_lock}\n"
        f"Outline: {preset.outline}. Lighting: {preset.lighting}.{palette_note}\n"
        f"One single real person only, centered composition.\n"
        f"{CLEAN_BACKGROUND_HARD_LOCK}\n\n"
        f"[COMPOSITION]\n"
        f"Square canvas. Keep subject inside a safe central area.\n"
        f"No background scenery, no props unless essential.\n"
        f"Do not draw any letters, words, or text.\n\n"
        f"[NEGATIVE]\n"
        f"No 2D cartoon, no anime, no flat vector illustration, no 3D doll, no face swapping,\n"
        f"no 3rd hand, no duplicate arm from one shoulder, no elongated/stretched face, no grey-white checkerboard grid,\n"
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
        f"[ANATOMY & PROPORTION LOCK]\n"
        f"{ANATOMY_AND_PROPORTION_HARD_LOCK}\n\n"
        f"[STYLE LOCK]\n"
        f"Style ID: {preset.id} ({preset.display_name}).\n"
        f"{preset.prompt_lock}\n"
        f"Outline: {preset.outline}. Lighting: {preset.lighting}.{palette_note}\n"
        f"One single real person only, centered chest-up/waist-up portrait composition.\n"
        f"{CLEAN_BACKGROUND_HARD_LOCK}\n\n"
        f"[ACTION]\n"
        f"Expression ID: {item.id}. Mood: {item.mood}.\n"
        f"Action: {item.static_pose}.\n"
        f"{meme_hint(item)}\n"
        f"[COMPOSITION]\n"
        f"Square canvas. Keep subject inside a safe central area with >=5% headroom above hair/hands.\n"
        f"{composition_hint(text_layout or item.text_layout)}\n\n"
        f"[NEGATIVE]\n"
        f"No 2D cartoon, no anime, no flat illustration, no 3D doll, no panda/animal head,\n"
        f"no 3rd hand, no duplicate arm from same shoulder, no 6 fingers, no elongated/stretched face, no baked checkerboard,\n"
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
        f"{REAL_PERSON_HARD_LOCK} {ANATOMY_AND_PROPORTION_HARD_LOCK} {preset.prompt_lock} "
        f"Expression ID: {item.id}. Mood: {item.mood}. "
        f"Movement: {item.motion.type}. Action sequence: {poses_str} "
        f"IMPORTANT: Keep the lower torso and shoulders anchored in place while animating genuine independent "
        f"hand waving/gestures, natural eye blinking/winking, and mouth expression changes. "
        f"Do NOT merely float or bob a rigid static image. "
        f"{CLEAN_BACKGROUND_HARD_LOCK} "
        f"One centered real person, stable photographic facial identity, no text, no watermark. {preset.negative_extra}"
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
        f"{ANATOMY_AND_PROPORTION_HARD_LOCK}\n"
        f"Preserve the exact same real person ({bible.subject_type}): {facts_str}.\n"
        f"Locked attributes: {locked_str}.\n\n"
        f"[2x2 ANIMATION SPRITE SHEET LAYOUT]\n"
        f"Generate a 2x2 4-frame sequential photorealistic real-person animation sprite sheet "
        f"(Top-Left=Frame 1, Top-Right=Frame 2, Bottom-Left=Frame 3, Bottom-Right=Frame 4). "
        f"{CLEAN_BACKGROUND_HARD_LOCK} "
        f"Each quadrant contains the exact same real person at the exact same chest-up/waist-up scale, centered in its quadrant "
        f"with clean empty separation along the horizontal and vertical centerlines (zero cross-quadrant bleeding), "
        f"performing genuine multi-frame real-person action for '{item.mood}' ({item.motion.type}):\n"
        f"{poses_block}\n\n"
        f"{meme_hint(item)}"
        f"[MOTION CONSTRAINTS]\n"
        f"Keep the lower torso, hairstyle, facial width-to-height ratio, and clothing identical across all 4 frames while the AI clearly draws "
        f"different hand wave positions (strictly <=2 arms per frame, lifting sleeve with any raised arm), natural eye blinking/closed-eye frames, "
        f"head tilt, and mouth changes across the 4 panels. "
        f"NEVER turn the person into a 2D cartoon or anime character. "
        f"No grid border lines, no dividing lines, no grey-white checkerboard, no text, no letters, no watermark.\n"
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
