"""Structural asset validation for WeChat requirements."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageSequence

from ..config import AssetSpec, PlatformProfile, get_profile
from ..schemas import ValidationCheck


def validate_png(
    path: Path,
    spec: AssetSpec,
    check_name_prefix: str = "PNG Check",
    require_alpha: bool = True,
) -> List[ValidationCheck]:
    checks: List[ValidationCheck] = []
    rel_path = str(path)

    if not path.exists():
        checks.append(
            ValidationCheck(
                name=f"{check_name_prefix}: Exists",
                target=rel_path,
                status="fail",
                message=f"File not found: {path}",
            )
        )
        return checks

    # File size check
    file_bytes = path.stat().st_size
    if file_bytes > spec.max_bytes:
        checks.append(
            ValidationCheck(
                name=f"{check_name_prefix}: File Size",
                target=rel_path,
                status="fail",
                message=f"Size {file_bytes} bytes exceeds maximum allowed {spec.max_bytes} bytes",
                details={"actual_bytes": file_bytes, "max_bytes": spec.max_bytes},
            )
        )
    else:
        checks.append(
            ValidationCheck(
                name=f"{check_name_prefix}: File Size",
                target=rel_path,
                status="pass",
                message=f"Size {file_bytes} bytes is within limit {spec.max_bytes}",
                details={"actual_bytes": file_bytes, "max_bytes": spec.max_bytes},
            )
        )

    # Decode and format check
    try:
        with Image.open(path) as img:
            fmt = img.format
            size = img.size
            mode = img.mode

            if fmt != "PNG":
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Format",
                        target=rel_path,
                        status="fail",
                        message=f"Expected format PNG, got {fmt}",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Format",
                        target=rel_path,
                        status="pass",
                        message="Valid PNG image",
                    )
                )

            if size != spec.size:
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Dimensions",
                        target=rel_path,
                        status="fail",
                        message=f"Dimensions {size} do not match required {spec.size}",
                        details={"actual": list(size), "expected": list(spec.size)},
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Dimensions",
                        target=rel_path,
                        status="pass",
                        message=f"Dimensions {size} match specification",
                    )
                )

            if require_alpha:
                has_alpha = mode in ("RGBA", "LA") or ("transparency" in img.info)
                if not has_alpha:
                    checks.append(
                        ValidationCheck(
                            name=f"{check_name_prefix}: Transparency",
                            target=rel_path,
                            status="warn",
                            message=f"Image mode {mode} might not contain an alpha channel",
                        )
                    )
                else:
                    checks.append(
                        ValidationCheck(
                            name=f"{check_name_prefix}: Transparency",
                            target=rel_path,
                            status="pass",
                            message="Transparent alpha channel present",
                        )
                    )
    except Exception as e:
        checks.append(
            ValidationCheck(
                name=f"{check_name_prefix}: Decode",
                target=rel_path,
                status="fail",
                message=f"Failed to decode image: {e}",
            )
        )

    return checks


def validate_gif(
    path: Path,
    spec: AssetSpec,
    check_name_prefix: str = "GIF Check",
) -> List[ValidationCheck]:
    checks: List[ValidationCheck] = []
    rel_path = str(path)

    if not path.exists():
        checks.append(
            ValidationCheck(
                name=f"{check_name_prefix}: Exists",
                target=rel_path,
                status="fail",
                message=f"File not found: {path}",
            )
        )
        return checks

    # File size check
    file_bytes = path.stat().st_size
    if file_bytes > spec.max_bytes:
        checks.append(
            ValidationCheck(
                name=f"{check_name_prefix}: File Size",
                target=rel_path,
                status="fail",
                message=f"Size {file_bytes} bytes exceeds maximum allowed {spec.max_bytes} bytes",
                details={"actual_bytes": file_bytes, "max_bytes": spec.max_bytes},
            )
        )
    else:
        checks.append(
            ValidationCheck(
                name=f"{check_name_prefix}: File Size",
                target=rel_path,
                status="pass",
                message=f"Size {file_bytes} bytes is within limit {spec.max_bytes}",
                details={"actual_bytes": file_bytes, "max_bytes": spec.max_bytes},
            )
        )

    try:
        with Image.open(path) as img:
            fmt = img.format
            size = img.size

            if fmt != "GIF":
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Format",
                        target=rel_path,
                        status="fail",
                        message=f"Expected format GIF, got {fmt}",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Format",
                        target=rel_path,
                        status="pass",
                        message="Valid GIF image",
                    )
                )

            if size != spec.size:
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Dimensions",
                        target=rel_path,
                        status="fail",
                        message=f"Dimensions {size} do not match required {spec.size}",
                        details={"actual": list(size), "expected": list(spec.size)},
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Dimensions",
                        target=rel_path,
                        status="pass",
                        message=f"Dimensions {size} match specification",
                    )
                )

            # Check frames
            frames = [f.copy() for f in ImageSequence.Iterator(img)]
            frame_count = len(frames)
            if frame_count < 2:
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Frame Count",
                        target=rel_path,
                        status="fail",
                        message=f"GIF has only {frame_count} frame; animation requires >= 2 frames",
                        details={"frame_count": frame_count},
                    )
                )
            else:
                # Check that frames are not identical
                f0_bytes = frames[0].tobytes()
                f1_bytes = frames[1].tobytes()
                if f0_bytes == f1_bytes and all(f.tobytes() == f0_bytes for f in frames):
                    checks.append(
                        ValidationCheck(
                            name=f"{check_name_prefix}: Distinct Motion",
                            target=rel_path,
                            status="fail",
                            message="All frames are identical; fake animated result detected",
                        )
                    )
                else:
                    checks.append(
                        ValidationCheck(
                            name=f"{check_name_prefix}: Frame Count",
                            target=rel_path,
                            status="pass",
                            message=f"Multi-frame animated GIF with {frame_count} frames",
                            details={"frame_count": frame_count},
                        )
                    )

            # Check loop info
            loop = img.info.get("loop", 0)
            if loop != 0:
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Loop Policy",
                        target=rel_path,
                        status="warn",
                        message=f"GIF loop is {loop}; platform recommends 0 (infinite loop)",
                    )
                )
            else:
                checks.append(
                    ValidationCheck(
                        name=f"{check_name_prefix}: Loop Policy",
                        target=rel_path,
                        status="pass",
                        message="Loop is set to 0 (infinite)",
                    )
                )
    except Exception as e:
        checks.append(
            ValidationCheck(
                name=f"{check_name_prefix}: Decode",
                target=rel_path,
                status="fail",
                message=f"Failed to decode GIF: {e}",
            )
        )

    return checks
