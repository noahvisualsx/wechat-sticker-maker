"""Strict real-person anatomy, facial-proportion, checkerboard, and sprite-sheet QA engine.

Implements pure-Pillow programmatic red-line detectors (zero numpy/opencv dependency),
high-magnification 2x Face/Shoulder/Hand QA contact-sheet generation, and optional
OpenAI / Gemini multimodal Vision API anatomy & proportion verification.
"""

from __future__ import annotations

import base64
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
import io
import json
import logging
import math
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont
import requests

from ..config import AppSettings, get_default_font_path
from ..processing.alpha import ensure_alpha_channel, remove_background_smart
from ..prompts import build_corrective_retry_prompt
from ..schemas import ValidationCheck

logger = logging.getLogger(__name__)

CANONICAL_DEFECT_CODES = (
    "baked_checkerboard",
    "third_hand_or_extra_limb",
    "stretched_or_warped_face",
    "floating_island",
    "tiny_subject",
    "hard_edge_clip",
    "cartoon_eyes_or_drift",
    "sprite_quadrant_mismatch",
)


@dataclass
class ItemStrictAudit:
    """Aggregated strict QA result for one generated sticker or raw frame."""

    item_id: str
    target_path: str
    status: str = "pass"  # pass | warn | fail
    defect_codes: List[str] = field(default_factory=list)
    checks: List[ValidationCheck] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    corrective_prompt_suffix: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "target_path": self.target_path,
            "status": self.status,
            "defect_codes": list(self.defect_codes),
            "metrics": dict(self.metrics),
            "checks": [c.model_dump() for c in self.checks],
            "corrective_prompt_suffix": self.corrective_prompt_suffix,
        }


# ---------------------------------------------------------------------------
# 1. Baked-in Fake Checkerboard Detector (Pre-matting & Post-matting)
# ---------------------------------------------------------------------------


