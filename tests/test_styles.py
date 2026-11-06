import json
from pathlib import Path

import pytest
from PIL import Image

from sticker_maker.analyzer import create_or_load_character_bible
from sticker_maker.orchestrator import StickerOrchestrator
from sticker_maker.processing.alpha import apply_die_cut_border
from sticker_maker.processing.resize import create_banner
from sticker_maker.prompts import build_anchor_prompt, build_sprite_sheet_prompt, build_static_prompt
from sticker_maker.providers.fake import FakeStickerProvider
from sticker_maker.schemas import AnimationConfig, JobConfig
from sticker_maker.styles import STYLE_REGIONS, hex_to_rgba, list_style_presets, normalize_region, resolve_style_preset
from scripts.make_test_fixture import create_sample_photo


def test_builtin_style_presets_catalog_real_person_only():
    presets = list_style_presets()
    assert len(presets) >= 26
    core_ids = {
        "real-cutout",
        "real-variety-meme",
        "real-bobblehead",
        "real-purikura",
        "real-street-cool",
        "real-vintage-ccd",
        "real-work-emo",
        "real-high-contrast",
    }
    actual_ids = {p.id for p in presets}
    assert core_ids <= actual_ids
    assert len(actual_ids) == len(presets)

    for p in presets:
        assert p.id.startswith("real-")
        assert p.category == "真人专属"
        assert p.region in STYLE_REGIONS
        assert p.display_name
        assert "exact same" in p.prompt_lock and "reference photo" in p.prompt_lock
        assert "NEVER" in p.negative_extra
        assert len(p.default_palette) >= 2
        assert hex_to_rgba(p.typography.text_color)[3] == 255
        assert hex_to_rgba(p.typography.stroke_color)[3] == 255
        assert p.prefer_keyframes is True
        assert p.die_cut_border_px >= 4
        assert p.caption_animation == "none"


def test_korean_japanese_chinese_style_series():
    for region, aliases in (("韩系", ["韩系", "kr", "korean"]), ("日系", ["日系", "jp", "日本"]), ("中式", ["中式", "cn", "国风", "中系"])):
        assert normalize_region(aliases[0]) == region
        for alias in aliases:
            group = list_style_presets(region=alias)
            assert len(group) >= 6, (region, alias)
            assert all(p.region == region for p in group)
    assert {p.id for p in list_style_presets(region="kr")} >= {"real-kr-idol-selfie", "real-kr-drama", "real-purikura"}
    assert {p.id for p in list_style_presets(region="jp")} >= {"real-jp-airy", "real-jp-fuji-film", "real-jp-purikura"}
    assert {p.id for p in list_style_presets(region="cn")} >= {"real-cn-hk-retro", "real-cn-new-chinese", "real-variety-meme"}
    both = list_style_presets(region="kr,jp")
    assert {p.region for p in both} == {"韩系", "日系"}
    with pytest.raises(ValueError):
        list_style_presets(region="mars")


@pytest.mark.parametrize("style_id", [p.id for p in list_style_presets()])
def test_every_style_prompt_keeps_real_person_lock(style_id, tmp_path: Path):
    from sticker_maker.planner import load_all_presets
    from sticker_maker.schemas import CharacterBible

    bible = CharacterBible(character_id="c", source_sha256="x", master_anchor="a.png", reference_image="r.png")
    item = load_all_presets()[0]
    prompt = build_static_prompt(bible, item, style=style_id)
    assert f"Style ID: {style_id}" in prompt
    assert "CRITICAL REAL-PERSON RULE" in prompt
    sheet = build_sprite_sheet_prompt(bible, item, style=style_id)
    assert "2x2 ANIMATION SPRITE SHEET" in sheet and "NEVER" in sheet
    out = tmp_path / "a.png"
    FakeStickerProvider().render_anchor([], prompt, out)
    assert out.exists()


def test_default_style_is_real_cutout_and_human_portrait(tmp_path: Path):
    source_img = tmp_path / "portrait.png"
    create_sample_photo(source_img)

    job = JobConfig(
        job_id="default-real-person",
        source_image=str(source_img),
        output_dir=str(tmp_path / "out"),
    )
    assert job.style == "real-cutout"
    assert job.subject_type == "human-portrait"

    bible = create_or_load_character_bible(source_img, tmp_path / "out")
    assert bible.subject_type == "human-portrait"
    assert bible.render_style.style_id == "real-cutout"
    assert bible.render_style.outline == "die-cut-white-border"

    anchor_prompt = build_anchor_prompt(bible.subject_type, bible.identity_facts)
    assert "Style ID: real-cutout" in anchor_prompt
    assert "CRITICAL REAL-PERSON RULE" in anchor_prompt
    assert "NEVER cartoonize" in anchor_prompt


