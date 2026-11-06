import json
from pathlib import Path

import pytest
from PIL import Image

from scripts.make_test_fixture import create_sample_photo
from sticker_maker.memes import MEME_ALIASES, make_meme, resolve_meme_id
from sticker_maker.orchestrator import StickerOrchestrator
from sticker_maker.planner import (
    MEME_CATEGORY_LABELS,
    load_meme_templates,
    localize_meme,
    plan_pack,
    resolve_text_spec,
)
from sticker_maker.processing.compose import compose_sticker_frames
from sticker_maker.processing.meme_fx import _RENDERERS, apply_filter, render_element
from sticker_maker.prompts import build_sprite_sheet_prompt, build_static_prompt
from sticker_maker.providers.fake import FakeStickerProvider
from sticker_maker.schemas import AnimationConfig, JobConfig, MemeElement, MemeSpec, TextSpec


def _char(offset: int = 0) -> Image.Image:
    img = FakeStickerProvider()._create_character_frame(offset, (512, 512), "real-cutout")
    bg = Image.new("RGBA", (512, 512), (255, 255, 255, 255))
    bg.alpha_composite(img)
    return bg


def test_meme_catalog_is_valid_and_covers_core_templates():
    memes = load_meme_templates()
    assert len(memes) >= 32
    ids = {m.id for m in memes}
    assert {"m01_ai_thinking", "m02_china_ip_blocked", "m03_ban_threat"} <= ids
    assert {m.category for m in memes} <= set(MEME_CATEGORY_LABELS)
    for m in memes:
        assert m.meme is not None
        for lang in ("zh-CN", "zh-TW", "en", "ja", "ko"):
            assert m.captions.get(lang)
    used = {el.type for m in memes for el in m.meme.elements}
    assert len(used) >= 18
    for alias, tid in MEME_ALIASES.items():
        assert tid in ids, alias


def test_meme_alias_resolution():
    assert resolve_meme_id("claude") == "m01_ai_thinking"
    assert resolve_meme_id("中国IP") == "m02_china_ip_blocked"
    assert resolve_meme_id("再说话封你号") == "m03_ban_threat"
    assert resolve_meme_id("m14") == "m14_shock_deepfried"
    with pytest.raises(ValueError):
        resolve_meme_id("not-a-meme")


@pytest.mark.parametrize("etype", sorted(_RENDERERS))
def test_every_meme_element_renders(etype):
    el = MemeElement(type=etype, text={"zh-CN": "测试文字", "en": "Test"}, title={"zh-CN": "提示"}, button={"zh-CN": "确定"}, value=42,
                     position="head" if etype == "spinner" else "top", animate="none")
    layer = render_element(el, (480, 480), (240, 120), (120, 100, 360, 470), "zh-CN")
    assert layer.size == (480, 480)
    assert layer.getchannel("A").getbbox() is not None


@pytest.mark.parametrize("name", ["deep_fry", "glitch", "patina", "grayscale", "hue_cycle", "vignette", "high_contrast", "posterize"])
def test_meme_filters_keep_alpha(name):
    frame = compose_sticker_frames([_char()], TextSpec(layout="none"), "real-cutout", (360, 360), 1)[0]
    out = apply_filter(frame, name, 1, 8)
    assert out.mode == "RGBA" and out.size == frame.size
    assert out.getchannel("A").getextrema()[0] == 0  # transparent background preserved


def test_ai_thinking_meme_animates_spinner_and_dots():
    item = next(m for m in load_meme_templates() if m.id == "m01_ai_thinking")
    job = JobConfig(job_id="t", source_image="a", output_dir="o", language="zh-CN", platforms=["generic"], count=1)
    spec = resolve_text_spec(item, job)
    assert spec.has_bubble and spec.bubble_shape == "thought" and spec.bubble_animation == "dots"
    frames = compose_sticker_frames([_char()], spec, "real-cutout", (360, 360), 8, meme=localize_meme(item, job))
    assert len(frames) == 8
    assert frames[0].tobytes() != frames[1].tobytes()  # spinner rotation / dots change


