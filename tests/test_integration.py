from pathlib import Path
from PIL import Image

from sticker_maker.config import get_default_font_path
from sticker_maker.orchestrator import StickerOrchestrator
from sticker_maker.providers.fake import FakeStickerProvider
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

    assert manifest.generated_count["static"] == 8
    assert manifest.generated_count["animated"] == 8
    assert len(manifest.items) == 8

    # Verify files on disk
    for item in manifest.items:
        assert (out_dir / item.static_path).exists()
        assert (out_dir / item.animated_path).exists()
        assert (out_dir / item.thumbnail_path).exists()

    # Verify platform assets
    assert (out_dir / "platform" / "cover.png").exists()
    assert (out_dir / "platform" / "icon.png").exists()
    assert (out_dir / "platform" / "banner.png").exists()

    # Verify ZIP packages
    assert (out_dir / "static-pack.zip").exists()
    assert (out_dir / "animated-pack.zip").exists()

    # Test single-item regeneration
    first_item_id = manifest.items[0].id
    static_file = out_dir / manifest.items[0].static_path
    old_mtime = static_file.stat().st_mtime

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
