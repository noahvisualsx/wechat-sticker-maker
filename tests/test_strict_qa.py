"""Tests for strict real-person anatomy, facial-proportion, checkerboard, and auto-retry QA gate."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import MagicMock, patch

from PIL import Image, ImageDraw
import pytest

from sticker_maker.duo import build_duo_sprite_sheet_prompt, build_duo_static_prompt, load_duo_presets
from sticker_maker.orchestrator import StickerOrchestrator
from sticker_maker.prompts import (
    ANATOMY_AND_PROPORTION_HARD_LOCK,
    CLEAN_BACKGROUND_HARD_LOCK,
    DUO_ANATOMY_AND_PROPORTION_LOCK,
    build_anchor_prompt,
    build_corrective_retry_prompt,
    build_sprite_sheet_prompt,
    build_static_prompt,
)
from sticker_maker.providers.fake import FakeStickerProvider
from sticker_maker.quality.anatomy import (
    analyze_cutout_geometry,
    audit_pack_directory,
    audit_single_image,
    audit_sprite_sheet_image,
    detect_baked_checkerboard,
    generate_strict_audit_sheet,
    verify_anatomy_with_vlm,
)
from sticker_maker.schemas import ActionMotion, CharacterBible, ExpressionItem, JobConfig


def _sample_bible(tmp_path: Path) -> CharacterBible:
    return CharacterBible(
        character_id="strict_qa_char",
        source_sha256="a" * 64,
        subject_type="human-portrait",
        identity_facts=["long dark wavy hair", "oval face with natural proportions"],
        locked_attributes=["bone structure", "hairstyle", "outfit"],
        master_anchor=str(tmp_path / "anchor.png"),
        reference_image=str(tmp_path / "source.png"),
    )


def _sample_expr() -> ExpressionItem:
    return ExpressionItem(
        id="01_hello",
        caption="你好",
        mood="warm greeting",
        static_pose="chest-up portrait waving one hand warmly with a natural smile",
        motion=ActionMotion(type="wave"),
    )


def _make_checkerboard_image(size: int = 512, cell: int = 24, grey: int = 241, post_matte: bool = False) -> Image.Image:
    """Create a synthetic image with a baked-in grey/white checkerboard background."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for y in range(0, size, cell):
        for x in range(0, size, cell):
            is_grey = ((x // cell) + (y // cell)) % 2 == 1
            if is_grey:
                draw.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(grey, grey, grey, 255))
            elif not post_matte:
                draw.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(255, 255, 255, 255))
    # Draw a central portrait silhouette over the checkerboard
    draw.ellipse([170, 110, 342, 310], fill=(245, 212, 196, 255))
    draw.pieslice([130, 290, 382, 510], start=180, end=360, fill=(40, 68, 112, 255))
    return img


def test_prompts_enforce_anatomy_face_ratio_and_zero_checkerboard(tmp_path: Path):
    bible = _sample_bible(tmp_path)
    expr = _sample_expr()

    static_p = build_static_prompt(bible, expr)
    anchor_p = build_anchor_prompt("human-portrait", bible.identity_facts)
    sprite_p = build_sprite_sheet_prompt(bible, expr)

    for p in (static_p, anchor_p, sprite_p):
        assert "ZERO 3rd hands" in p
        assert "CRANIOFACIAL ASPECT RATIO LOCK" in p
        assert "checkerboard" in p.lower()

    duos = {d.id: d for d in load_duo_presets()}
    d03 = duos["d03_bestie_hype_queen"]
    assert "hype-claps and holds up a phone" not in d03.static_pose
    assert "starry-eyed" not in d03.static_pose
    assert "strictly 2 arms" in d03.static_pose

    duo_static = build_duo_static_prompt(bible, d03)
    duo_sheet = build_duo_sprite_sheet_prompt(bible, d03)
    assert DUO_ANATOMY_AND_PROPORTION_LOCK in duo_static
    assert CLEAN_BACKGROUND_HARD_LOCK in duo_static
    assert DUO_ANATOMY_AND_PROPORTION_LOCK in duo_sheet
    assert ANATOMY_AND_PROPORTION_HARD_LOCK in static_p


