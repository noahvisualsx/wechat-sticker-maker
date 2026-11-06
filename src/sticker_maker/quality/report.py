"""Validation reporting and contact sheet preview generator."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from PIL import Image, ImageDraw

from ..config import get_profile
from ..schemas import ValidationCheck, ValidationReport
from .structural import validate_gif, validate_png
from .visual import check_visual_safety


def run_full_validation(
    output_dir: Path,
    profile_name: str = "wechat-conservative-2026-11",
) -> ValidationReport:
    profile = get_profile(profile_name)
    all_checks: List[ValidationCheck] = []
    stats = {
        "static_count": 0,
        "animated_count": 0,
        "thumbnail_count": 0,
        "total_failures": 0,
        "total_warnings": 0,
    }

    # Validate static stickers if static/ exists
    static_dir = output_dir / "static"
    if static_dir.exists():
        for png_file in sorted(static_dir.glob("*.png")):
            stats["static_count"] += 1
            all_checks.extend(validate_png(png_file, profile.sticker, check_name_prefix=f"Static {png_file.stem}"))
            all_checks.extend(check_visual_safety(png_file, check_name_prefix=f"Static {png_file.stem} Visual"))

    # Validate animated stickers if animated/ exists
    animated_dir = output_dir / "animated"
    if animated_dir.exists():
        for gif_file in sorted(animated_dir.glob("*.gif")):
            stats["animated_count"] += 1
            all_checks.extend(validate_gif(gif_file, profile.sticker, check_name_prefix=f"Animated {gif_file.stem}"))

    # Validate thumbnails if thumbnails/ exists
    thumb_dir = output_dir / "thumbnails"
    if thumb_dir.exists():
        for t_file in sorted(thumb_dir.glob("*.png")):
            stats["thumbnail_count"] += 1
            all_checks.extend(validate_png(t_file, profile.thumbnail, check_name_prefix=f"Thumb {t_file.stem}"))

    # Validate platform assets if platform/ exists
    platform_dir = output_dir / "platform"
    if platform_dir.exists():
        cover_p = platform_dir / "cover.png"
        if cover_p.exists():
            all_checks.extend(validate_png(cover_p, profile.cover, check_name_prefix="Platform Cover"))
        icon_p = platform_dir / "icon.png"
        if icon_p.exists():
            all_checks.extend(validate_png(icon_p, profile.icon, check_name_prefix="Platform Icon"))
        banner_p = platform_dir / "banner.png"
        if banner_p.exists():
            all_checks.extend(validate_png(banner_p, profile.banner, check_name_prefix="Platform Banner", require_alpha=False))

    # Validate manifest.json exists
    manifest_p = output_dir / "manifest.json"
    if not manifest_p.exists():
        all_checks.append(
            ValidationCheck(
                name="Manifest: Exists",
                target="manifest.json",
                status="fail",
                message="manifest.json not found in output directory",
            )
        )
    else:
        try:
            with manifest_p.open("r", encoding="utf-8") as f:
                mdata = json.load(f)
                items = mdata.get("items", [])
                all_checks.append(
                    ValidationCheck(
                        name="Manifest: Decode",
                        target="manifest.json",
                        status="pass",
                        message=f"Valid manifest with {len(items)} items",
                    )
                )
                for m_item in items:
                    item_id = m_item.get("id", "unknown")
                    if m_item.get("status") == "FAILED":
                        all_checks.append(
                            ValidationCheck(
                                name=f"Manifest Item {item_id}: Status",
                                target="manifest.json",
                                status="fail",
                                message=f"Item {item_id} failed generation: {m_item.get('error', 'unknown error')}",
                            )
                        )
                    for key in ("static_path", "animated_path", "thumbnail_path"):
                        rel = m_item.get(key)
                        if rel and not (output_dir / rel).exists():
                            all_checks.append(
                                ValidationCheck(
                                    name=f"Manifest Item {item_id}: {key}",
                                    target=rel,
                                    status="fail",
                                    message=f"Manifest references missing file: {rel}",
                                )
                            )
        except Exception as e:
            all_checks.append(
                ValidationCheck(
                    name="Manifest: Decode",
                    target="manifest.json",
                    status="fail",
                    message=f"Invalid manifest JSON: {e}",
                )
            )

    fails = [c for c in all_checks if c.status == "fail"]
    warns = [c for c in all_checks if c.status == "warn"]
    stats["total_failures"] = len(fails)
    stats["total_warnings"] = len(warns)

    overall = "fail" if fails else ("warn" if warns else "pass")

    report = ValidationReport(
        job_id=output_dir.name,
        profile=profile_name,
        overall_status=overall,
        timestamp=datetime.now(timezone.utc).isoformat(),
        checks=all_checks,
        stats=stats,
    )

    # Save reports
    qa_dir = output_dir / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    with (qa_dir / "report.json").open("w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)

    md_content = generate_markdown_report(report)
    with (qa_dir / "report.md").open("w", encoding="utf-8") as f:
        f.write(md_content)

    return report


def generate_markdown_report(report: ValidationReport) -> str:
    lines = [
        f"# Sticker Pack Validation Report: {report.job_id}",
        "",
        f"- **Timestamp**: {report.timestamp}",
        f"- **Profile**: {report.profile}",
        f"- **Overall Status**: **{report.overall_status.upper()}**",
        f"- **Static Stickers**: {report.stats.get('static_count', 0)}",
        f"- **Animated Stickers**: {report.stats.get('animated_count', 0)}",
        f"- **Thumbnails**: {report.stats.get('thumbnail_count', 0)}",
        f"- **Failures**: {report.stats.get('total_failures', 0)}",
        f"- **Warnings**: {report.stats.get('total_warnings', 0)}",
        "",
        "## Detailed Checks",
        "",
        "| Target | Check | Status | Details |",
        "|---|---|---|---|",
    ]
    for c in report.checks:
        icon = "✅" if c.status == "pass" else ("⚠️" if c.status == "warn" else "❌")
        lines.append(f"| `{c.target}` | {c.name} | {icon} {c.status} | {c.message} |")

    lines.append("")
    lines.append("> ⚠️ Note: Platform submission requirements must be manually re-verified in the official WeChat Sticker platform console.")
    return "\n".join(lines)


def generate_preview_sheet(
    output_dir: Path,
    target_path: Path | None = None,
    files: List[Path] | None = None,
) -> Path | None:
    """Generate a combined contact sheet preview for QA review (internal only)."""
    if files is None:
        static_dir = output_dir / "static"
        if not static_dir.exists():
            return None
        files = sorted(static_dir.glob("*.png"))
    if not files:
        return None

    num_files = len(files)
    cols = 4
    rows = int(math.ceil(num_files / float(cols)))

    cell_size = 240
    pad = 16
    banner_h = 40
    sheet_w = cols * (cell_size + pad) + pad
    sheet_h = rows * (cell_size + pad) + pad + banner_h

    # Create light gray checkerboard or clean neutral bg
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (245, 245, 248, 255))
    draw = ImageDraw.Draw(sheet)

    # Top banner
    draw.rectangle([0, 0, sheet_w, banner_h], fill=(50, 50, 60, 255))
    draw.text((pad, 10), "INTERNAL QA CONTACT SHEET — NOT FOR PLATFORM SUBMISSION", fill=(255, 255, 255, 255))

    for idx, f in enumerate(files):
        r = idx // cols
        c = idx % cols
        x = pad + c * (cell_size + pad)
        y = banner_h + pad + r * (cell_size + pad)

        # White cell background with border
        draw.rectangle([x, y, x + cell_size, y + cell_size], fill=(255, 255, 255, 255), outline=(220, 220, 225, 255))
        try:
            with Image.open(f) as cell_img:
                cell_rgba = cell_img.convert("RGBA")
                if cell_rgba.size != (cell_size, cell_size):
                    cell_rgba.thumbnail((cell_size, cell_size), Image.Resampling.LANCZOS)
                sheet.paste(cell_rgba, (x, y), cell_rgba)
        except Exception:
            pass

    out = target_path or (output_dir / "qa" / "preview-sheet.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, format="PNG")
    return out
