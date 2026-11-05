"""Generate test fixture images and test pack fixtures."""

from pathlib import Path
from PIL import Image, ImageDraw


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


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    sample = repo_root / "tests" / "fixtures" / "sample_cat.png"
    create_sample_photo(sample)
    print(f"Created sample photo at {sample}")
