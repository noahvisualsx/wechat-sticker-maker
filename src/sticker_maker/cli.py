"""Unified CLI entry point for WeChat Sticker Maker."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from .config import AppSettings, get_default_font_path, get_profile
from .orchestrator import StickerOrchestrator
from .package import package_deliverables
from .planner import plan_expressions
from .providers.fake import FakeStickerProvider
from .providers.openai_images import OpenAIImagesProvider
from .providers.openai_native_gif import OpenAINativeGifProvider
from .quality.report import run_full_validation
from .schemas import AnimationConfig, JobConfig

logger = logging.getLogger("sticker_maker")


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def cmd_doctor(args: argparse.Namespace) -> int:
    """Check runtime environment, dependencies, fonts, and API credentials."""
    print("=== WeChat Sticker Maker Doctor ===")
    print(f"Python Version: {sys.version}")

    # Check dependencies
    missing = []
    for pkg in ("PIL", "pydantic", "yaml", "requests"):
        try:
            __import__(pkg)
            print(f"  [OK] Python package: {pkg}")
        except ImportError:
            print(f"  [MISSING] Python package: {pkg}")
            missing.append(pkg)

    # Check fonts
    font_path = get_default_font_path()
    if font_path:
        print(f"  [OK] Detected Chinese Font: {font_path}")
    else:
        print("  [WARN] No Chinese TrueType font automatically detected. Fallback default will be used.")

    # Check API key
    settings = AppSettings()
    if settings.openai_api_key:
        masked = settings.openai_api_key[:6] + "..." + settings.openai_api_key[-4:]
        print(f"  [OK] OPENAI_API_KEY detected ({masked})")
        print(f"       Image Model: {settings.sticker_image_model}")
        print(f"       GIF Model:   {settings.sticker_gif_model}")
    else:
        print("  [INFO] No OPENAI_API_KEY detected. System is running in offline / mock provider mode.")

    if missing:
        print("Status: Incomplete environment. Please install missing packages.")
        return 3

    print("Doctor check complete. Ready for generation.")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    """Plan job parameters and generate job.json."""
    source_p = Path(args.input)
    if not source_p.exists():
        print(f"Error: Source image file not found: {source_p}", file=sys.stderr)
        return 2

    out_p = Path(args.output)
    out_p.mkdir(parents=True, exist_ok=True)

    job_id = args.job_id or out_p.name
    job = JobConfig(
        job_id=job_id,
        source_image=str(source_p.resolve()),
        output_dir=str(out_p.resolve()),
        mode=args.mode,
        count=args.count,
        style=args.style,
        language=args.language,
        animation=AnimationConfig(
            backend=args.animation_backend,
            frames=args.gif_frames,
            frame_duration_ms=args.gif_duration,
        ),
        export_profile=args.profile,
        font_path=args.font or get_default_font_path(),
    )

    job_file = out_p / "job.json"
    with job_file.open("w", encoding="utf-8") as f:
        json.dump(job.model_dump(), f, indent=2, ensure_ascii=False)

    print(f"Planned job saved to {job_file}")
    print(f"Total expressions planned: {job.count}")
    expressions = plan_expressions(count=job.count)
    for idx, e in enumerate(expressions, 1):
        print(f"  {idx:02d}. [{e.caption}] {e.mood} -> {e.static_pose}")

    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    """Execute generation pipeline from job.json."""
    job_p = Path(args.job)
    if not job_p.exists():
        print(f"Error: job.json not found: {job_p}", file=sys.stderr)
        return 2

    with job_p.open("r", encoding="utf-8") as f:
        job_data = json.load(f)

    # Allow CLI overrides
    if args.animation_backend:
        job_data.setdefault("animation", {})["backend"] = args.animation_backend

    job = JobConfig(**job_data)

    provider = None
    gif_provider = None
    if args.provider == "fake":
        provider = FakeStickerProvider()
        gif_provider = FakeStickerProvider()
    elif args.provider == "openai":
        settings = AppSettings()
        provider = OpenAIImagesProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            image_model=settings.sticker_image_model,
        )
        gif_provider = OpenAINativeGifProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            gif_model=settings.sticker_gif_model,
        )

    orchestrator = StickerOrchestrator(job=job, provider=provider, native_gif_provider=gif_provider)
    try:
        manifest = orchestrator.run()
        print(f"Generation finished. Generated: {manifest.generated_count}")
        print(f"Manifest saved at: {job.output_dir}/manifest.json")
        print(f"QA report saved at: {job.output_dir}/qa/report.md")
        return 0
    except Exception as e:
        logger.exception("Generation error: %s", e)
        print(f"Error during generation: {e}", file=sys.stderr)
        return 4


def cmd_regenerate(args: argparse.Namespace) -> int:
    """Regenerate a specific expression item."""
    job_p = Path(args.job)
    if not job_p.exists():
        print(f"Error: job.json not found: {job_p}", file=sys.stderr)
        return 2

    with job_p.open("r", encoding="utf-8") as f:
        job = JobConfig(**json.load(f))

    orchestrator = StickerOrchestrator(job=job)
    try:
        orchestrator.regenerate_single_item(args.item)
        print(f"Item {args.item} regenerated successfully.")
        return 0
    except Exception as e:
        print(f"Error regenerating item: {e}", file=sys.stderr)
        return 4


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate assets against platform specifications."""
    out_p = Path(args.output)
    if not out_p.exists():
        print(f"Error: Output folder not found: {out_p}", file=sys.stderr)
        return 2

    report = run_full_validation(out_p, profile_name=args.profile)
    print(f"Validation finished. Overall status: {report.overall_status.upper()}")
    print(f"  Failures: {report.stats.get('total_failures', 0)}")
    print(f"  Warnings: {report.stats.get('total_warnings', 0)}")
    print(f"Report written to: {out_p}/qa/report.md")

    if report.overall_status == "fail":
        return 5
    return 0


