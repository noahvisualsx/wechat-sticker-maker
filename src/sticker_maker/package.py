"""Packaging and ZIP archive creation for WeChat Sticker deliverables."""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import List, Tuple

from .quality.report import run_full_validation


def create_zip_archive(source_files: List[Tuple[Path, str]], zip_path: Path) -> Path:
    """Create a clean ZIP archive with controlled relative paths, preventing path traversal."""
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_zip = zip_path.with_suffix(".tmp.zip")

    with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src_file, arc_name in source_files:
            # Prevent zip slip or leakage
            clean_arc = arc_name.replace("\\", "/").lstrip("/")
            if ".." in clean_arc.split("/"):
                raise ValueError(f"Illegal path traversal detected in archive name: {arc_name}")
            zf.write(src_file, clean_arc)

    # Verify archive integrity
    with zipfile.ZipFile(tmp_zip, "r") as zf:
        bad_file = zf.testzip()
        if bad_file:
            raise RuntimeError(f"Corrupt file found in created zip: {bad_file}")

    tmp_zip.replace(zip_path)
    return zip_path


def package_deliverables(
    output_dir: Path,
    strict: bool = True,
    profile_name: str = "wechat-conservative-2026-11",
) -> dict[str, Path]:
    """Package static and animated packs into clean, separate ZIP files."""
    if strict:
        report = run_full_validation(output_dir, profile_name=profile_name)
        if report.overall_status == "fail":
            fail_count = report.stats.get("total_failures", 0)
            raise ValueError(
                f"Strict packaging failed: output contains {fail_count} validation failures. "
                f"Review qa/report.md for details."
            )

    results: dict[str, Path] = {}
    manifest_file = output_dir / "manifest.json"

    # Common platform files
    common_files: List[Tuple[Path, str]] = []
    if manifest_file.exists():
        common_files.append((manifest_file, "manifest.json"))

    platform_dir = output_dir / "platform"
    if platform_dir.exists():
        for p in platform_dir.glob("*.png"):
            common_files.append((p, f"platform/{p.name}"))

    thumb_dir = output_dir / "thumbnails"
    if thumb_dir.exists():
        for p in thumb_dir.glob("*.png"):
            common_files.append((p, f"thumbnails/{p.name}"))

    # 1. Static Pack
    static_dir = output_dir / "static"
    if static_dir.exists():
        static_files = list(common_files)
        for p in sorted(static_dir.glob("*.png")):
            static_files.append((p, f"static/{p.name}"))
        if len(static_files) > len(common_files):
            static_zip = output_dir / "static-pack.zip"
            create_zip_archive(static_files, static_zip)
            results["static_zip"] = static_zip

    # 2. Animated Pack
    animated_dir = output_dir / "animated"
    if animated_dir.exists():
        anim_files = list(common_files)
        for p in sorted(animated_dir.glob("*.gif")):
            anim_files.append((p, f"animated/{p.name}"))
        if len(anim_files) > len(common_files):
            anim_zip = output_dir / "animated-pack.zip"
            create_zip_archive(anim_files, anim_zip)
            results["animated_zip"] = anim_zip

    return results
