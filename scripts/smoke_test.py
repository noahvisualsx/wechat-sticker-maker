"""End-to-end smoke test script."""

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from PIL import Image

from sticker_maker.config import get_default_font_path
from sticker_maker.orchestrator import StickerOrchestrator
from sticker_maker.providers.fake import FakeStickerProvider
from sticker_maker.quality.report import run_full_validation
from sticker_maker.schemas import AnimationConfig, JobConfig
from scripts.make_test_fixture import create_sample_photo



def run_smoke_test() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    test_dir = repo_root / "output" / "smoke_test_run"
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)

    test_dir.mkdir(parents=True, exist_ok=True)
    input_img = test_dir / "sample_cat.png"
    create_sample_photo(input_img)

    job = JobConfig(
        job_id="smoke-cat-01",
        source_image=str(input_img),
        output_dir=str(test_dir),
        mode="both",
        count=16,
        style="kawaii-flat",
        language="zh-CN",
        animation=AnimationConfig(backend="auto", frames=8, frame_duration_ms=180),
        font_path=get_default_font_path(),
    )

    print("Running orchestrator with FakeStickerProvider...")
    orchestrator = StickerOrchestrator(
        job=job,
        provider=FakeStickerProvider(can_native_gif=True),
        native_gif_provider=FakeStickerProvider(can_native_gif=True),
    )
    manifest = orchestrator.run()

    print(f"Generated: {manifest.generated_count}")
    assert manifest.generated_count["static"] == 16, f"Expected 16 static, got {manifest.generated_count['static']}"
    assert manifest.generated_count["animated"] == 16, f"Expected 16 animated, got {manifest.generated_count['animated']}"

    # Check ZIP archives
    static_zip = test_dir / "static-pack.zip"
    anim_zip = test_dir / "animated-pack.zip"
    assert static_zip.exists(), "static-pack.zip missing"
    assert anim_zip.exists(), "animated-pack.zip missing"

    # Validate report
    report = run_full_validation(test_dir)
    print(f"Validation status: {report.overall_status}")
    assert report.overall_status in ("pass", "warn"), f"Validation failed: {report.stats}"

    print("Smoke test passed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(run_smoke_test())