def test_corrective_retry_prompt_targets_specific_defects():
    retried = build_corrective_retry_prompt(
        "Base prompt.",
        ["third_hand_or_extra_limb", "stretched_or_warped_face", "baked_checkerboard"],
        custom_note="Ensure blue knit sleeve lifts upward with right arm.",
    )
    assert "[CRITICAL RETRY CORRECTION — STRICT QUALITY GATE]" in retried
    assert "REJECTED FOR EXTRA ARM / 3RD HAND" in retried
    assert "REJECTED FOR STRETCHED / ELONGATED FACE" in retried
    assert "REJECTED FOR BAKED-IN CHECKERBOARD" in retried
    assert "Ensure blue knit sleeve lifts upward with right arm." in retried


def test_baked_checkerboard_detector_catches_subtle_and_post_matte_grids(tmp_path: Path):
    # 1. Subtle Codex light-mode checkerboard (#FFFFFF vs #F1F1F1)
    subtle_bad = _make_checkerboard_image(grey=241, post_matte=False)
    chk1 = detect_baked_checkerboard(subtle_bad, "codex_subtle.png")
    assert chk1.status == "fail"
    assert chk1.details["defect_code"] == "baked_checkerboard"

    # 2. Post-matting checkerboard residue (alpha=0 alternating with #CCCCCC grey squares)
    post_matte_bad = _make_checkerboard_image(grey=204, post_matte=True)
    chk2 = detect_baked_checkerboard(post_matte_bad, "post_matte.png")
    assert chk2.status == "fail"

    # 3. Clean transparent portrait cutout -> PASS
    clean_trans = FakeStickerProvider()._create_character_frame(0, (512, 512))
    assert detect_baked_checkerboard(clean_trans, "clean_trans.png").status == "pass"

    # 4. Clean solid pure white studio backdrop -> PASS
    solid_white = Image.new("RGBA", (512, 512), (255, 255, 255, 255))
    solid_white.paste(clean_trans, (0, 0), clean_trans)
    assert detect_baked_checkerboard(solid_white, "solid_white.png").status == "pass"


def test_geometry_catches_floating_island_vertical_stretch_and_tiny_subject():
    # Floating severed hand / artifact island on raw cutout
    floating = FakeStickerProvider()._create_character_frame(0, (512, 512))
    d = ImageDraw.Draw(floating)
    d.ellipse([28, 36, 92, 98], fill=(245, 212, 196, 255))  # detached floating hand in top-left corner
    checks, metrics = analyze_cutout_geometry(floating, "floating.png", is_duo=False, is_raw=True, strict=True)
    codes = [c.details.get("defect_code") for c in checks if c.status == "fail"]
    assert "floating_island" in codes
    assert metrics["suspicious_islands"] >= 1

    # Abnormally tall/narrow stretched figure (H/W > 2.12)
    stretched = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    ImageDraw.Draw(stretched).ellipse([206, 20, 306, 490], fill=(240, 200, 185, 255))
    s_checks, _ = analyze_cutout_geometry(stretched, "stretched.png", is_duo=False, is_raw=True, strict=True)
    s_codes = [c.details.get("defect_code") for c in s_checks if c.status == "fail"]
    assert "stretched_or_warped_face" in s_codes

    # Tiny distant full-body figure
    tiny = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    ImageDraw.Draw(tiny).ellipse([236, 220, 276, 290], fill=(240, 200, 185, 255))
    t_checks, _ = analyze_cutout_geometry(tiny, "tiny.png", is_duo=False, is_raw=True, strict=True)
    t_codes = [c.details.get("defect_code") for c in t_checks if c.status == "fail"]
    assert "tiny_subject" in t_codes


def test_sprite_sheet_audit_catches_empty_and_mismatched_quadrants():
    fp = FakeStickerProvider()
    good_sheet = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    for (qx, qy), off in zip([(0, 0), (512, 0), (0, 512), (512, 512)], [0, 1, 2, 3]):
        cell = fp._create_character_frame(off, (512, 512))
        good_sheet.paste(cell, (qx, qy), cell)
    g_checks, _ = audit_sprite_sheet_image(good_sheet, "good_sheet.png", strict=True)
    assert all(c.status == "pass" for c in g_checks)

    # Corrupt BR quadrant to be empty
    bad_sheet = good_sheet.copy()
    ImageDraw.Draw(bad_sheet).rectangle([512, 512, 1024, 1024], fill=(0, 0, 0, 0))
    b_checks, _ = audit_sprite_sheet_image(bad_sheet, "bad_sheet.png", strict=True)
    assert any(c.status == "fail" and c.details.get("defect_code") == "sprite_quadrant_mismatch" for c in b_checks)


