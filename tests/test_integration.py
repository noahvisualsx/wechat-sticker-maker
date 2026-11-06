from pathlib import Path
import pytest
from PIL import Image, ImageDraw

from sticker_maker.analyzer import extract_dominant_palette, normalize_source_image
from sticker_maker.config import get_default_font_path
from sticker_maker.orchestrator import StickerOrchestrator
from sticker_maker.processing.alpha import remove_matte_background
from sticker_maker.providers.fake import FakeStickerProvider
from sticker_maker.providers.openai_images import OpenAIImagesProvider
from sticker_maker.schemas import AnimationConfig, JobConfig
from scripts.make_test_fixture import create_sample_photo


def test_full_pipeline_with_fake_provider(tmp_path: Path):
    source_img = tmp_path / "cat.png"
    create_sample_photo(source_img)

    out_dir = tmp_path / "out_pack"
    job = JobConfig(
        job_id="test-cat-pack",
        source_image=str(source_img),
        output_dir=str(out_dir),
        mode="both",
        count=8,
        animation=AnimationConfig(backend="auto", frames=8, frame_duration_ms=180),
        font_path=get_default_font_path(),
    )

    fake = FakeStickerProvider(can_native_gif=True)
    orchestrator = StickerOrchestrator(job=job, provider=fake, native_gif_provider=fake)

    manifest = orchestrator.run()

    assert manifest.state == "COMPLETED"
    assert manifest.generated_count["static"] == 8
    assert manifest.generated_count["animated"] == 8
    assert len(manifest.items) == 8

    # Verify files on disk and check that native GIFs were post-processed to 240x240
    for item in manifest.items:
        assert (out_dir / item.static_path).exists()
        anim_file = out_dir / item.animated_path
        assert anim_file.exists()
        with Image.open(anim_file) as gimg:
            assert gimg.size == (240, 240)
        assert (out_dir / item.thumbnail_path).exists()

    # Verify platform assets
    assert (out_dir / "platform" / "cover.png").exists()
    assert (out_dir / "platform" / "icon.png").exists()
    assert (out_dir / "platform" / "banner.png").exists()

    # Verify ZIP packages
    assert (out_dir / "static-pack.zip").exists()
    assert (out_dir / "animated-pack.zip").exists()

    # Verify source copy was removed because keep_source=False by default
    assert not list((out_dir / "work").glob("source_normalized_*"))

    # Test single-item regeneration
    first_item_id = manifest.items[0].id
    static_file = out_dir / manifest.items[0].static_path

    orchestrator.regenerate_single_item(first_item_id)
    assert static_file.exists()


def test_native_gif_fallback_to_keyframes_integration(tmp_path: Path):
    source_img = tmp_path / "cat.png"
    create_sample_photo(source_img)

    out_dir = tmp_path / "out_fallback_pack"
    job = JobConfig(
        job_id="fallback-pack",
        source_image=str(source_img),
        output_dir=str(out_dir),
        mode="animated",
        count=8,
        animation=AnimationConfig(backend="native-gif", frames=8),
        font_path=get_default_font_path(),
    )

    # Provider cannot do native gif (can_native_gif=False)
    fake_no_gif = FakeStickerProvider(can_native_gif=False)
    orchestrator = StickerOrchestrator(job=job, provider=fake_no_gif, native_gif_provider=fake_no_gif)

    manifest = orchestrator.run()
    assert manifest.generated_count["animated"] == 8
    assert (out_dir / "animated-pack.zip").exists()


def test_fifth_item_failure_and_single_item_recovery(tmp_path: Path):
    """Simulate 5th item (09_acknowledged) failing, then recover only the failed item."""
    source_img = tmp_path / "cat.png"
    create_sample_photo(source_img)

    out_dir = tmp_path / "partial_pack"
    job = JobConfig(
        job_id="partial-recovery-pack",
        source_image=str(source_img),
        output_dir=str(out_dir),
        mode="both",
        count=8,
        animation=AnimationConfig(backend="keyframes", frames=8),
        font_path=get_default_font_path(),
    )

    # 5th item in 8-item preset plan is 09_acknowledged
    flaky_provider = FakeStickerProvider(can_native_gif=False, fail_item_ids=["09_acknowledged"])
    orchestrator = StickerOrchestrator(
        job=job,
        provider=flaky_provider,
        native_gif_provider=flaky_provider,
        max_parallel=1,
    )

    manifest = orchestrator.run()
    assert manifest.state == "PARTIAL"
    assert manifest.generated_count["static"] == 7
    assert manifest.generated_count["animated"] == 7

    failed = [m for m in manifest.items if m.status == "FAILED"]
    assert len(failed) == 1
    assert failed[0].id == "09_acknowledged"

    # Record mtime of item #1 to prove it is NOT overwritten during recovery
    item1_path = out_dir / "static" / "01_hello.png"
    item1_bytes = item1_path.read_bytes()

    # Now recover item #5 using a healthy provider
    healthy_provider = FakeStickerProvider(can_native_gif=False)
    recovery_orch = StickerOrchestrator(
        job=job,
        provider=healthy_provider,
        native_gif_provider=healthy_provider,
    )
    updated_item = recovery_orch.regenerate_single_item("09_acknowledged")
    assert updated_item.status == "SUCCESS"
    assert (out_dir / "static" / "09_acknowledged.png").exists()
    assert (out_dir / "animated" / "09_acknowledged.gif").exists()
    assert item1_path.read_bytes() == item1_bytes


