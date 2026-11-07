"""Tests for 108 Duo Interaction Presets (闺蜜 / 情侣 / 百合), Auto Style-Language Matching,
Multi-Language Single-Pass Pack Generation (--languages), and Local Preview HTML."""

from __future__ import annotations

from pathlib import Path
from PIL import Image
import pytest

from sticker_maker.duo import (
    DUO_CATEGORIES,
    build_duo_sprite_sheet_prompt,
    build_duo_static_prompt,
    list_duo_presets,
    load_duo_presets,
    normalize_duo_category,
    plan_duo_expressions,
)
from sticker_maker.orchestrator import StickerOrchestrator
from sticker_maker.planner import get_item_by_id, language_issues, plan_pack
from sticker_maker.providers.fake import FakeStickerProvider
from sticker_maker.schemas import CharacterBible, JobConfig
from sticker_maker.styles import infer_language_for_style


def _make_dummy_photo(path: Path, color=(220, 180, 170)) -> Path:
    img = Image.new("RGB", (512, 512), color)
    img.save(path, format="PNG")
    return path


def test_duo_catalog_168_presets_and_categories():
    all_duo = load_duo_presets()
    assert len(all_duo) == 168

    besties = list_duo_presets("闺蜜")
    couple = list_duo_presets("情侣")
    yuri = list_duo_presets("百合")
    yaoi = list_duo_presets("双男主")
    rivals = list_duo_presets("欢喜冤家")
    family = list_duo_presets("亲子")
    assert len(besties) == 36
    assert len(couple) == 36
    assert len(yuri) == 36
    assert len(yaoi) == 20
    assert len(rivals) == 20
    assert len(family) == 20

    assert normalize_duo_category("姐妹") == "besties"
    assert normalize_duo_category("对象") == "couple"
    assert normalize_duo_category("双女主") == "yuri"
    assert normalize_duo_category("gl") == "yuri"
    assert normalize_duo_category("bl") == "yaoi"
    assert normalize_duo_category("损友") == "rivals"
    assert normalize_duo_category("萌娃") == "family"

    # Verify all 168 duo presets have 5 single-language captions & bubbles (zh-CN, zh-TW, en, ko, ja)
    for lang in ("zh-CN", "zh-TW", "en", "ko", "ja"):
        dummy_job = JobConfig(
            job_id=f"duo-check-{lang}",
            source_image="a.png",
            output_dir="out",
            language=lang,
            pack_type="duo",
        )
        issues = language_issues(all_duo, dummy_job)
        assert not issues, f"Language issues in duo presets for {lang}: {issues}"


def test_expanded_catalogs_220_expressions_and_60_memes():
    from sticker_maker.planner import CATEGORY_LABELS, load_all_presets, load_meme_templates

    exprs = load_all_presets()
    memes = load_meme_templates()
    assert len(exprs) == 220
    assert len(CATEGORY_LABELS) == 22
    assert len(memes) == 60


def test_duo_planning_and_prompts():
    planned_yuri = plan_duo_expressions(count=8, categories=["百合"])
    assert len(planned_yuri) == 8
    assert all(it.category == "yuri" for it in planned_yuri)

    item = get_item_by_id("d73_yuri_chin_lift_gaze")
    assert item.category == "yuri"

    bible = CharacterBible(
        character_id="test_duo",
        source_sha256="0" * 64,
        reference_image="ref.png",
        subject_type="human-portrait",
        identity_facts=["young woman with long wavy dark hair"],
        locked_attributes=["face", "hair"],
        master_anchor="anchor.png",
    )
    sp = build_duo_static_prompt(bible, item, partner_facts=["cool tall woman in black blazer"], style="kr-gyaru-peace")
    assert "TWO-PERSON" in sp
    assert "Person A" in sp and "Person B" in sp
    assert "NEVER cartoonize" in sp

    sheet_p = build_duo_sprite_sheet_prompt(bible, item, partner_facts=["cool tall woman in black blazer"])
    assert "2x2 ANIMATION SPRITE SHEET" in sheet_p


def test_infer_language_for_style():
    assert infer_language_for_style("kr-idol-aegyo") == "ko"
    assert infer_language_for_style("jp-purikura-sweet") == "ja"
    assert infer_language_for_style("cn-hanfu-daily") == "zh-CN"
    assert infer_language_for_style("real-cutout") == "en"


def test_duo_and_multilang_orchestrator_end_to_end(tmp_path: Path):
    p1 = _make_dummy_photo(tmp_path / "person_a.png", (230, 190, 180))
    p2 = _make_dummy_photo(tmp_path / "person_b.png", (200, 175, 195))
    out_dir = tmp_path / "duo_out"

    job = JobConfig(
        job_id="duo_yuri_pack",
        source_image=str(p1),
        partner_image=str(p2),
        partner_facts=["long black hair, gentle smile"],
        output_dir=str(out_dir),
        mode="static",
        count=8,
        style="kr-gyaru-peace",
        language="ko",
        languages=["zh-CN", "en", "ja"],
        pack_type="duo",
        duo_categories=["yuri"],
        platforms=["wechat"],
        allow_cloud_upload=False,
    )
    planned = plan_pack(job, strict_counts=True)
    assert len(planned) == 8
    assert all(x.category == "yuri" for x in planned)

    orch = StickerOrchestrator(job=job, provider=FakeStickerProvider(), native_gif_provider=FakeStickerProvider())
    manifest = orch.run(sample_only=True)
    assert manifest.state == "SAMPLE_COMPLETED"
    assert (out_dir / "preview.html").exists()

    # Check extra single-language packs were generated from the same raw cutouts
    for extra_lang in ("zh-CN", "en", "ja"):
        pack_dir = out_dir / "packs" / extra_lang
        assert pack_dir.exists()
        assert (pack_dir / "preview.html").exists()
        assert len(list((pack_dir / "static").glob("*.png"))) == 2

    # Test 0-Token Remix Captions & Social Poster Generator
    import json
    from sticker_maker.studio import generate_social_posters, list_theme_presets, remix_captions, resolve_theme_preset

    assert len(list_theme_presets()) == 15
    assert resolve_theme_preset("电竞")["style"] == "real-cyber-neon"
    assert resolve_theme_preset("双男主")["pack_type"] == "duo"

    job_file = out_dir / "job.json"
    job_file.write_text(json.dumps(job.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")

    first_id = planned[0].id
    preview_html = remix_captions(
        job_file,
        caption_overrides={first_id: "自定义新台词!"},
        bubble_overrides={first_id: "只贴贴你"},
        language="zh-CN",
    )
    assert preview_html.exists()

    poster_res = generate_social_posters(out_dir, title="百合双女主贴贴包", subtitle="真人实拍 · 168套双人互动")
    assert poster_res["xhs_3x4"].exists()
    assert poster_res["story_9x16"].exists()
    assert poster_res["grid_1x1"].exists()
    assert poster_res["submission_copy"].exists()