def test_vlm_anatomy_verifier_parses_third_hand_and_stretched_face(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key")
    img = FakeStickerProvider()._create_character_frame(0, (512, 512))

    fake_resp = MagicMock()
    fake_resp.raise_for_status.return_value = None
    fake_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "passed": False,
                            "person_count": 2,
                            "arms_per_person": [3, 2],
                            "same_shoulder_dual_arm": True,
                            "face_vertically_stretched": True,
                            "cartoon_eyes_or_2d": False,
                            "baked_checkerboard": False,
                            "defect_codes": [],
                            "reason": "Left girl has hanging blue sleeve plus second bare arm raised to head, and midface is elongated.",
                        }
                    )
                }
            }
        ]
    }
    with patch("sticker_maker.quality.anatomy.requests.post", return_value=fake_resp):
        chk = verify_anatomy_with_vlm(img, is_duo=True, target_label="d03_raw.png")
    assert chk is not None
    assert chk.status == "fail"
    assert "third_hand_or_extra_limb" in chk.details["defect_codes"]
    assert "stretched_or_warped_face" in chk.details["defect_codes"]


class _FlakyCheckerboardThenCleanProvider(FakeStickerProvider):
    """Returns a baked-checkerboard raw image on Attempt 1, then a clean cutout once corrective retry is injected."""

    def __init__(self) -> None:
        super().__init__(can_native_gif=False)
        self.prompts_seen: list[str] = []

    def render_static(self, reference_paths: list[Path], prompt: str, output: Path) -> Path:
        self.prompts_seen.append(prompt)
        output.parent.mkdir(parents=True, exist_ok=True)
        if "2x2 ANIMATION SPRITE SHEET" not in prompt and "[CRITICAL RETRY CORRECTION" not in prompt:
            bad = _make_checkerboard_image(grey=240, post_matte=False)
            bad.save(output, format="PNG")
            return output
        return super().render_static(reference_paths, prompt, output)


def test_orchestrator_auto_retries_failed_raw_and_cli_audit(tmp_path: Path):
    src = tmp_path / "person.png"
    FakeStickerProvider()._create_character_frame(0, (512, 512)).save(src)
    out_dir = tmp_path / "pack_out"

    job = JobConfig(
        job_id="strict_retry_job",
        source_image=str(src),
        output_dir=str(out_dir),
        mode="static",
        count=8,
        platforms=["telegram"],
        strict_qa=True,
        qa_max_retries=2,
    )
    job_path = out_dir / "job.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    job_path.write_text(json.dumps(job.model_dump(), indent=2), encoding="utf-8")

    flaky = _FlakyCheckerboardThenCleanProvider()
    orch = StickerOrchestrator(job=job, provider=flaky, native_gif_provider=flaky, max_parallel=1)
    manifest = orch.run(sample_only=True)

    assert manifest.state == "SAMPLE_COMPLETED"
    # 2 sample items -> each failed attempt 1 (baked_checkerboard) and succeeded on attempt 2 with corrective prompt
    assert len(flaky.prompts_seen) == 4
    assert any("REJECTED FOR BAKED-IN CHECKERBOARD" in p for p in flaky.prompts_seen)

    strict_sheet = out_dir / "qa" / "strict-audit-sheet.jpg"
    strict_json = out_dir / "qa" / "strict-audit.json"
    assert strict_sheet.exists()
    assert strict_json.exists()
    audit_data = json.loads(strict_json.read_text(encoding="utf-8"))
    assert audit_data["overall_status"] == "pass"

    # Verify CLI `audit` passes on cleaned pack directory and fails (exit code 5) on a defective checkerboard image
    ok_proc = subprocess.run(
        [sys.executable, "-m", "sticker_maker.cli", "audit", "-o", str(out_dir), "--strict"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert ok_proc.returncode == 0, ok_proc.stderr

    bad_img_path = tmp_path / "bad_codex.png"
    _make_checkerboard_image(grey=241).save(bad_img_path)
    bad_proc = subprocess.run(
        [sys.executable, "-m", "sticker_maker.cli", "audit", "-i", str(bad_img_path), "--duo"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert bad_proc.returncode == 5
    assert "baked_checkerboard" in bad_proc.stdout
    assert (tmp_path / "bad_codex_strict_audit.jpg").exists()
