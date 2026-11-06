import json
import shutil
from pathlib import Path

import pytest
from PIL import Image

from scripts.make_test_fixture import create_sample_photo
from sticker_maker.i18n import BUILTIN_CAPTION_LANGUAGES, normalize_language, resolve_localized_text
from sticker_maker.orchestrator import StickerOrchestrator
from sticker_maker.planner import (
    CATEGORY_LABELS,
    load_all_presets,
    load_motion_library,
    plan_expressions,
    resolve_text_spec,
    translation_template,
)
from sticker_maker.platforms import load_platform_profiles, resolve_platforms
from sticker_maker.processing.bubbles import BUBBLE_SHAPES
from sticker_maker.processing.compose import compose_sticker_frames
from sticker_maker.processing.encoders import save_animated
from sticker_maker.processing.typography import add_caption_to_image, wrap_text
from sticker_maker.providers.fake import FakeStickerProvider
from sticker_maker.schemas import AnimationConfig, JobConfig, TextSpec


def _char_frame(offset: int = 0, size: int = 512) -> Image.Image:
    fake = FakeStickerProvider()
    img = fake._create_character_frame(offset, (size, size), "real-cutout")
    bg = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    bg.alpha_composite(img)
    return bg


# ---------------------------------------------------------------- catalog


def test_expression_catalog_covers_categories_languages_and_motions():
    items = load_all_presets()
    assert len(items) >= 110
    cats = {}
    for it in items:
        cats.setdefault(it.category, 0)
        cats[it.category] += 1
        for lang in BUILTIN_CAPTION_LANGUAGES:
            assert it.captions.get(lang), f"{it.id} missing {lang}"
        assert len(it.motion.keyframe_poses) == 4
        if it.text_layout in ("bubble", "both"):
            assert it.bubble is not None and it.bubble.shape in BUBBLE_SHAPES
    assert set(cats) == set(CATEGORY_LABELS)
    assert all(n >= 7 for n in cats.values())
    library = load_motion_library()
    assert len(library) >= 60
    assert {it.motion.type for it in items} <= set(library)
    layouts = {it.text_layout for it in items}
    assert {"caption", "bubble", "both", "none"} <= layouts


def test_plan_by_categories_and_explicit_ids():
    plan = plan_expressions(count=12, categories=["meme", "work"], strict_counts=False)
    assert len(plan) == 12
    assert {p.category for p in plan} == {"meme", "work"}

    picked = plan_expressions(count=8, expression_ids=["41_table_flip", "01_hello"])
    assert [p.id for p in picked[:2]] == ["41_table_flip", "01_hello"]
    assert len(picked) == 8

    with pytest.raises(ValueError):
        plan_expressions(count=12)  # WeChat strict counts
    with pytest.raises(ValueError):
        plan_expressions(count=8, categories=["not-a-category"])


def test_job_count_rules_depend_on_platforms():
    JobConfig(job_id="t", source_image="a.png", output_dir="o", count=10, platforms=["telegram"])
    with pytest.raises(ValueError):
        JobConfig(job_id="t", source_image="a.png", output_dir="o", count=10, platforms=["wechat", "telegram"])


# ---------------------------------------------------------------- languages & text


def test_language_normalization_and_fallback():
    assert normalize_language("zh_hans") == "zh-CN"
    assert normalize_language("zh-HK") == "zh-TW"
    assert normalize_language("ko_KR") == "ko"
    assert normalize_language("ja-JP") == "ja"
    text, exact = resolve_localized_text({"en": "Hi", "zh-CN": "你好"}, "es")
    assert text == "Hi" and exact is False


def test_resolve_text_spec_caption_bubble_both_and_custom(tmp_path: Path):
    items = {i.id: i for i in load_all_presets()}
    job = JobConfig(job_id="t", source_image="a.png", output_dir=str(tmp_path), language="ko")

    hello = items["01_hello"]
    spec = resolve_text_spec(hello, job)
    assert spec.language == "ko"
    shown = spec.caption or spec.bubble_text
    assert shown == hello.captions["ko"]  # exactly one language, no "안녕! Hi there!" mixing
    assert hello.captions["en"] not in shown

    both_item = next(i for i in items.values() if i.text_layout == "both")
    spec_both = resolve_text_spec(both_item, job)
    assert spec_both.layout == "both"
    assert spec_both.bubble_text == both_item.bubble.texts["ko"]
    assert spec_both.caption == both_item.captions["ko"]

    # Forced global layout
    job_bubble = JobConfig(job_id="t", source_image="a.png", output_dir=str(tmp_path), language="en", text_layout="bubble")
    assert resolve_text_spec(items["04_laugh"], job_bubble).bubble_text == items["04_laugh"].captions["en"]

    # Any language through a captions file
    cap_file = tmp_path / "captions_es.json"
    cap_file.write_text(json.dumps({"01_hello": {"es": "¡Hola!"}}, ensure_ascii=False), encoding="utf-8")
    job_es = JobConfig(job_id="t", source_image="a.png", output_dir=str(tmp_path), language="es", captions_file=str(cap_file))
    from sticker_maker.i18n import load_captions_file

    custom = load_captions_file(str(cap_file))
    spec_es = resolve_text_spec(hello, job_es, custom)
    assert "¡Hola!" in (spec_es.caption or spec_es.bubble_text)
    assert spec_es.needs_translation is False
    spec_missing = resolve_text_spec(items["04_laugh"], job_es, custom)
    assert spec_missing.needs_translation is True

    tpl = translation_template([hello], "es")
    assert "_source" in tpl["01_hello"] and "es" in tpl["01_hello"]["caption"]