def cmd_package(args: argparse.Namespace) -> int:
    """Package validated files into separate ZIP archives."""
    out_p = Path(args.output)
    if not out_p.exists():
        print(f"Error: Output folder not found: {out_p}", file=sys.stderr)
        return 2

    try:
        zips = package_deliverables(out_p, strict=args.strict, profile_name=args.profile)
        for name, p in zips.items():
            print(f"Created package: {name} -> {p} ({p.stat().st_size} bytes)")
        return 0
    except Exception as e:
        print(f"Packaging error: {e}", file=sys.stderr)
        return 5


def main() -> None:
    parser = argparse.ArgumentParser(prog="wechat-sticker-maker", description="WeChat AI Sticker Maker CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # doctor
    subparsers.add_parser("doctor", help="Check local dependencies, fonts, and API environment")

    # plan
    p_plan = subparsers.add_parser("plan", help="Plan expressions and create job.json")
    p_plan.add_argument("--input", "-i", required=True, help="Path to input photo")
    p_plan.add_argument("--output", "-o", required=True, help="Output directory")
    p_plan.add_argument("--job-id", help="Job identifier")
    p_plan.add_argument("--mode", choices=["both", "static", "animated"], default="both")
    p_plan.add_argument("--count", type=int, choices=[8, 16, 24], default=16)
    p_plan.add_argument("--style", default="kawaii-flat")
    p_plan.add_argument("--language", default="zh-CN")
    p_plan.add_argument("--animation-backend", choices=["auto", "keyframes", "native-gif"], default="auto")
    p_plan.add_argument("--gif-frames", type=int, default=8)
    p_plan.add_argument("--gif-duration", type=int, default=180)
    p_plan.add_argument("--profile", default="wechat-conservative-2026-11")
    p_plan.add_argument("--font", help="Path to Chinese TTF/OTF font")

    # generate
    p_gen = subparsers.add_parser("generate", help="Run generation pipeline")
    p_gen.add_argument("--job", "-j", required=True, help="Path to job.json")
    p_gen.add_argument("--provider", choices=["auto", "fake", "openai"], default="auto")
    p_gen.add_argument("--animation-backend", choices=["auto", "keyframes", "native-gif"])

    # regenerate
    p_regen = subparsers.add_parser("regenerate", help="Regenerate a specific single item")
    p_regen.add_argument("--job", "-j", required=True, help="Path to job.json")
    p_regen.add_argument("--item", required=True, help="Expression item ID to regenerate (e.g. 05_shy)")

    # validate
    p_val = subparsers.add_parser("validate", help="Validate assets in output directory")
    p_val.add_argument("--output", "-o", required=True, help="Output directory containing assets")
    p_val.add_argument("--profile", default="wechat-conservative-2026-11")

    # package
    p_pkg = subparsers.add_parser("package", help="Create ZIP archives for platform submission")
    p_pkg.add_argument("--output", "-o", required=True, help="Output directory containing assets")
    p_pkg.add_argument("--strict", action="store_true", default=True, help="Enforce passing QA report")
    p_pkg.add_argument("--profile", default="wechat-conservative-2026-11")

    args = parser.parse_args()
    setup_logging()

    cmd_map = {
        "doctor": cmd_doctor,
        "plan": cmd_plan,
        "generate": cmd_generate,
        "regenerate": cmd_regenerate,
        "validate": cmd_validate,
        "package": cmd_package,
    }

    exit_code = cmd_map[args.command](args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
