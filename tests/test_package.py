import zipfile
from pathlib import Path
from PIL import Image
import pytest

from sticker_maker.package import create_zip_archive, package_deliverables
from scripts.make_test_fixture import create_broken_pack


def test_create_zip_archive_and_prevent_traversal(tmp_path: Path):
    f1 = tmp_path / "hello.txt"
    f1.write_text("hello", encoding="utf-8")

    zip_dest = tmp_path / "bundle.zip"
    create_zip_archive([(f1, "data/hello.txt")], zip_dest)

    assert zip_dest.exists()
    with zipfile.ZipFile(zip_dest, "r") as zf:
        assert "data/hello.txt" in zf.namelist()

    # Test rejection of path traversal (Zip Slip protection)
    with pytest.raises(ValueError, match="Illegal path traversal"):
        create_zip_archive([(f1, "../malicious.txt")], zip_dest)


def test_strict_packaging_blocks_failed_pack(tmp_path: Path):
    broken_dir = tmp_path / "broken_pack"
    create_broken_pack(broken_dir)

    with pytest.raises(ValueError, match="Strict packaging failed"):
        package_deliverables(broken_dir, strict=True)