@pytest.mark.parametrize(
    "lang,text",
    [("zh-CN", "你好呀"), ("zh-TW", "謝謝老闆"), ("en", "See you tomorrow!"), ("ja", "了解です！"), ("ko", "고마워요 정말"), ("th", "สวัสดีครับ"), ("ru", "Привет!")],
)
def test_multilingual_caption_renders_inside_canvas(lang, text):
    out = add_caption_to_image(Image.new("RGBA", (240, 240), (0, 0, 0, 0)), text, language=lang)
    bbox = out.getchannel("A").getbbox()
    assert bbox is not None
    assert bbox[0] >= 0 and bbox[2] <= 240 and bbox[3] > 170


def test_wrapping_rules_words_and_kinsoku():
    lines = wrap_text("See you tomorrow my friend", "en", 26, 150)
    assert len(lines) >= 2
    words = {"See", "you", "tomorrow", "my", "friend"}
    for line in lines:
        assert all(w in words for w in line.split())
    ja = wrap_text("今日もよろしくお願いします！", "ja", 26, 110)
    assert len(ja) >= 2
    assert not any(l.startswith(("！", "。", "、")) for l in ja)


# ---------------------------------------------------------------- bubbles


@pytest.mark.parametrize("shape", BUBBLE_SHAPES)
def test_every_bubble_shape_renders_in_upper_corner(shape):
    spec = TextSpec(language="en", layout="bubble", bubble_text="Hello there!", bubble_shape=shape, bubble_position="top-left")
    frame = compose_sticker_frames([_char_frame()], spec, "real-cutout", (480, 480), 1)[0]
    corner = frame.crop((0, 0, 240, 150)).getchannel("A")
    assert corner.getbbox() is not None
    # caption area at the bottom stays free of caption text in pure-bubble layout
    plain = compose_sticker_frames([_char_frame()], TextSpec(layout="none"), "real-cutout", (480, 480), 1)[0]
    assert frame.tobytes() != plain.tobytes()


def test_bubble_auto_side_opposes_raised_hand_and_pop_animation():
    spec = TextSpec(language="zh-CN", layout="both", caption="收到", bubble_text="好的老板！", bubble_shape="shout", bubble_animation="pop")
    frames = compose_sticker_frames([_char_frame(i) for i in range(4)], spec, "real-cutout", (480, 480), 8)
    assert len(frames) == 8
    # fake character raises its hand on the right → bubble placed on the left
    left = frames[3].crop((0, 0, 200, 140)).getchannel("A").getbbox()
    assert left is not None
    assert frames[0].tobytes() != frames[3].tobytes()


# ---------------------------------------------------------------- platforms


def test_platform_profiles_aliases_and_groups():
    profiles = load_platform_profiles()
    assert len(profiles) >= 20
    for required in ("wechat", "qq", "douyin", "xiaohongshu", "soul", "weibo", "telegram", "whatsapp", "line",
                     "kakaotalk", "discord", "slack", "imessage", "signal", "giphy", "instagram", "tiktok", "x"):
        assert required in profiles
    assert resolve_platforms("ins,小红书,tg,kakao") == ["instagram", "xiaohongshu", "telegram", "kakaotalk"]
    assert "wechat" in resolve_platforms(["china"])
    assert len(resolve_platforms(["all"])) == len(profiles)
    with pytest.raises(ValueError):
        resolve_platforms(["myspace"])


def test_encoders_respect_byte_budgets(tmp_path: Path):
    frames = [_char_frame(i, 512) for i in range(8)]
    for fmt, budget in (("webp", 500_000), ("apng", 300_000), ("gif", 500_000)):
        p = tmp_path / f"a.{fmt}"
        save_animated(frames, p, fmt, 150, budget, loop=0)
        assert p.exists() and p.stat().st_size <= budget
        with Image.open(p) as im:
            assert getattr(im, "n_frames", 1) >= 2


