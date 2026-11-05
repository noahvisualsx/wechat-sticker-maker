from pathlib import Path
from PIL import Image
from sticker_maker.config import AssetSpec
from sticker_maker.quality.report import run_full_validation
from sticker_maker.quality.structural import validate_gif, validate_png
from scripts.make_test_fixture import create_broken_pack


def test_validate_png_spec(tmp_path: Path):
    spec = AssetSpec(size=(240, 240), max_bytes=500_000)
    valid_png = tmp_path / "valid.png"
    img = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    img.save(valid_png, format="PNG")

    checks = validate_png(valid_png, spec)
    assert all(c.status == "pass" for c in checks)

    # Wrong dimensions
    invalid_png = tmp_path / "invalid.png"
    bad_img = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    bad_img.save(invalid_png, format="PNG")
    bad_checks = validate_png(invalid_png, spec)
    assert any(c.status == "fail" and "Dimensions" in c.name for c in bad_checks)


def test_validate_broken_pack(tmp_path: Path):
    broken_dir = tmp_path / "broken_pack"
    create_broken_pack(broken_dir)

    report = run_full_validation(broken_dir)
    assert report.overall_status == "fail"
    assert report.stats["total_failures"] > 0