def test_sample_first_mode(tmp_path: Path):
    source_img = tmp_path / "cat.png"
    create_sample_photo(source_img)

    out_dir = tmp_path / "sample_pack"
    job = JobConfig(
        job_id="sample-pack",
        source_image=str(source_img),
        output_dir=str(out_dir),
        mode="both",
        count=16,
    )
    fake = FakeStickerProvider(can_native_gif=False)
    orchestrator = StickerOrchestrator(job=job, provider=fake, native_gif_provider=fake)
    manifest = orchestrator.run(sample_only=True)

    assert manifest.state == "SAMPLE_COMPLETED"
    assert manifest.generated_count["static"] == 2
    assert manifest.generated_count["animated"] == 1


def test_cloud_upload_permission_block(tmp_path: Path):
    source_img = tmp_path / "cat.png"
    create_sample_photo(source_img)

    out_dir = tmp_path / "blocked_pack"
    job = JobConfig(
        job_id="blocked-pack",
        source_image=str(source_img),
        output_dir=str(out_dir),
        allow_cloud_upload=False,
    )
    cloud_provider = OpenAIImagesProvider(api_key="sk-test-dummy")
    orchestrator = StickerOrchestrator(job=job, provider=cloud_provider)
    with pytest.raises(PermissionError, match="allow_cloud_upload=False"):
        orchestrator.run()


def test_exif_orientation_and_palette_extraction(tmp_path: Path):
    raw_img = Image.new("RGB", (300, 500), (245, 200, 210))
    exif = raw_img.getexif()
    exif[274] = 6  # Orientation 6 = Rotate 90 CW -> should become 500x300
    src_path = tmp_path / "rotated.jpg"
    raw_img.save(src_path, format="JPEG", exif=exif.tobytes())

    norm_path = tmp_path / "normalized.png"
    normalize_source_image(src_path, norm_path)
    with Image.open(norm_path) as nimg:
        assert nimg.size == (500, 300)

    palette = extract_dominant_palette(norm_path, count=3)
    assert len(palette) >= 1
    assert palette[0].startswith("#")


def test_flood_fill_preserves_interior_white_character(tmp_path: Path):
    # Opaque white background (255, 255, 255), dark outline ring, pure white interior
    img = Image.new("RGB", (200, 200), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([40, 40, 160, 160], fill=(255, 255, 255), outline=(80, 70, 70), width=6)

    cleaned = remove_matte_background(img)
    # Exterior corner is transparent
    assert cleaned.getpixel((5, 5))[3] == 0
    # Interior white face inside dark outline remains opaque!
    assert cleaned.getpixel((100, 100))[3] == 255


def test_sprite_sheet_animation_backend_integration(tmp_path: Path):
    source_img = tmp_path / "portrait.png"
    create_sample_photo(source_img)

    out_dir = tmp_path / "out_sprite_sheet_pack"
    job = JobConfig(
        job_id="sprite-sheet-pack",
        source_image=str(source_img),
        output_dir=str(out_dir),
        style="real-cutout",
        mode="both",
        count=8,
        animation=AnimationConfig(backend="sprite-sheet", frames=8, frame_duration_ms=160),
        font_path=get_default_font_path(),
    )

    fake = FakeStickerProvider(can_native_gif=False)
    orchestrator = StickerOrchestrator(job=job, provider=fake, native_gif_provider=fake)
    manifest = orchestrator.run()

    assert manifest.state == "COMPLETED"
    assert manifest.generated_count["static"] == 8
    assert manifest.generated_count["animated"] == 8
    assert len(list((out_dir / "work" / "raw_gif").glob("*_sheet_raw.png"))) == 8

    for item in manifest.items:
        gif_path = out_dir / item.animated_path
        assert gif_path.exists()
        with Image.open(gif_path) as gimg:
            assert gimg.size == (240, 240)
            assert gimg.info.get("transparency") == 0
            assert gimg.n_frames == 8
            gimg.seek(0)
            f0 = gimg.convert("RGBA").tobytes()
            gimg.seek(2)
            f2 = gimg.convert("RGBA").tobytes()
            assert f0 != f2