def test_custom_json_style_and_fallback(tmp_path: Path):
    custom_json = tmp_path / "custom_real_film.json"
    custom_data = {
        "id": "real-film-noir",
        "display_name": "真人电影感写真",
        "category": "真人专属",
        "description": "电影级人像质感与白边",
        "prompt_lock": "Photorealistic cinematic portrait sticker cutout of the exact same real person.",
        "negative_extra": "NEVER cartoonize.",
        "outline": "die-cut-white-border",
        "lighting": "cinematic-portrait",
        "default_palette": ["#2E1A47", "#D8BFD8", "#111111"],
        "banner_bg": "#1F162B",
        "die_cut_border_px": 4,
        "prefer_keyframes": True,
        "typography": {
            "text_color": "#2E1A47",
            "stroke_color": "#F5E6FF",
            "stroke_width": 4,
            "start_font_size": 26,
        },
    }
    custom_json.write_text(json.dumps(custom_data, ensure_ascii=False), encoding="utf-8")

    loaded = resolve_style_preset(str(custom_json))
    assert loaded.id == "real-film-noir"
    assert loaded.display_name == "真人电影感写真"
    assert loaded.outline == "die-cut-white-border"
    assert loaded.typography.stroke_width == 4

    # Free-form fallback still enforces real-person cutout rules
    fallback = resolve_style_preset("real-magazine-cover")
    assert fallback.id == "real-magazine-cover"
    assert fallback.category == "真人专属"
    assert fallback.prefer_keyframes is True
    assert fallback.die_cut_border_px == 4
    assert "Photorealistic real-person portrait sticker cutout" in fallback.prompt_lock


def test_different_real_styles_produce_distinct_visuals_and_metadata(tmp_path: Path):
    source_img = tmp_path / "portrait.png"
    create_sample_photo(source_img)

    fake = FakeStickerProvider(can_native_gif=False)

    out_cutout = tmp_path / "anchor_cutout.png"
    out_bobble = tmp_path / "anchor_bobble.png"
    out_mono = tmp_path / "anchor_mono.png"

    fake.render_anchor([source_img], "Style ID: real-cutout", out_cutout)
    fake.render_anchor([source_img], "Style ID: real-bobblehead", out_bobble)
    fake.render_anchor([source_img], "Style ID: real-high-contrast", out_mono)

    assert out_cutout.read_bytes() != out_bobble.read_bytes()
    assert out_cutout.read_bytes() != out_mono.read_bytes()

    with Image.open(out_cutout) as cimg:
        b_variety = create_banner(cimg, style="real-variety-meme")
        b_ccd = create_banner(cimg, style="real-vintage-ccd")
        assert b_variety.getpixel((300, 10)) != b_ccd.getpixel((300, 10))

    pack_dir = tmp_path / "variety_pack"
    job = JobConfig(
        job_id="variety-portrait",
        source_image=str(source_img),
        output_dir=str(pack_dir),
        mode="both",
        count=8,
        style="real-variety-meme",
        animation=AnimationConfig(backend="keyframes", frames=6),
    )
    orch = StickerOrchestrator(job=job, provider=fake, native_gif_provider=fake)
    manifest = orch.run(sample_only=True)
    assert manifest.state == "SAMPLE_COMPLETED"

    bible = create_or_load_character_bible(source_img, pack_dir, style="real-variety-meme")
    assert bible.render_style.style_id == "real-variety-meme"
    assert bible.render_style.outline == "die-cut-white-border"
    assert bible.render_style.lighting == "high-key-tv"


def test_real_person_styles_die_cut_border_and_keyframe_gif(tmp_path: Path):
    source_img = tmp_path / "portrait.png"
    create_sample_photo(source_img)

    dot = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    for x in range(45, 55):
        for y in range(45, 55):
            dot.putpixel((x, y), (200, 50, 50, 255))
    bordered = apply_die_cut_border(dot, border_px=4)
    r, g, b, a = bordered.getpixel((42, 50))
    assert (r, g, b) == (255, 255, 255)
    assert a > 200

    fake = FakeStickerProvider(can_native_gif=True)
    real_dir = tmp_path / "real_bobble_pack"
    job = JobConfig(
        job_id="real-bobble-test",
        source_image=str(source_img),
        output_dir=str(real_dir),
        mode="both",
        count=8,
        style="real-bobblehead",
        subject_type="human-portrait",
        animation=AnimationConfig(backend="auto", frames=8, frame_duration_ms=160),
    )
    orch = StickerOrchestrator(job=job, provider=fake, native_gif_provider=fake)
    manifest = orch.run(sample_only=True)
    assert manifest.state == "SAMPLE_COMPLETED"
    assert manifest.generated_count["static"] == 2
    assert manifest.generated_count["animated"] == 1
    assert not list((real_dir / "work" / "raw_gif").glob("*.gif"))
    assert (real_dir / "animated" / "01_hello.gif").exists()
