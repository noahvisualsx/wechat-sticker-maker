"""Prompt assembly and stabilization."""

from __future__ import annotations

from typing import Optional
from .schemas import CharacterBible, ExpressionItem


def build_anchor_prompt(subject_type: str, facts: list[str], style: str = "kawaii-flat") -> str:
    facts_str = "; ".join(facts) if facts else "Distinct recognizable character features"
    return (
        f"[IDENTITY LOCK]\n"
        f"Design the master reference anchor for this character ({subject_type}).\n"
        f"Observable facts: {facts_str}.\n"
        f"Neutral relaxed front-facing pose, calm pleasant expression.\n\n"
        f"[STYLE LOCK]\n"
        f"Consistent kawaii sticker illustration, clean rounded linework,\n"
        f"soft pastel palette, expressive yet recognizable features.\n"
        f"One single character only, transparent background, centered composition.\n\n"
        f"[COMPOSITION]\n"
        f"Square canvas. Keep subject inside a safe central area.\n"
        f"No background scenery, no props unless essential.\n"
        f"Do not draw any letters, words, or text.\n\n"
        f"[NEGATIVE]\n"
        f"No extra subjects, no collages, no grid layout, no watermark,\n"
        f"no random outfit changes, no extra limbs, no background scene,\n"
        f"no text, no letters, no speech bubbles."
    )


def build_static_prompt(bible: CharacterBible, item: ExpressionItem) -> str:
    facts_str = "; ".join(bible.identity_facts) if bible.identity_facts else "Preserve subject identity"
    locked_str = ", ".join(bible.locked_attributes) if bible.locked_attributes else "Facial structure, colors, outfit"

    return (
        f"[IDENTITY LOCK]\n"
        f"Use the supplied photo and canonical character anchor.\n"
        f"Preserve the same subject identity ({bible.subject_type}): {facts_str}.\n"
        f"Locked attributes: {locked_str}.\n"
        f"Do not redesign or swap the character.\n\n"
        f"[STYLE LOCK]\n"
        f"Consistent kawaii sticker illustration, clean rounded linework,\n"
        f"soft pastel palette, expressive yet recognizable features.\n"
        f"One single character only, transparent background, centered composition.\n\n"
        f"[ACTION]\n"
        f"Expression: {item.mood}.\n"
        f"Action: {item.static_pose}.\n\n"
        f"[COMPOSITION]\n"
        f"Square canvas. Keep subject inside a safe central area.\n"
        f"Reserve lower space for separate typography; do not draw text into image.\n\n"
        f"[NEGATIVE]\n"
        f"No extra subjects, no collages, no grid layout, no watermark,\n"
        f"no random outfit changes, no extra limbs, no background scene,\n"
        f"no letters or words in the raster illustration."
    )


def build_native_gif_prompt(bible: CharacterBible, item: ExpressionItem) -> str:
    facts_str = "; ".join(bible.identity_facts) if bible.identity_facts else bible.subject_type
    return (
        f"Create a seamless looping kawaii sticker animation of {facts_str}. "
        f"Mood: {item.mood}. "
        f"Movement: {item.motion.type}, gentle amplitude, looping seamlessly. "
        f"One centered character, stable identity, transparent or clean empty background, "
        f"no text, no watermark, gentle continuous motion."
    )


def build_keyframe_prompt(
    bible: CharacterBible,
    item: ExpressionItem,
    frame_idx: int,
    total_frames: int,
    frame_desc: Optional[str] = None,
) -> str:
    base = build_static_prompt(bible, item)
    delta_note = frame_desc or f"Frame {frame_idx + 1} of {total_frames} in cyclical motion {item.motion.type}."
    return (
        f"{base}\n\n"
        f"[ANIMATION FRAME CONSTRAINT]\n"
        f"{delta_note}\n"
        f"Maintain exact identical body position, silhouette, and locked attributes as the base pose."
    )