def detect_baked_checkerboard(
    img: Image.Image,
    target_label: str = "image",
) -> ValidationCheck:
    """Detect grey/white checkerboard grids painted directly into RGB pixels.

    Catches BOTH:
      1. Raw images where the model drew alternating white (#FFFFFF) and grey (#C0C0C0..#E6E6E6)
         squares instead of a solid flat background or true RGBA alpha=0.
      2. Post-matted images where flood-fill keyed out the white squares (alpha=0) and left
         periodic opaque neutral grey squares along the outer border.
    """
    rgba = ensure_alpha_channel(img)
    w, h = rgba.size
    if w < 32 or h < 32:
        return ValidationCheck(
            name="Strict QA: Baked Checkerboard",
            target=target_label,
            status="pass",
            message="Image too small for checkerboard grid artefacts",
        )

    px = rgba.load()
    top_h = max(8, int(h * 0.12))
    side_w = max(8, int(w * 0.10))

    # Sample horizontal scanlines in the top border strip + vertical scanlines in left/right strips
    bright_count = 0
    grey_count = 0
    opaque_neutral_count = 0
    rgb_step_transitions = 0
    alpha_grey_transitions = 0

    def _classify_pixel(x: int, y: int) -> Tuple[str, int]:
        r, g, b, a = px[x, y]
        if a <= 25:
            return ("trans", 0)
        chroma = max(r, g, b) - min(r, g, b)
        lum = (r + g + b) // 3
        if a >= 180 and chroma <= 16:
            if lum >= 249:
                return ("white", lum)
            if 165 <= lum <= 245:
                return ("grey", lum)
        return ("other", lum)

    # Scan 6 horizontal lines across the top margin
    y_samples = sorted({max(1, min(top_h - 1, int(top_h * k / 6))) for k in range(1, 6)})
    for y in y_samples:
        prev_kind = ""
        run_len = 0
        for x in range(0, w, max(1, w // 240)):
            kind, _lum = _classify_pixel(x, y)
            if kind in ("white", "grey"):
                opaque_neutral_count += 1
                if kind == "white":
                    bright_count += 1
                else:
                    grey_count += 1
            if kind == prev_kind:
                run_len += 1
            else:
                if run_len >= 2:
                    if {prev_kind, kind} == {"white", "grey"}:
                        rgb_step_transitions += 1
                    elif {prev_kind, kind} == {"trans", "grey"}:
                        alpha_grey_transitions += 1
                prev_kind = kind
                run_len = 1

    # Scan 4 vertical lines on left & right margins (upper 75% height to avoid bottom torso)
    x_samples = [
        max(1, side_w // 3),
        max(2, (side_w * 2) // 3),
        min(w - 2, w - 1 - side_w // 3),
        min(w - 3, w - 1 - (side_w * 2) // 3),
    ]
    y_limit = int(h * 0.78)
    for x in x_samples:
        prev_kind = ""
        run_len = 0
        for y in range(0, y_limit, max(1, h // 240)):
            kind, _lum = _classify_pixel(x, y)
            if kind in ("white", "grey"):
                opaque_neutral_count += 1
                if kind == "white":
                    bright_count += 1
                else:
                    grey_count += 1
            if kind == prev_kind:
                run_len += 1
            else:
                if run_len >= 2:
                    if {prev_kind, kind} == {"white", "grey"}:
                        rgb_step_transitions += 1
                    elif {prev_kind, kind} == {"trans", "grey"}:
                        alpha_grey_transitions += 1
                prev_kind = kind
                run_len = 1

    raw_checker_detected = (
        opaque_neutral_count >= 40
        and bright_count >= int(opaque_neutral_count * 0.14)
        and grey_count >= int(opaque_neutral_count * 0.14)
        and rgb_step_transitions >= 10
    )
    post_matte_checker_detected = alpha_grey_transitions >= 12 and grey_count >= 18

    if raw_checker_detected or post_matte_checker_detected:
        mode_desc = "baked RGB grey/white grid" if raw_checker_detected else "post-matte grey checkerboard residue"
        return ValidationCheck(
            name="Strict QA: Baked Checkerboard",
            target=target_label,
            status="fail",
            message=(
                f"Fake transparency checkerboard detected ({mode_desc}: "
                f"rgb_transitions={rgb_step_transitions}, alpha_grey_transitions={alpha_grey_transitions})"
            ),
            details={
                "defect_code": "baked_checkerboard",
                "rgb_step_transitions": rgb_step_transitions,
                "alpha_grey_transitions": alpha_grey_transitions,
                "bright_count": bright_count,
                "grey_count": grey_count,
            },
        )

    return ValidationCheck(
        name="Strict QA: Baked Checkerboard",
        target=target_label,
        status="pass",
        message="No baked-in grey/white checkerboard detected",
    )


# ---------------------------------------------------------------------------
# 2. Connected-Component Island & Proportion / Edge-Clip Analysis
# ---------------------------------------------------------------------------


def _prepare_cutout_for_analysis(img: Image.Image, is_raw: bool) -> Image.Image:
    rgba = ensure_alpha_channel(img)
    if is_raw:
        # Raw images from providers may sit on a solid white backdrop prior to matting
        return remove_background_smart(rgba, mode="color")
    return rgba


def _connected_components_grid(alpha: Image.Image, grid_size: int = 192, alpha_thresh: int = 48) -> Tuple[List[Dict[str, Any]], int, int]:
    """Run fast 8-connected BFS on a downsampled alpha mask in pure Python."""
    w, h = alpha.size
    gw = min(grid_size, max(16, w))
    gh = min(grid_size, max(16, h))
    small = alpha.resize((gw, gh), Image.Resampling.BILINEAR)
    spx = small.load()

    visited = bytearray(gw * gh)
    comps: List[Dict[str, Any]] = []
    for y in range(gh):
        for x in range(gw):
            idx = y * gw + x
            if visited[idx] or spx[x, y] <= alpha_thresh:
                continue
            visited[idx] = 1
            q: deque[Tuple[int, int]] = deque([(x, y)])
            cells = 0
            min_x = max_x = x
            min_y = max_y = y
            while q:
                cx, cy = q.popleft()
                cells += 1
                if cx < min_x:
                    min_x = cx
                if cx > max_x:
                    max_x = cx
                if cy < min_y:
                    min_y = cy
                if cy > max_y:
                    max_y = cy
                for ny in (cy - 1, cy, cy + 1):
                    if ny < 0 or ny >= gh:
                        continue
                    row_off = ny * gw
                    for nx in (cx - 1, cx, cx + 1):
                        if 0 <= nx < gw:
                            nidx = row_off + nx
                            if not visited[nidx] and spx[nx, ny] > alpha_thresh:
                                visited[nidx] = 1
                                q.append((nx, ny))
            comps.append(
                {
                    "cells": cells,
                    "area_ratio": cells / float(gw * gh),
                    "bbox": (min_x / float(gw), min_y / float(gh), (max_x + 1) / float(gw), (max_y + 1) / float(gh)),
                }
            )
    comps.sort(key=lambda c: c["cells"], reverse=True)
    return comps, gw, gh


def _bbox_gap(b1: Tuple[float, float, float, float], b2: Tuple[float, float, float, float]) -> float:
    dx = max(0.0, b1[0] - b2[2], b2[0] - b1[2])
    dy = max(0.0, b1[1] - b2[3], b2[1] - b1[3])
    return math.hypot(dx, dy)


def analyze_cutout_geometry(
    img: Image.Image,
    target_label: str = "image",
    *,
    is_duo: bool = False,
    is_raw: bool = True,
    strict: bool = True,
) -> Tuple[List[ValidationCheck], Dict[str, Any]]:
    """Inspect subject occupancy, vertical stretch / squishing, edge clipping, and floating islands."""
    checks: List[ValidationCheck] = []
    metrics: Dict[str, Any] = {}

    cutout = _prepare_cutout_for_analysis(img, is_raw=is_raw)
    w, h = cutout.size
    alpha = cutout.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        checks.append(
            ValidationCheck(
                name="Strict QA: Subject Presence",
                target=target_label,
                status="fail",
                message="Image contains no opaque foreground subject after matting",
                details={"defect_code": "tiny_subject"},
            )
        )
        return checks, {"empty": True}

    x0, y0, x1, y1 = bbox
    bw = max(1, x1 - x0)
    bh = max(1, y1 - y0)
    bbox_occupancy = (bw * bh) / float(w * h)
    aspect_hw = bh / float(bw)

    hist = alpha.histogram()
    fg_pixels = sum(hist[48:])
    opaque_ratio = fg_pixels / float(w * h)

    comps, _gw, _gh = _connected_components_grid(alpha)
    metrics.update(
        {
            "bbox": [x0, y0, x1, y1],
            "bbox_w": bw,
            "bbox_h": bh,
            "bbox_occupancy": round(bbox_occupancy, 4),
            "opaque_ratio": round(opaque_ratio, 4),
            "aspect_hw": round(aspect_hw, 3),
            "component_count": len(comps),
        }
    )

    # 1. Tiny / shrunken distant full-body check
    if bbox_occupancy < 0.14 or opaque_ratio < 0.05:
        checks.append(
            ValidationCheck(
                name="Strict QA: Framing Scale",
                target=target_label,
                status="fail" if strict else "warn",
                message=(
                    f"Subject too small ({bbox_occupancy:.1%} bbox, {opaque_ratio:.1%} opaque) — "
                    f"likely distant/kneeling full-body figure instead of chest-up/waist-up portrait"
                ),
                details={"defect_code": "tiny_subject", "bbox_occupancy": bbox_occupancy, "opaque_ratio": opaque_ratio},
            )
        )
    else:
        checks.append(
            ValidationCheck(
                name="Strict QA: Framing Scale",
                target=target_label,
                status="pass",
                message=f"Good portrait occupancy ({bbox_occupancy:.1%} bbox, {opaque_ratio:.1%} opaque)",
            )
        )

    # 2. Abnormal vertical stretch / horizontal squishing check (mainly on raw cutouts before bottom text)
    max_aspect = 1.74 if is_duo else 2.12
    if is_raw and aspect_hw > max_aspect:
        checks.append(
            ValidationCheck(
                name="Strict QA: Aspect & Proportion",
                target=target_label,
                status="fail" if strict else "warn",
                message=(
                    f"Silhouette abnormally tall/narrow (H/W={aspect_hw:.2f} > {max_aspect:.2f}) — "
                    f"risk of vertically stretched face/body or horizontally squished duo subjects"
                ),
                details={"defect_code": "stretched_or_warped_face", "aspect_hw": aspect_hw, "max_aspect": max_aspect},
            )
        )
    else:
        checks.append(
            ValidationCheck(
                name="Strict QA: Aspect & Proportion",
                target=target_label,
                status="pass",
                message=f"Natural silhouette aspect ratio (H/W={aspect_hw:.2f})",
            )
        )

    # 3. Raw top-edge hard truncation (head crown or raised hand sliced flat at y=0)
    if is_raw and w >= 32:
        apx = alpha.load()
        top_opaque = sum(1 for x in range(w) if apx[x, 0] > 160) / float(w)
        metrics["top_edge_opaque_ratio"] = round(top_opaque, 4)
        if top_opaque > 0.20:
            checks.append(
                ValidationCheck(
                    name="Strict QA: Head/Hand Top Headroom",
                    target=target_label,
                    status="fail" if (strict and top_opaque > 0.30) else "warn",
                    message=f"Top edge heavily clipped ({top_opaque:.1%} of y=0 opaque) — head crown or raised hand cut off",
                    details={"defect_code": "hard_edge_clip", "top_edge_opaque_ratio": top_opaque},
                )
            )

    # 4. Disconnected floating islands on raw cutouts (severed hands / stray AI text / fragments)
    if is_raw and len(comps) > 1:
        primary = [comps[0]]
        start_idx = 1
        # In duo stickers, Person B may be a second large adjacent silhouette
        if is_duo and comps[1]["area_ratio"] >= 0.065:
            primary.append(comps[1])
            start_idx = 2

        suspicious = []
        for extra in comps[start_idx:]:
            area_r = extra["area_ratio"]
            if area_r < 0.0035:
                continue  # tiny hair wisp / earring / confetti speck
            gap = min(_bbox_gap(extra["bbox"], p["bbox"]) for p in primary)
            if gap >= 0.025 or area_r >= 0.008:
                suspicious.append({"area_ratio": round(area_r, 4), "gap": round(gap, 4)})

        metrics["suspicious_islands"] = len(suspicious)
        if suspicious:
            checks.append(
                ValidationCheck(
                    name="Strict QA: Disconnected Limb / Fragment Islands",
                    target=target_label,
                    status="fail" if strict else "warn",
                    message=(
                        f"Detected {len(suspicious)} detached foreground island(s) on raw cutout "
                        f"(largest={suspicious[0]['area_ratio']:.1%}) — possible floating hand, stray AI text, or artifact"
                    ),
                    details={"defect_code": "floating_island", "islands": suspicious},
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    name="Strict QA: Disconnected Limb / Fragment Islands",
                    target=target_label,
                    status="pass",
                    message="Clean cohesive subject silhouette (zero detached islands)",
                )
            )

    return checks, metrics


# ---------------------------------------------------------------------------
# 3. 2x2 Sprite Sheet Consistency & Cross-Bleed Checker
# ---------------------------------------------------------------------------


def audit_sprite_sheet_image(
    sheet_img: Image.Image,
    target_label: str = "sprite_sheet",
    *,
    is_duo: bool = False,
    strict: bool = True,
) -> Tuple[List[ValidationCheck], Dict[str, Any]]:
    """Validate a 2x2 4-frame raw action sprite sheet before slicing into GIF frames."""
    checks: List[ValidationCheck] = [detect_baked_checkerboard(sheet_img, target_label=target_label)]
    rgba = ensure_alpha_channel(sheet_img)
    w, h = rgba.size
    hw, hh = w // 2, h // 2
    if hw < 32 or hh < 32:
        checks.append(
            ValidationCheck(
                name="Strict QA: Sprite Sheet Size",
                target=target_label,
                status="fail",
                message=f"Sprite sheet {w}x{h} too small for 2x2 slicing",
                details={"defect_code": "sprite_quadrant_mismatch"},
            )
        )
        return checks, {}

    quads = [
        ("TL", rgba.crop((0, 0, hw, hh))),
        ("TR", rgba.crop((hw, 0, w, hh))),
        ("BL", rgba.crop((0, hh, hw, h))),
        ("BR", rgba.crop((hw, hh, w, h))),
    ]
    cleaned_quads: List[Tuple[str, Image.Image]] = [(name, remove_background_smart(q, mode="color")) for name, q in quads]

    widths: List[int] = []
    heights: List[int] = []
    empties: List[str] = []
    for name, cq in cleaned_quads:
        bb = cq.getchannel("A").getbbox()
        if not bb or ((bb[2] - bb[0]) * (bb[3] - bb[1])) / float(hw * hh) < 0.08:
            empties.append(name)
        else:
            widths.append(bb[2] - bb[0])
            heights.append(bb[3] - bb[1])

    metrics: Dict[str, Any] = {"quadrant_widths": widths, "quadrant_heights": heights}
    if empties:
        checks.append(
            ValidationCheck(
                name="Strict QA: Sprite Quadrants Populated",
                target=target_label,
                status="fail",
                message=f"Empty or tiny quadrant(s) in 2x2 sprite sheet: {', '.join(empties)}",
                details={"defect_code": "sprite_quadrant_mismatch", "empty_quadrants": empties},
            )
        )
        return checks, metrics

    h_ratio = max(heights) / float(max(1, min(heights)))
    w_ratio = max(widths) / float(max(1, min(widths)))
    metrics["height_spread_ratio"] = round(h_ratio, 3)
    metrics["width_spread_ratio"] = round(w_ratio, 3)

    if h_ratio > 1.38 or w_ratio > 1.45:
        checks.append(
            ValidationCheck(
                name="Strict QA: Sprite Scale Consistency",
                target=target_label,
                status="fail" if strict else "warn",
                message=(
                    f"Inconsistent character scale across 4 quadrants "
                    f"(height ratio={h_ratio:.2f}, width ratio={w_ratio:.2f})"
                ),
                details={"defect_code": "sprite_quadrant_mismatch", "h_ratio": h_ratio, "w_ratio": w_ratio},
            )
        )
    else:
        checks.append(
            ValidationCheck(
                name="Strict QA: Sprite Scale Consistency",
                target=target_label,
                status="pass",
                message=f"Consistent scale across 4 quadrants (H spread={h_ratio:.2f}, W spread={w_ratio:.2f})",
            )
        )

    # Check vertical centerline bleed (left/right quadrants colliding across x = hw)
    full_clean = remove_background_smart(rgba, mode="color")
    f_alpha = full_clean.getchannel("A")
    fpx = f_alpha.load()
    v_seam_opaque = sum(1 for y in range(h) if fpx[hw, y] > 180) / float(h)
    metrics["vertical_seam_opaque_ratio"] = round(v_seam_opaque, 4)
    if v_seam_opaque > 0.26:
        checks.append(
            ValidationCheck(
                name="Strict QA: Sprite Quadrant Separation",
                target=target_label,
                status="fail" if (strict and v_seam_opaque > 0.40) else "warn",
                message=f"Characters/limbs bleed across vertical 2x2 centerline ({v_seam_opaque:.1%} seam opaque)",
                details={"defect_code": "sprite_quadrant_mismatch", "vertical_seam_opaque_ratio": v_seam_opaque},
            )
        )

    # Check identical frames (fake static copy)
    raw_bytes = [cq.tobytes() for _, cq in cleaned_quads]
    if all(b == raw_bytes[0] for b in raw_bytes[1:]):
        checks.append(
            ValidationCheck(
                name="Strict QA: Sprite Distinct Action",
                target=target_label,
                status="fail",
                message="All 4 sprite sheet quadrants are identical — no genuine multi-frame action",
                details={"defect_code": "sprite_quadrant_mismatch"},
            )
        )

    # Run checkerboard + proportion check on Frame 1 (TL) as representative
    q_checks, _ = analyze_cutout_geometry(cleaned_quads[0][1], target_label=f"{target_label}[TL]", is_duo=is_duo, is_raw=True, strict=strict)
    checks.extend(q_checks)
    return checks, metrics


# ---------------------------------------------------------------------------
# 4. Optional Multimodal VLM Anatomy & Facial-Proportion Verifier
# ---------------------------------------------------------------------------

_VLM_AUDIT_SYSTEM_PROMPT = """You are a strict forensic quality inspector for photorealistic real-person chat stickers.
Inspect the generated sticker image (and its 2x zoomed face/shoulder/hand crops, plus any reference photo) for anatomical hallucinations and facial distortion.
Check EVERY rule strictly:
1. ARM & HAND TOPOLOGY (P0):
   - Single-person sticker: strictly <= 2 arms and <= 2 hands (1 left, 1 right).
   - Two-person (duo) sticker: strictly <= 4 arms and <= 4 hands total (<= 2 per person).
   - SAME-SHOULDER DUAL-ARM SPLIT ("3rd hand"): Check carefully whether a person has a sleeve/arm hanging down at their side AND simultaneously a second raised arm emerging from behind that exact same shoulder to touch hair/head/cheek/prop. If yes -> FAIL ('third_hand_or_extra_limb').
   - Disembodied floating hands on shoulders/waists, 6+ fingers, or melted tentacle fingers -> FAIL ('third_hand_or_extra_limb').
2. FACIAL PROPORTION & GEOMETRY (P0):
   - Compare facial width-to-height ratio against natural human proportions (and reference photo if shown).
   - If the midface, nose bridge, philtrum, or chin is vertically elongated/stretched ("horse-face distortion") or horizontally squished -> FAIL ('stretched_or_warped_face').
3. REAL HUMAN EYES & IDENTITY (P0):
   - If 2D cartoon swirl eyes (@_@), star/heart/coin stickers covering eyeballs, or 2D anime conversion -> FAIL ('cartoon_eyes_or_drift').
4. CLEAN TRANSPARENCY (P0):
   - If grey-and-white checkerboard squares are painted into the background -> FAIL ('baked_checkerboard').

Respond ONLY with valid JSON matching:
{
  "passed": true/false,
  "person_count": 1,
  "arms_per_person": [2],
  "same_shoulder_dual_arm": false,
  "face_vertically_stretched": false,
  "cartoon_eyes_or_2d": false,
  "baked_checkerboard": false,
  "defect_codes": [],
  "reason": "brief explanation"
}"""


def _build_vlm_composite_panel(
    sticker_img: Image.Image,
    reference_paths: Optional[Sequence[Path]] = None,
) -> bytes:
    """Create a compact side-by-side image [Reference | Full Sticker | 2x Face+Shoulders Crop] as PNG bytes."""
    cutout = _prepare_cutout_for_analysis(sticker_img, is_raw=True)
    bbox = cutout.getchannel("A").getbbox() or (0, 0, cutout.width, cutout.height)
    x0, y0, x1, y1 = bbox
    bw, bh = max(1, x1 - x0), max(1, y1 - y0)

    # Upper 62% of subject bbox captures head, face, both shoulders, sleeves, and raised hands
    head_crop = ensure_alpha_channel(sticker_img).crop(
        (max(0, x0 - int(bw * 0.06)), max(0, y0 - int(bh * 0.04)), min(sticker_img.width, x1 + int(bw * 0.06)), min(sticker_img.height, y0 + int(bh * 0.65)))
    )

    panel_h = 420
    panels: List[Tuple[str, Image.Image]] = []
    for idx, rp in enumerate(list(reference_paths or [])[:2], 1):
        if rp and rp.exists():
            try:
                with Image.open(rp) as rim:
                    rc = rim.convert("RGBA")
                    rc.thumbnail((320, panel_h - 40), Image.Resampling.LANCZOS)
                    panels.append((f"Ref {idx}", rc))
            except Exception:
                pass

    full_c = ensure_alpha_channel(sticker_img).copy()
    full_c.thumbnail((380, panel_h - 40), Image.Resampling.LANCZOS)
    panels.append(("Generated Full", full_c))

    zoom_c = head_crop.copy()
    zoom_c.thumbnail((380, panel_h - 40), Image.Resampling.LANCZOS)
    panels.append(("2x Zoom Face & Shoulders", zoom_c))

    total_w = sum(p[1].width + 24 for p in panels) + 16
    board = Image.new("RGB", (total_w, panel_h), (36, 40, 52))
    draw = ImageDraw.Draw(board)
    cx = 12
    for title, pim in panels:
        draw.text((cx + 4, 8), title, fill=(240, 244, 250))
        board.paste(pim, (cx, 30), pim)
        cx += pim.width + 24

    buf = io.BytesIO()
    board.save(buf, format="PNG")
    return buf.getvalue()


def _parse_json_dict(raw_text: str) -> Dict[str, Any]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]
    return json.loads(cleaned)


def verify_anatomy_with_vlm(
    img_or_path: Image.Image | Path,
    *,
    reference_paths: Optional[Sequence[Path]] = None,
    is_duo: bool = False,
    target_label: str = "image",
    timeout_s: int = 45,
) -> Optional[ValidationCheck]:
    """Run multimodal Vision API anatomy & face-proportion check when OPENAI_API_KEY or GEMINI_API_KEY is available.

    Returns ``None`` if no Vision API key is configured.
    """
    settings = AppSettings()
    if isinstance(img_or_path, Path):
        with Image.open(img_or_path) as opened:
            sticker_img = opened.convert("RGBA")
    else:
        sticker_img = ensure_alpha_channel(img_or_path)

    panel_bytes = _build_vlm_composite_panel(sticker_img, reference_paths=reference_paths)
    b64 = base64.b64encode(panel_bytes).decode("ascii")
    mode_hint = "TWO-PERSON (duo, max 4 arms total, max 2 per person)" if is_duo else "SINGLE-PERSON (max 2 arms total, 1 per shoulder)"
    user_text = (
        f"Mode: {mode_hint}. Inspect 'Generated Full' and '2x Zoom Face & Shoulders' against any Reference photo(s). "
        f"Count every arm and sleeve carefully and check facial width-to-height proportions."
    )

    verdict: Optional[Dict[str, Any]] = None
    if settings.openai_api_key:
        url = settings.openai_base_url.rstrip("/") + "/chat/completions"
        vlm_model = settings.sticker_vision_model or "gpt-4o-mini"
        payload = {
            "model": vlm_model,
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": _VLM_AUDIT_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "high"}},
                    ],
                },
            ],
        }
        try:
            resp = requests.post(
                url,
                headers={"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=timeout_s,
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            verdict = _parse_json_dict(content)
        except Exception as e:
            logger.warning("OpenAI VLM QA check skipped/failed for %s: %s", target_label, e)
            return None
    elif settings.gemini_api_key:
        gem_model = "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{gem_model}:generateContent?key={settings.gemini_api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": _VLM_AUDIT_SYSTEM_PROMPT + "\n\n" + user_text},
                        {"inline_data": {"mime_type": "image/png", "data": b64}},
                    ]
                }
            ],
            "generationConfig": {"temperature": 0.0, "responseMimeType": "application/json"},
        }
        try:
            resp = requests.post(url, json=payload, timeout=timeout_s)
            resp.raise_for_status()
            content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            verdict = _parse_json_dict(content)
        except Exception as e:
            logger.warning("Gemini VLM QA check skipped/failed for %s: %s", target_label, e)
            return None
    else:
        return None

    if not verdict:
        return None

    codes: List[str] = list(verdict.get("defect_codes") or [])
    arms = verdict.get("arms_per_person") or []
    if verdict.get("same_shoulder_dual_arm") or any(isinstance(a, int) and a > 2 for a in arms):
        if "third_hand_or_extra_limb" not in codes:
            codes.append("third_hand_or_extra_limb")
    if verdict.get("face_vertically_stretched"):
        if "stretched_or_warped_face" not in codes:
            codes.append("stretched_or_warped_face")
    if verdict.get("cartoon_eyes_or_2d"):
        if "cartoon_eyes_or_drift" not in codes:
            codes.append("cartoon_eyes_or_drift")
    if verdict.get("baked_checkerboard"):
        if "baked_checkerboard" not in codes:
            codes.append("baked_checkerboard")

    passed = bool(verdict.get("passed", True)) and not codes
    reason = str(verdict.get("reason") or ("VLM anatomy & proportion check passed" if passed else "VLM detected defect"))
    return ValidationCheck(
        name="Strict QA: VLM Anatomy & Proportion Judge",
        target=target_label,
        status="pass" if passed else "fail",
        message=reason,
        details={"defect_codes": codes, "verdict": verdict, "defect_code": codes[0] if codes else ""},
    )


# ---------------------------------------------------------------------------
# 5. Unified Single-Image & Directory Strict Audit + 2x Zoom Contact Sheet
# ---------------------------------------------------------------------------


def audit_single_image(
    path: Path,
    *,
    item_id: Optional[str] = None,
    is_duo: Optional[bool] = None,
    is_raw: bool = True,
    is_sprite_sheet: bool = False,
    strict: bool = True,
    use_vlm: bool = False,
    reference_paths: Optional[Sequence[Path]] = None,
) -> ItemStrictAudit:
    """Run all strict red-line checks on a single image file and synthesize corrective retry instructions."""
    iid = item_id or path.stem.replace("_sheet_raw", "").replace("_raw", "")
    inferred_duo = bool(re.match(r"^d\d+_", iid)) if is_duo is None else is_duo
    rel = str(path)

    if not path.exists():
        chk = ValidationCheck(
            name="Strict QA: File Exists",
            target=rel,
            status="fail",
            message=f"File not found: {path}",
        )
        return ItemStrictAudit(item_id=iid, target_path=rel, status="fail", checks=[chk])

    with Image.open(path) as opened:
        rgba = opened.convert("RGBA")

    checks: List[ValidationCheck] = []
    metrics: Dict[str, Any] = {}
    if is_sprite_sheet:
        s_checks, s_metrics = audit_sprite_sheet_image(rgba, target_label=rel, is_duo=inferred_duo, strict=strict)
        checks.extend(s_checks)
        metrics.update(s_metrics)
    else:
        checks.append(detect_baked_checkerboard(rgba, target_label=rel))
        g_checks, g_metrics = analyze_cutout_geometry(
            rgba, target_label=rel, is_duo=inferred_duo, is_raw=is_raw, strict=strict
        )
        checks.extend(g_checks)
        metrics.update(g_metrics)

    if use_vlm:
        vlm_chk = verify_anatomy_with_vlm(
            rgba,
            reference_paths=reference_paths,
            is_duo=inferred_duo,
            target_label=rel,
        )
        if vlm_chk is not None:
            checks.append(vlm_chk)

    defect_codes: List[str] = []
    for c in checks:
        if c.status in ("fail", "warn"):
            for dc in [c.details.get("defect_code"), *(c.details.get("defect_codes") or [])]:
                if dc and dc not in defect_codes:
                    defect_codes.append(dc)

    has_fail = any(c.status == "fail" for c in checks)
    has_warn = any(c.status == "warn" for c in checks)
    overall = "fail" if has_fail else ("warn" if has_warn else "pass")
    retry_suffix = ""
    if defect_codes:
        retry_suffix = build_corrective_retry_prompt("", defect_codes).strip()

    return ItemStrictAudit(
        item_id=iid,
        target_path=rel,
        status=overall,
        defect_codes=defect_codes,
        checks=checks,
        metrics=metrics,
        corrective_prompt_suffix=retry_suffix,
    )


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    fp = get_default_font_path()
    if fp:
        try:
            return ImageFont.truetype(fp, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def _paste_contain(
    dest: Image.Image,
    src: Image.Image,
    box: Tuple[int, int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    bw, bh = max(8, x1 - x0), max(8, y1 - y0)
    cp = ensure_alpha_channel(src).copy()
    cp.thumbnail((bw, bh), Image.Resampling.LANCZOS)
    px = x0 + (bw - cp.width) // 2
    py = y0 + (bh - cp.height) // 2
    dest.paste(cp, (px, py), cp)


def generate_strict_audit_sheet(
    audits: Sequence[ItemStrictAudit],
    output_path: Path,
    title: str = "STRICT ANATOMY & PROPORTION QA AUDIT SHEET (2x FACE / SHOULDER / HAND ZOOM)",
) -> Optional[Path]:
    """Render a high-magnification 3-panel-per-sticker inspection board for Codex & human QA.

    Each sticker card shows:
      - Panel 1: Full cutout over a high-contrast dark-slate / warm-coral split background
      - Panel 2: 2.2x zoomed Head, Face & Shoulders crop (catches elongated face & dual-arm shoulder split)
      - Panel 3: 2.0x zoomed Sleeves, Hands & Props crop (catches 3rd hand, 6th finger, disembodied hands)
    """
    valid = [a for a in audits if Path(a.target_path).exists()]
    if not valid:
        return None

    cols = 2 if len(valid) > 1 else 1
    rows = int(math.ceil(len(valid) / float(cols)))

    card_w = 736
    card_h = 336
    pad = 18
    header_h = 88
    sheet_w = cols * (card_w + pad) + pad
    sheet_h = header_h + rows * (card_h + pad) + pad

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (239, 242, 247, 255))
    draw = ImageDraw.Draw(sheet)

    f_title = _load_font(20)
    f_sub = _load_font(13)
    f_card = _load_font(15)
    f_small = _load_font(12)

    # Header banner
    draw.rectangle([0, 0, sheet_w, header_h], fill=(24, 29, 40, 255))
    n_pass = sum(1 for a in valid if a.status == "pass")
    n_warn = sum(1 for a in valid if a.status == "warn")
    n_fail = sum(1 for a in valid if a.status == "fail")
    draw.text((pad, 14), title, fill=(255, 255, 255, 255), font=f_title)
    draw.text(
        (pad, 46),
        (
            f"Items: {len(valid)}  |  PASS: {n_pass}  WARN: {n_warn}  FAIL: {n_fail}  |  "
            f"Red-Lines: [1] <=2 Arms/Person (No Hanging Sleeve + Raised Arm)  "
            f"[2] Natural Face Width:Height  [3] 5 Fingers  [4] Real Eyes  [5] Zero Checkerboard"
        ),
        fill=(196, 208, 228, 255),
        font=f_sub,
    )

    status_colors = {
        "pass": ((18, 138, 74, 255), (232, 248, 238, 255)),
        "warn": ((186, 112, 12, 255), (255, 247, 230, 255)),
        "fail": ((204, 34, 48, 255), (254, 235, 238, 255)),
    }

    for idx, aud in enumerate(valid):
        r, c = divmod(idx, cols)
        cx = pad + c * (card_w + pad)
        cy = header_h + pad + r * (card_h + pad)
        fg_col, bg_tint = status_colors.get(aud.status, status_colors["pass"])

        # Card container
        draw.rounded_rectangle(
            [cx, cy, cx + card_w, cy + card_h],
            radius=12,
            fill=(255, 255, 255, 255),
            outline=fg_col if aud.status != "pass" else (210, 216, 226, 255),
            width=3 if aud.status == "fail" else 2,
        )

        # Card top bar
        draw.rounded_rectangle([cx + 2, cy + 2, cx + card_w - 2, cy + 36], radius=10, fill=bg_tint)
        badge_w = 68
        draw.rounded_rectangle([cx + 10, cy + 7, cx + 10 + badge_w, cy + 31], radius=6, fill=fg_col)
        draw.text((cx + 22, cy + 10), aud.status.upper(), fill=(255, 255, 255, 255), font=f_small)
        draw.text((cx + 88, cy + 9), f"#{idx + 1:02d}  {aud.item_id}", fill=(22, 26, 36, 255), font=f_card)

        hw_val = aud.metrics.get("aspect_hw", "-")
        occ_val = aud.metrics.get("bbox_occupancy")
        occ_str = f"{occ_val:.0%}" if isinstance(occ_val, float) else "-"
        isl_val = aud.metrics.get("suspicious_islands", 0)
        draw.text(
            (cx + card_w - 245, cy + 11),
            f"H/W:{hw_val}  Occ:{occ_str}  Islands:{isl_val}",
            fill=(75, 85, 102, 255),
            font=f_small,
        )

        p_top = cy + 44
        p_bot = cy + card_h - 34
        p_h = p_bot - p_top

        # Panel 1: Full cutout over split dark-slate / warm-coral backdrop
        p1_x0, p1_x1 = cx + 12, cx + 244
        draw.rectangle([p1_x0, p_top, p1_x1, p_top + p_h // 2], fill=(34, 41, 56, 255))
        draw.rectangle([p1_x0, p_top + p_h // 2, p1_x1, p_bot], fill=(242, 216, 205, 255))
        draw.rectangle([p1_x0, p_top, p1_x1, p_bot], outline=(200, 206, 216, 255))

        # Panel 2: 2.2x Face & Shoulders zoom
        p2_x0, p2_x1 = cx + 254, cx + 486
        draw.rectangle([p2_x0, p_top, p2_x1, p_bot], fill=(246, 248, 252, 255), outline=(200, 206, 216, 255))

        # Panel 3: 2.0x Hands & Sleeves zoom
        p3_x0, p3_x1 = cx + 496, cx + card_w - 12
        draw.rectangle([p3_x0, p_top, p3_x1, p_bot], fill=(246, 248, 252, 255), outline=(200, 206, 216, 255))

        try:
            with Image.open(aud.target_path) as im_raw:
                rgba = im_raw.convert("RGBA")
                cutout = _prepare_cutout_for_analysis(rgba, is_raw=True)
                comps, _gw, _gh = _connected_components_grid(cutout.getchannel("A"))
                if comps:
                    # Focus zoom crops on the largest connected silhouette (ignores floating speech bubbles / captions)
                    rx0, ry0, rx1, ry1 = comps[0]["bbox"]
                    if len(comps) > 1 and comps[1]["area_ratio"] >= 0.08 and comps[1]["bbox"][3] > 0.55:
                        rx0 = min(rx0, comps[1]["bbox"][0])
                        ry0 = min(ry0, comps[1]["bbox"][1])
                        rx1 = max(rx1, comps[1]["bbox"][2])
                        ry1 = max(ry1, comps[1]["bbox"][3])
                    bx0 = int(rx0 * rgba.width)
                    by0 = int(ry0 * rgba.height)
                    bx1 = int(rx1 * rgba.width)
                    by1 = int(ry1 * rgba.height)
                else:
                    bx0, by0, bx1, by1 = cutout.getchannel("A").getbbox() or (0, 0, rgba.width, rgba.height)
                bw, bh = max(1, bx1 - bx0), max(1, by1 - by0)

                face_shoulders = rgba.crop(
                    (
                        max(0, bx0 - int(bw * 0.05)),
                        max(0, by0 - int(bh * 0.03)),
                        min(rgba.width, bx1 + int(bw * 0.05)),
                        min(rgba.height, by0 + int(bh * 0.58)),
                    )
                )
                hands_sleeves = rgba.crop(
                    (
                        max(0, bx0 - int(bw * 0.05)),
                        max(0, by0 + int(bh * 0.24)),
                        min(rgba.width, bx1 + int(bw * 0.05)),
                        min(rgba.height, min(by1, by0 + int(bh * 0.94))),
                    )
                )

                _paste_contain(sheet, rgba, (p1_x0 + 6, p_top + 6, p1_x1 - 6, p_bot - 20))
                _paste_contain(sheet, face_shoulders, (p2_x0 + 6, p_top + 6, p2_x1 - 6, p_bot - 20))
                _paste_contain(sheet, hands_sleeves, (p3_x0 + 6, p_top + 6, p3_x1 - 6, p_bot - 20))
        except Exception as e:
            draw.text((p1_x0 + 8, p_top + 12), f"Load error: {e}", fill=(220, 40, 40, 255), font=f_small)

        draw.text((p1_x0 + 6, p_bot - 17), "1x Full (Split Contrast)", fill=(35, 40, 52, 255), font=f_small)
        draw.text((p2_x0 + 6, p_bot - 17), "2x Face & Shoulders", fill=(55, 65, 82, 255), font=f_small)
        draw.text((p3_x0 + 6, p_bot - 17), "2x Sleeves & Hands", fill=(55, 65, 82, 255), font=f_small)

        # Footer defect / verification note
        if aud.defect_codes:
            note = "DEFECTS: " + ", ".join(aud.defect_codes)
            note_col = fg_col
        else:
            note = "Verify visually: <=2 arms/person (no dual-arm shoulder) | natural face ratio | 5 fingers"
            note_col = (88, 98, 116, 255)
        draw.text((cx + 14, cy + card_h - 25), note[:96], fill=note_col, font=f_small)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() in (".jpg", ".jpeg"):
        sheet.convert("RGB").save(output_path, format="JPEG", quality=92, optimize=True)
    else:
        sheet.save(output_path, format="PNG")
    return output_path


def audit_pack_directory(
    output_dir: Path,
    *,
    strict: bool = True,
    use_vlm: bool = False,
    prefer_raw: bool = True,
) -> Dict[str, Any]:
    """Run strict anatomy & quality audit across an entire job/pack directory.

    Inspects raw cutouts (`work/raw_static`, `work/raw_gif`) when available, plus composed
    static stickers (`static/*.png` or `*.png`), writes `qa/strict-audit.json`, `qa/strict-audit.md`,
    and `qa/strict-audit-sheet.jpg`.
    """
    raw_static_dir = output_dir / "work" / "raw_static"
    raw_gif_dir = output_dir / "work" / "raw_gif"
    static_dir = output_dir / "static"

    refs: List[Path] = []
    work_dir = output_dir / "work"
    if work_dir.exists():
        refs.extend(sorted(work_dir.glob("source_normalized_*")))
        refs.extend(sorted(work_dir.glob("partner_normalized_*")))
        anchor = work_dir / "character-anchor.png"
        if anchor.exists():
            refs.append(anchor)

    is_duo_job: Optional[bool] = None
    job_file = output_dir / "job.json"
    if job_file.exists():
        try:
            jdata = json.loads(job_file.read_text(encoding="utf-8"))
            if jdata.get("pack_type") == "duo" or jdata.get("partner_image") or jdata.get("duo_categories"):
                is_duo_job = True
        except Exception:
            pass

    audits: List[ItemStrictAudit] = []
    sheet_targets_for_contact: List[ItemStrictAudit] = []

    raw_files = sorted(raw_static_dir.glob("*_raw.png")) if raw_static_dir.exists() else []
    sprite_files = sorted(raw_gif_dir.glob("*_sheet_raw.png")) if raw_gif_dir.exists() else []
    composed_files = sorted(static_dir.glob("*.png")) if static_dir.exists() else []
    if not raw_files and not sprite_files and not composed_files:
        composed_files = sorted(p for p in output_dir.glob("*.png") if "sheet" not in p.name and "preview" not in p.name)

    if prefer_raw and raw_files:
        for rf in raw_files:
            aud = audit_single_image(
                rf,
                is_duo=is_duo_job,
                is_raw=True,
                strict=strict,
                use_vlm=use_vlm,
                reference_paths=refs,
            )
            audits.append(aud)
            sheet_targets_for_contact.append(aud)
    elif composed_files:
        for cf in composed_files:
            aud = audit_single_image(
                cf,
                is_duo=is_duo_job,
                is_raw=False,
                strict=strict,
                use_vlm=use_vlm,
                reference_paths=refs,
            )
            audits.append(aud)
            sheet_targets_for_contact.append(aud)

    for sf in sprite_files:
        saud = audit_single_image(
            sf,
            item_id=f"{sf.stem.replace('_sheet_raw', '')}[2x2_sheet]",
            is_duo=is_duo_job,
            is_raw=True,
            is_sprite_sheet=True,
            strict=strict,
            use_vlm=False,
        )
        audits.append(saud)
        if not sheet_targets_for_contact:
            sheet_targets_for_contact.append(saud)

    qa_dir = output_dir / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    sheet_path = generate_strict_audit_sheet(
        sheet_targets_for_contact or audits,
        qa_dir / "strict-audit-sheet.jpg",
    )

    n_fail = sum(1 for a in audits if a.status == "fail")
    n_warn = sum(1 for a in audits if a.status == "warn")
    n_pass = sum(1 for a in audits if a.status == "pass")
    overall = "fail" if n_fail > 0 else ("warn" if n_warn > 0 else "pass")

    payload: Dict[str, Any] = {
        "job_id": output_dir.name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "strict": strict,
        "vlm_used": use_vlm,
        "overall_status": overall,
        "counts": {"total": len(audits), "pass": n_pass, "warn": n_warn, "fail": n_fail},
        "audit_sheet": str(sheet_path) if sheet_path else None,
        "items": [a.to_dict() for a in audits],
    }

    json_out = qa_dir / "strict-audit.json"
    json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = [
        f"# Strict Anatomy & Quality Audit Report: {output_dir.name}",
        "",
        f"- **Timestamp**: {payload['timestamp']}",
        f"- **Overall Status**: **{overall.upper()}** (`pass={n_pass}`, `warn={n_warn}`, `fail={n_fail}`)",
        f"- **2x Magnified Audit Sheet**: `{sheet_path.name if sheet_path else 'N/A'}`",
        f"- **Standard Spec**: `references/quality-standards.md`",
        "",
        "## Item Results",
        "",
        "| Item | Status | Defect Codes | H/W | Occupancy | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for a in audits:
        icon = "✅" if a.status == "pass" else ("⚠️" if a.status == "warn" else "❌")
        codes_str = ", ".join(f"`{c}`" for c in a.defect_codes) or "-"
        hw = a.metrics.get("aspect_hw", "-")
        occ = a.metrics.get("bbox_occupancy")
        occ_s = f"{occ:.1%}" if isinstance(occ, float) else "-"
        bad_msgs = [c.message for c in a.checks if c.status != "pass"]
        note = "; ".join(bad_msgs) if bad_msgs else "Passed programmatic checks — verify 2x zoom sheet for 3rd hand / face ratio"
        md_lines.append(f"| `{a.item_id}` | {icon} {a.status.upper()} | {codes_str} | {hw} | {occ_s} | {note} |")

    failed_or_warned = [a for a in audits if a.defect_codes]
    if failed_or_warned:
        md_lines.extend(["", "## Corrective Retry Prompts for Defective Items", ""])
        for a in failed_or_warned:
            md_lines.append(f"### `{a.item_id}` ({', '.join(a.defect_codes)})")
            md_lines.append("```text")
            md_lines.append(a.corrective_prompt_suffix)
            md_lines.append("```")
            md_lines.append("")

    md_out = qa_dir / "strict-audit.md"
    md_out.write_text("\n".join(md_lines), encoding="utf-8")
    payload["report_json"] = str(json_out)
    payload["report_md"] = str(md_out)
    return payload