def test_multi_platform_export_end_to_end(tmp_path: Path):
    src = tmp_path / "cat.png"
    create_sample_photo(src)
    out = tmp_path / "pack"
    job = JobConfig(
        job_id="multi",
        source_image=str(src),
        output_dir=str(out),
        count=8,
        language="en",
        style="real-cutout",
        master_size=480,
        platforms=["wechat", "whatsapp", "line", "telegram", "xiaohongshu", "instagram"],
        animation=AnimationConfig(backend="sprite-sheet", frames=8, frame_duration_ms=150),
    )
    fake = FakeStickerProvider(can_native_gif=False)
    manifest = StickerOrchestrator(job, provider=fake, native_gif_provider=fake, max_parallel=2).run()
    assert manifest.state == "COMPLETED"

    # WeChat keeps the classic layout
    for item in manifest.items:
        with Image.open(out / item.static_path) as im:
            assert im.size == (240, 240)
        assert "whatsapp" in item.exports and "line" in item.exports
    assert (out / "static-pack.zip").exists()

    wa = sorted((out / "exports" / "whatsapp" / "stickers" / "static").glob("*.webp"))
    assert len(wa) == 8
    for p in wa:
        assert p.stat().st_size <= 100_000
        with Image.open(p) as im:
            assert im.size == (512, 512)
    assert (out / "exports" / "whatsapp" / "assets" / "tray_icon.png").exists()

    line_anim = sorted((out / "exports" / "line" / "stickers" / "animated").glob("*.png"))
    assert len(line_anim) == 8
    with Image.open(line_anim[0]) as im:
        assert im.width <= 320 and im.height <= 270 and im.width % 2 == 0 and im.n_frames >= 5

    xhs = out / "exports" / "xiaohongshu" / "showcase"
    assert (xhs / "cover_01.jpg").exists() and (xhs / "grid_01.jpg").exists()
    with Image.open(xhs / "cover_01.jpg") as im:
        assert im.size == (1080, 1440)
    assert (out / "exports" / "instagram" / "showcase" / "story_01.jpg").exists()

    if shutil.which("ffmpeg"):
        assert len(list((out / "exports" / "telegram" / "stickers" / "animated").glob("*.webm"))) == 8
        assert (xhs / "video_01.mp4").exists()

    for pid in ("whatsapp", "line", "telegram", "xiaohongshu", "instagram"):
        report = json.loads((out / "exports" / pid / "qa-report.json").read_text(encoding="utf-8"))
        assert report["status"] in ("pass", "warn"), (pid, [c for c in report["checks"] if c["status"] == "fail"][:3])
        assert (out / "exports" / f"{pid}-pack.zip").exists()
        assert (out / "exports" / pid / "README.md").exists()

    # Re-export to a new platform from masters without regenerating images
    orch = StickerOrchestrator(job, provider=fake, native_gif_provider=fake)
    res = orch.export_only(["discord"])
    assert res["discord"].status in ("pass", "warn")
    assert (out / "exports" / "discord-pack.zip").exists()


def test_fit_text_shrinks_instead_of_breaking_words():
    from sticker_maker.processing.typography import fit_text

    layout = fit_text("Unbelievable", "en", max_width=110, max_height=80, start_size=30, min_size=8, max_lines=2)
    assert [l.text for l in layout.lines] == ["Unbelievable"]



def test_every_builtin_text_is_single_language():
    from sticker_maker.planner import language_issues, load_meme_templates

    items = load_all_presets() + load_meme_templates()
    for lang in BUILTIN_CAPTION_LANGUAGES:
        job = JobConfig(job_id="t", source_image="a", output_dir="o", language=lang, platforms=["generic"], count=1)
        assert language_issues(items, job) == [], lang


def test_foreign_text_detection():
    from sticker_maker.i18n import foreign_text_issue

    assert foreign_text_issue("你好\nHi there!", "zh-CN") is not None
    assert foreign_text_issue("안녕! Hi there!", "ko") is not None
    assert foreign_text_issue("Hello 你好", "en") is not None
    assert foreign_text_issue("こんにちは 안녕", "ja") is not None
    # normal slang acronyms are fine
    assert foreign_text_issue("检测到中国IP 禁止靠近", "zh-CN") is None
    assert foreign_text_issue("CPU干烧了", "zh-CN") is None
    assert foreign_text_issue("これ以上喋ったらBANな", "ja") is None
    assert foreign_text_issue("Hi there!", "en") is None


def test_pipeline_refuses_mixed_or_untranslated_language(tmp_path: Path):
    src = tmp_path / "cat.png"
    create_sample_photo(src)
    fake = FakeStickerProvider(can_native_gif=False)
    # Spanish without a captions file → would fall back to English → refuse before generating
    job = JobConfig(job_id="es", source_image=str(src), output_dir=str(tmp_path / "es"), count=8, language="es")
    with pytest.raises(ValueError, match="Single-language"):
        StickerOrchestrator(job, provider=fake, native_gif_provider=fake).run()
    # A custom caption that mixes languages is rejected too
    cap = tmp_path / "mixed.json"
    cap.write_text(json.dumps({"01_hello": {"zh-CN": "你好 Hello there"}}, ensure_ascii=False), encoding="utf-8")
    job2 = JobConfig(job_id="zh", source_image=str(src), output_dir=str(tmp_path / "zh"), count=8, captions_file=str(cap))
    with pytest.raises(ValueError, match="Single-language"):
        StickerOrchestrator(job2, provider=fake, native_gif_provider=fake).run()
