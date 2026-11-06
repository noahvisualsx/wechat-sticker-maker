"""Generate test fixture images and test pack fixtures."""

from pathlib import Path
import sys
from PIL import Image, ImageDraw

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


def create_sample_photo(target_path: Path) -> Path:
    """Create a sample cat photo test fixture."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (640, 640), (240, 235, 225))
    draw = ImageDraw.Draw(img)

    # Cat body & head
    draw.ellipse([180, 200, 460, 480], fill=(255, 246, 234), outline=(120, 100, 95), width=4)
    # Ears
    draw.polygon([(200, 230), (180, 120), (280, 180)], fill=(255, 246, 234), outline=(120, 100, 95))
    draw.polygon([(440, 230), (460, 120), (360, 180)], fill=(190, 185, 180), outline=(120, 100, 95))
    # Eyes
    draw.ellipse([250, 300, 290, 340], fill=(60, 50, 50))
    draw.ellipse([350, 300, 390, 340], fill=(60, 50, 50))
    # Nose
    draw.polygon([(310, 350), (330, 350), (320, 365)], fill=(240, 160, 175))

    img.save(target_path, format="PNG")
    return target_path


def create_broken_pack(target_dir: Path) -> Path:
    """Create a pack that should fail validation (wrong size, single-frame GIF, etc.)."""
    static_dir = target_dir / "static"
    animated_dir = target_dir / "animated"
    static_dir.mkdir(parents=True, exist_ok=True)
    animated_dir.mkdir(parents=True, exist_ok=True)

    # Broken PNG: wrong size (100x100 instead of 240x240)
    bad_png = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    bad_png.save(static_dir / "01_hello.png", format="PNG")

    # Broken GIF: single frame (fake animation)
    bad_gif = Image.new("RGBA", (240, 240), (0, 255, 0, 255))
    bad_gif.save(animated_dir / "01_hello.gif", format="GIF")

    # No manifest
    return target_dir


def create_good_pack(target_dir: Path) -> Path:
    """Create a valid 8-sticker fixture pack that passes all structural and visual checks."""
    from sticker_maker.config import get_default_font_path
    from sticker_maker.orchestrator import StickerOrchestrator
    from sticker_maker.providers.fake import FakeStickerProvider
    from sticker_maker.schemas import AnimationConfig, JobConfig

    sample_photo = target_dir.parent / "sample_cat.png"
    if not sample_photo.exists():
        create_sample_photo(sample_photo)

    job = JobConfig(
        job_id="good-pack-fixture",
        source_image=str(sample_photo),
        output_dir=str(target_dir),
        mode="both",
        count=8,
        animation=AnimationConfig(backend="keyframes", frames=8, frame_duration_ms=180),
        font_path=get_default_font_path(),
    )
    fake = FakeStickerProvider(can_native_gif=True)
    orchestrator = StickerOrchestrator(job=job, provider=fake, native_gif_provider=fake)
    orchestrator.run()
    return target_dir


if __name__ == "__main__":
    fixtures_dir = repo_root / "tests" / "fixtures"
    sample = fixtures_dir / "sample_cat.png"
    create_sample_photo(sample)
    create_good_pack(fixtures_dir / "good_pack")
    create_broken_pack(fixtures_dir / "broken_pack")
    print(f"Created fixtures in {fixtures_dir}")
