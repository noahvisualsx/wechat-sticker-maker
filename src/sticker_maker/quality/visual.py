"""Visual quality and character safety checks."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional
from PIL import Image

from ..schemas import ValidationCheck
from .anatomy import detect_baked_checkerboard


def check_visual_safety(
    path: Path,
    check_name_prefix: str = "Visual Check",
) -> List[ValidationCheck]:
    checks: List[ValidationCheck] = []
    rel_path = str(path)

    if not path.exists():
        return checks

    try:
        with Image.open(path) as img:
            rgba = img.convert("RGBA")
            checker_chk = detect_baked_checkerboard(rgba, target_label=rel_path)
            checker_chk.name = f"{check_name_prefix}: Fake Checkerboard Check"
            checks.append(checker_chk)
            w, h = rgba.size
            alpha = rgba.getchannel("A")
            bbox = alpha.getbbox()

            if not bbox:
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Content Presence",
                        target=rel_path,
                        status="fail",
                        message="Image is completely transparent / blank",
                    )
                )
                return checks

            # Content area occupancy
            content_w = bbox[2] - bbox[0]
            content_h = bbox[3] - bbox[1]
            content_area = content_w * content_h
            total_area = w * h
            occupancy = content_area / float(total_area)

            if occupancy < 0.10:
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Subject Size",
                        target=rel_path,
                        status="warn",
                        message=f"Subject occupancy is very small ({occupancy:.1%})",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Subject Size",
                        target=rel_path,
                        status="pass",
                        message=f"Subject well proportioned ({occupancy:.1%} canvas occupancy)",
                    )
                )

            # Check safe perimeter (2px margin)
            a_data = alpha.load()
            outer_bleed = False
            for x in range(w):
                if a_data[x, 0] > 0 or a_data[x, h - 1] > 0:
                    outer_bleed = True
                    break
            if not outer_bleed:
                for y in range(h):
                    if a_data[0, y] > 0 or a_data[w - 1, y] > 0:
                        outer_bleed = True
                        break

            if outer_bleed:
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Safe Margin",
                        target=rel_path,
                        status="warn",
                        message="Pixels bleed directly into outer boundary; safe margin recommended",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Safe Margin",
                        target=rel_path,
                        status="pass",
                        message="Safe transparent border maintained",
                    )
                )
    except Exception as e:
        checks.append(
            ValidationCheck(
                name=f"{check_name_prefix}: Inspection",
                target=rel_path,
                status="fail",
                message=f"Failed visual inspection: {e}",
            )
        )

    return checks