def test_meme_text_override_and_language():
    item = next(m for m in load_meme_templates() if m.id == "m03_ban_threat")
    job = JobConfig(job_id="t", source_image="a", output_dir="o", language="ko", platforms=["generic"], count=1,
                    meme_texts={"m03_ban_threat": "한 번만 더!"})
    meme = localize_meme(item, job)
    first_text_el = next(el for el in meme.elements if el.text)
    assert first_text_el.text == {"ko": "한 번만 더!"}
    assert item.meme.elements[0].text != first_text_el.text  # original template untouched


def test_meme_prompts_never_ask_model_for_text():
    item = next(m for m in load_meme_templates() if m.id == "m02_china_ip_blocked")
    from sticker_maker.schemas import CharacterBible

    bible = CharacterBible(character_id="c", source_sha256="x", master_anchor="a.png", reference_image="r.png")
    for prompt in (build_static_prompt(bible, item), build_sprite_sheet_prompt(bible, item)):
        assert "[MEME LOOK]" in prompt
        assert "Do not draw any text" in prompt


def test_make_meme_from_single_image_and_sheet(tmp_path: Path):
    img = tmp_path / "char.png"
    _char().save(img)
    outs = make_meme("claude", images=[img], gif_output=tmp_path / "a.gif", png_output=tmp_path / "a.png", size=240)
    assert outs["png"].exists() and outs["gif"].exists()
    with Image.open(outs["gif"]) as g:
        assert g.size == (240, 240) and g.n_frames == 8

    sheet = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
    for k, (x, y) in enumerate(((0, 0), (512, 0), (0, 512), (512, 512))):
        sheet.paste(_char(k), (x, y))
    sp = tmp_path / "sheet.png"
    sheet.save(sp)
    outs2 = make_meme("封号", sprite_sheet=sp, gif_output=tmp_path / "b.gif", png_output=tmp_path / "b.png", language="en", text="One more word", size=360)
    with Image.open(outs2["gif"]) as g:
        assert g.size == (360, 360) and g.n_frames == 8


def test_plan_pack_memes_and_mixed():
    job = JobConfig(job_id="t", source_image="a", output_dir="o", count=8, pack_type="memes", meme_categories=["ban-warning"])
    plan = plan_pack(job)
    assert len(plan) == 8 and all(p.meme is not None for p in plan)
    assert plan[0].category == "ban-warning"
    mixed = plan_pack(JobConfig(job_id="t", source_image="a", output_dir="o", count=16, pack_type="mixed", meme_templates=["m01_ai_thinking", "m03_ban_threat"]))
    assert len(mixed) == 16
    assert sum(1 for p in mixed if p.meme is not None) == 2


def test_meme_pack_end_to_end(tmp_path: Path):
    src = tmp_path / "cat.png"
    create_sample_photo(src)
    out = tmp_path / "memepack"
    job = JobConfig(
        job_id="memes", source_image=str(src), output_dir=str(out), count=8, pack_type="memes",
        language="zh-CN", master_size=480, platforms=["wechat", "telegram"],
        animation=AnimationConfig(backend="sprite-sheet", frames=8),
    )
    fake = FakeStickerProvider(can_native_gif=False)
    manifest = StickerOrchestrator(job, provider=fake, native_gif_provider=fake, max_parallel=2).run()
    assert manifest.state == "COMPLETED"
    assert all(i.id.startswith("m") for i in manifest.items)
    for item in manifest.items:
        with Image.open(out / item.animated_path) as g:
            assert g.size == (240, 240) and g.n_frames >= 2
    report = json.loads((out / "exports" / "telegram" / "qa-report.json").read_text(encoding="utf-8"))
    assert report["status"] in ("pass", "warn")
