"""Unified CLI entry point for WeChat Sticker Maker."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from .config import AppSettings, get_default_font_path, get_profile
from .duo import DUO_CATEGORIES, DUO_CATEGORY_LABELS, list_duo_presets
from .orchestrator import StickerOrchestrator
from .package import package_deliverables
from .i18n import BUILTIN_CAPTION_LANGUAGES, describe_font_support, normalize_language
from .planner import CATEGORY_LABELS, list_categories, load_all_presets, localized_caption, plan_expressions, translation_template
from .platforms import load_platform_profiles, platform_groups, resolve_platforms
from .memes import list_memes, make_meme, meme_category_label, resolve_meme_id
from .processing.gif_encoder import assemble_gif_from_keyframe_files, assemble_gif_from_sprite_sheet
from .processing.optimizer import optimize_gif, optimize_png
from .providers.fake import FakeStickerProvider
from .providers.gemini_images import GeminiImagesProvider
from .providers.openai_images import OpenAIImagesProvider
from .providers.openai_native_gif import OpenAINativeGifProvider
from .quality.report import run_full_validation
from .schemas import AnimationConfig, JobConfig
from .styles import STYLE_REGIONS, infer_language_for_style, list_style_presets, resolve_style_preset

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
    if settings.gemini_api_key:
        masked = settings.gemini_api_key[:6] + "..." + settings.gemini_api_key[-4:]
        print(f"  [OK] GEMINI_API_KEY detected ({masked}) -> {settings.gemini_image_model}")
    if settings.ark_api_key:
        masked = settings.ark_api_key[:6] + "..." + settings.ark_api_key[-4:]
        print(f"  [OK] ARK_API_KEY detected ({masked}) -> {settings.ark_image_model}")
    if not (settings.openai_api_key or settings.gemini_api_key or settings.ark_api_key):
        print("  [INFO] No cloud API key detected. System is running in offline / Agent built-in image mode.")

    if missing:
        print("Status: Incomplete environment. Please install missing packages.")
        return 3

    print("Doctor check complete. Ready for generation.")
    return 0


def cmd_styles(args: argparse.Namespace) -> int:
    """List available built-in sticker style presets."""
    try:
        presets = list_style_presets(region=getattr(args, "region", None))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    if getattr(args, "json", False):
        print(json.dumps([p.model_dump() for p in presets], indent=2, ensure_ascii=False))
        return 0

    print(f"=== 真人表情包风格 ({len(presets)} 款，全部保留本人真实五官) ===")
    for region in STYLE_REGIONS:
        group = [p for p in presets if p.region == region]
        if not group:
            continue
        print(f"\n[{region}] ({len(group)})")
        for p in group:
            print(f"  * {p.id:<22} {p.display_name}")
            print(f"    - 描述: {p.description}")
            print(f"    - 渲染: lighting={p.lighting}, palette={','.join(p.default_palette)}, 白边={p.die_cut_border_px}px")
    return 0


def cmd_duo(args: argparse.Namespace) -> int:
    """List built-in 108 real-person duo interaction presets (闺蜜 / 情侣 / 百合)."""
    lang = normalize_language(args.language)
    try:
        items = list_duo_presets(category=getattr(args, "category", None))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    if getattr(args, "json", False):
        print(json.dumps([i.model_dump() for i in items], indent=2, ensure_ascii=False))
        return 0

    print(f"=== 双人互动真人表情包预设 ({len(items)} 套: 闺蜜36 + 情侣36 + 百合36, language={lang}) ===")
    for cid in DUO_CATEGORIES:
        group = [i for i in items if i.category == cid]
        if not group:
            continue
        meta = DUO_CATEGORY_LABELS[cid]
        print(f"\n[{cid}] {meta['zh']} / {meta['en']} ({len(group)}) — {meta['desc_zh']}")
        for it in group:
            cap, _ = localized_caption(it, lang)
            bubble = it.bubble.texts.get(lang, "") if it.bubble else ""
            b_tag = f" 💬[{bubble}]" if bubble else ""
            print(f"  * {it.id:<30} {cap}{b_tag}  <{it.text_layout}> {it.mood}")
            print(f"    pose: {it.static_pose}")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    """Plan job parameters and generate job.json."""
    source_p = Path(args.input)
    if not source_p.exists():
        print(f"Error: Source image file not found: {source_p}", file=sys.stderr)
        return 2

    partner_p = None
    if getattr(args, "partner", None):
        partner_p = Path(args.partner)
        if not partner_p.exists():
            print(f"Error: Partner image file not found: {partner_p}", file=sys.stderr)
            return 2

    out_p = Path(args.output)
    out_p.mkdir(parents=True, exist_ok=True)

    raw_lang = args.language
    resolved_lang = infer_language_for_style(args.style) if raw_lang.strip().lower() == "auto" else normalize_language(raw_lang)
    extra_langs = [normalize_language(x) for x in (_split(getattr(args, "languages", None)) or [])] or None
    duo_cats = _split(getattr(args, "duo_category", None))
    duo_ids = _split(getattr(args, "duo_ids", None))
    pack_type = args.pack_type
    if (partner_p or duo_cats or duo_ids) and pack_type == "expressions":
        pack_type = "duo"

    job_id = args.job_id or out_p.name
    job = JobConfig(
        job_id=job_id,
        source_image=str(source_p.resolve()),
        partner_image=str(partner_p.resolve()) if partner_p else None,
        partner_facts=_split(getattr(args, "partner_facts", None)),
        output_dir=str(out_p.resolve()),
        mode=args.mode,
        count=args.count,
        style=args.style,
        language=resolved_lang,
        languages=extra_langs,
        text_layout=args.text_layout,
        bubble_shape=args.bubble_shape,
        bubble_animation=args.bubble_animation,
        categories=_split(args.categories),
        expression_ids=_split(args.expressions),
        duo_categories=duo_cats,
        duo_ids=duo_ids,
        pack_type=pack_type,
        meme_templates=[resolve_meme_id(m) for m in (_split(args.meme_templates) or [])] or None,
        meme_categories=_split(args.meme_categories),
        meme_texts=_parse_meme_texts(args.meme_text),
        captions_file=str(Path(args.captions_file).resolve()) if args.captions_file else None,
        platforms=resolve_platforms(args.platforms),
        master_size=args.master_size,
        pack_title=args.pack_title,
        animation=AnimationConfig(
            backend=args.animation_backend,
            frames=args.gif_frames,
            frame_duration_ms=args.gif_duration,
        ),
        export_profile=args.profile,
        allow_cloud_upload=args.allow_cloud_upload,
        keep_source=args.keep_source,
        resume=getattr(args, "resume", True),
        matting=getattr(args, "matting", "auto"),
        font_path=args.font or get_default_font_path(),
        subject_type=args.subject_type,
    )

    job_file = out_p / "job.json"
    with job_file.open("w", encoding="utf-8") as f:
        json.dump(job.model_dump(), f, indent=2, ensure_ascii=False)

    preset = resolve_style_preset(job.style)
    print(f"Planned job saved to {job_file}")
    print(f"Style selected: {preset.id} ({preset.display_name} - {preset.category})")
    print(f"Language: {job.language} (single language for every sticker)")
    print(f"Platforms: {', '.join(job.platforms)}")
    print(f"Total expressions planned: {job.count}")
    from .planner import plan_pack

    expressions = plan_pack(job, strict_counts="wechat" in job.platforms)
    for idx, e in enumerate(expressions, 1):
        cap, missing = localized_caption(e, job.language)
        flag = " (需翻译)" if missing and not job.captions_file else ""
        print(f"  {idx:02d}. [{cap}]{flag} <{e.category}/{e.text_layout}> {e.mood} -> {e.static_pose}")
    if job.language not in BUILTIN_CAPTION_LANGUAGES and not job.captions_file:
        print(f"Note: '{job.language}' has no built-in captions; run `captions-template --language {job.language}` and pass --captions-file.")

    return 0


def _build_providers(provider_arg: str):
    provider = None
    gif_provider = None
    settings = AppSettings()
    if provider_arg == "fake":
        provider = FakeStickerProvider()
        gif_provider = FakeStickerProvider()
    elif provider_arg == "openai":
        provider = OpenAIImagesProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            image_model=settings.sticker_image_model,
            max_retries=settings.sticker_max_retries,
        )
        gif_provider = OpenAINativeGifProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            gif_model=settings.sticker_gif_model,
            max_retries=settings.sticker_max_retries,
        )
    elif provider_arg == "gemini":
        provider = GeminiImagesProvider(
            api_key=settings.gemini_api_key,
            image_model=settings.gemini_image_model,
            max_retries=settings.sticker_max_retries,
        )
        gif_provider = FakeStickerProvider()
    elif provider_arg == "ark":
        provider = OpenAIImagesProvider(
            api_key=settings.ark_api_key,
            base_url=settings.ark_base_url,
            image_model=settings.ark_image_model,
            max_retries=settings.sticker_max_retries,
        )
        gif_provider = FakeStickerProvider()
    return provider, gif_provider


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
    if getattr(args, "style", None):
        job_data["style"] = args.style
    if getattr(args, "language", None):
        raw_l = args.language
        job_data["language"] = infer_language_for_style(job_data.get("style", "real-cutout")) if raw_l.strip().lower() == "auto" else normalize_language(raw_l)
    if getattr(args, "languages", None):
        job_data["languages"] = [normalize_language(x) for x in (_split(args.languages) or [])]
    if getattr(args, "platforms", None):
        job_data["platforms"] = resolve_platforms(args.platforms)
    if getattr(args, "resume", None) is not None:
        job_data["resume"] = args.resume
    if getattr(args, "matting", None):
        job_data["matting"] = args.matting

    job = JobConfig(**job_data)
    provider, gif_provider = _build_providers(args.provider)

    orchestrator = StickerOrchestrator(
        job=job,
        provider=provider,
        native_gif_provider=gif_provider,
        max_parallel=getattr(args, "max_parallel", None),
    )
    try:
        manifest = orchestrator.run(sample_only=getattr(args, "sample", False))
        print(f"Generation finished (state={manifest.state}). Generated: {manifest.generated_count}")
        print(f"Manifest saved at: {job.output_dir}/manifest.json")
        print(f"QA report saved at: {job.output_dir}/qa/report.md")
        for pid, res in orchestrator.export_results.items():
            zp = f" → {res.zip_path}" if res.zip_path else ""
            print(f"  [{res.status.upper():4}] {pid}: {len(res.files)} files, {len(res.showcase)} showcase{zp}")
        if manifest.state == "PARTIAL":
            return 6
        return 0
    except PermissionError as e:
        print(f"Security/Permission error: {e}", file=sys.stderr)
        return 7
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

    provider, gif_provider = _build_providers(getattr(args, "provider", "auto"))
    orchestrator = StickerOrchestrator(job=job, provider=provider, native_gif_provider=gif_provider)
    try:
        orchestrator.regenerate_single_item(args.item)
        print(f"Item {args.item} regenerated successfully.")
        return 0
    except PermissionError as e:
        print(f"Security/Permission error: {e}", file=sys.stderr)
        return 7
    except ValueError as e:
        print(f"Invalid input: {e}", file=sys.stderr)
        return 2
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


def _parse_meme_texts(values):
    out = {}
    for v in values or []:
        if "=" not in v:
            raise SystemExit(f"--meme-text expects TEMPLATE=TEXT, got {v!r}")
        k, t = v.split("=", 1)
        out[resolve_meme_id(k)] = t
    return out or None


def cmd_memes(args: argparse.Namespace) -> int:
    """List meme / abstract templates."""
    lang = normalize_language(args.language)
    items = list_memes(lang, args.category)
    from .planner import MEME_CATEGORY_LABELS

    order = {c: i for i, c in enumerate(MEME_CATEGORY_LABELS)}
    items = sorted(items, key=lambda m: (order.get(m.category, 99), m.id))
    if args.json:
        print(json.dumps([i.model_dump() for i in items], ensure_ascii=False, indent=2))
        return 0
    print(f"=== Meme templates ({len(items)}) language={lang} ===")
    current = None
    for it in items:
        if it.category != current:
            current = it.category
            print(f"\n[{current}] {meme_category_label(current)}")
        cap, _ = localized_caption(it, lang)
        els = ",".join(e.type for e in (it.meme.elements if it.meme else []))
        flt = ",".join(it.meme.filters) if it.meme and it.meme.filters else ""
        print(f"  {it.id:<26} {it.name_zh or ''} | {cap}  [{els}{(' | ' + flt) if flt else ''}]")
    print("\n别名: claude / 正在思考 → m01, 中国ip / 禁止靠近 → m02, 封号 / 再说话封你号 → m03, 熊猫头 → m19 ...")
    return 0


def cmd_meme(args: argparse.Namespace) -> int:
    """Render one meme template over character image(s)."""
    gif = Path(args.output) if args.output else None
    png = Path(args.static_output) if args.static_output else (gif.with_suffix(".png") if gif else None)
    try:
        outs = make_meme(
            args.template,
            images=[Path(p) for p in (args.image or [])],
            sprite_sheet=Path(args.sprite_sheet) if args.sprite_sheet else None,
            gif_output=gif,
            png_output=png,
            language=normalize_language(args.language),
            text=args.text,
            style=args.style,
            size=args.size,
            frames=args.gif_frames,
            frame_duration_ms=args.gif_duration,
            color=args.color,
            font_path=args.font or get_default_font_path(),
        )
    except Exception as e:
        print(f"Meme error: {e}", file=sys.stderr)
        return 4
    for k, v in outs.items():
        print(f"{k.upper()}: {v}")
    if gif and "gif" not in outs:
        print("Note: single image + static template → only PNG (give 2–8 frames or --sprite-sheet for an animated meme).")
    return 0


def _split(value):
    if not value:
        return None
    if isinstance(value, list):
        value = ",".join(value)
    return [v.strip() for v in value.replace("，", ",").split(",") if v.strip()]


def cmd_expressions(args: argparse.Namespace) -> int:
    """List the expression catalog (by category) with captions in a language."""
    lang = normalize_language(args.language)
    items = load_all_presets()
    if args.category:
        cats = set(_split(args.category) or [])
        items = [i for i in items if i.category in cats]
    if args.json:
        print(json.dumps([i.model_dump() for i in items], ensure_ascii=False, indent=2))
        return 0
    cats = list_categories()
    print(f"=== Expression catalog: {len(load_all_presets())} expressions, {len(cats)} categories (language={lang}) ===")
    by_cat = {}
    for it in items:
        by_cat.setdefault(it.category, []).append(it)
    for cid, group in by_cat.items():
        label = CATEGORY_LABELS.get(cid, {"zh": cid, "en": cid})
        print(f"\n[{cid}] {label['zh']} / {label['en']} ({len(group)})")
        for it in group:
            cap, missing = localized_caption(it, lang)
            bubble = f" 💬{it.bubble.shape}" if it.bubble else ""
            print(f"  {it.id:<24} {cap}{' *' if missing else ''}  <{it.text_layout}{bubble}> motion={it.motion.type}")
    return 0


def cmd_languages(args: argparse.Namespace) -> int:
    """Show supported languages and detected fonts."""
    rows = describe_font_support()
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    print("=== Supported caption languages ===")
    print("内置手写文案: " + ", ".join(BUILTIN_CAPTION_LANGUAGES) + "；其他语言通过 --captions-file 提供翻译")
    for r in rows:
        ok = "OK " if r["render_ok"] else "!! "
        font = Path(r["font"]).name if r["font"] else "未找到字体"
        builtin = "内置" if r["builtin_captions"] else "    "
        print(f"  {ok}{r['code']:<6} {r['name']:<18} {builtin} {r['direction']}  font={font} {r['note']}")
    return 0


def cmd_platforms(args: argparse.Namespace) -> int:
    """List supported social platforms and their export specs."""
    profiles = load_platform_profiles()
    if args.json:
        print(json.dumps([p.model_dump() for p in profiles.values()], ensure_ascii=False, indent=2))
        return 0
    print(f"=== Supported platforms ({len(profiles)}) ===")
    for p in profiles.values():
        print(f"\n* {p.id:<12} {p.display_name_zh} / {p.display_name} [{p.kind}, {p.region}]")
        print(f"    {p.description_zh}")
        for es in p.sets:
            parts = []
            if es.static:
                parts.append(f"static {es.static.format} {es.static.size[0]}x{es.static.size[1]} <= {es.static.max_bytes // 1000}KB")
            if es.animated:
                parts.append(f"animated {es.animated.format} {es.animated.size[0]}x{es.animated.size[1]} <= {es.animated.max_bytes // 1000}KB")
            print(f"    - {es.name}: " + "; ".join(parts))
        if p.showcase:
            print("    - showcase: " + ", ".join(f"{s.name}({s.kind} {s.size[0]}x{s.size[1]} {s.format})" for s in p.showcase))
    print("\nGroups: " + "; ".join(f"{k}={','.join(v)}" for k, v in platform_groups().items()) + "; all=全部")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    """Re-export existing master assets to more platforms (no image regeneration)."""
    job_p = Path(args.job)
    if not job_p.exists():
        print(f"Error: job.json not found: {job_p}", file=sys.stderr)
        return 2
    with job_p.open("r", encoding="utf-8") as f:
        job = JobConfig(**json.load(f))
    orchestrator = StickerOrchestrator(job=job, provider=FakeStickerProvider(), native_gif_provider=FakeStickerProvider())
    try:
        results = orchestrator.export_only(resolve_platforms(args.platforms) if args.platforms else None, force=args.force)
    except Exception as e:
        print(f"Export error: {e}", file=sys.stderr)
        return 4
    for pid, res in results.items():
        zp = f" → {res.zip_path}" if res.zip_path else ""
        print(f"[{res.status.upper():4}] {pid}: {len(res.files)} files, {len(res.showcase)} showcase{zp}")
        for w in res.warnings + res.skipped:
            print(f"       - {w}")
    return 0


def cmd_captions_template(args: argparse.Namespace) -> int:
    """Export a captions-file template for translating captions into any language."""
    lang = normalize_language(args.language)
    items = plan_expressions(count=args.count, strict_counts=False) if args.count else load_all_presets()
    data = translation_template(items, lang)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Captions template for {lang} written to {out} ({len(data)} expressions). Fill in caption/bubble texts, then pass --captions-file.")
    return 0


def _assemble_text_kwargs(args: argparse.Namespace) -> dict:
    return {
        "language": normalize_language(args.language),
        "bubble_text": args.bubble_text or "",
        "bubble_shape": args.bubble_shape or "round",
        "bubble_position": args.bubble_position,
        "bubble_animation": args.bubble_animation,
        "text_layout": args.text_layout,
    }


def cmd_assemble_gif(args: argparse.Namespace) -> int:
    """Assemble a WeChat 240x240 animated GIF (and optional static PNG) from Codex AI-generated
    2x2 sprite sheet or multi-pose keyframe images."""
    gif_out = Path(args.output)
    static_out = Path(args.static_output) if getattr(args, "static_output", None) else None
    font_path = getattr(args, "font", None) or get_default_font_path()

    try:
        if getattr(args, "sprite_sheet", None):
            sheet_p = Path(args.sprite_sheet)
            if not sheet_p.exists():
                print(f"Error: Sprite sheet not found: {sheet_p}", file=sys.stderr)
                return 2
            assemble_gif_from_sprite_sheet(
                sheet_path=sheet_p,
                gif_output_path=gif_out,
                caption=args.caption or "",
                style=args.style,
                static_output_path=static_out,
                font_path=font_path,
                frame_duration_ms=args.gif_duration,
                target_frames=args.gif_frames,
                **_assemble_text_kwargs(args),
            )
        elif getattr(args, "keyframes", None):
            kf_paths = [Path(p) for p in args.keyframes]
            for p in kf_paths:
                if not p.exists():
                    print(f"Error: Keyframe file not found: {p}", file=sys.stderr)
                    return 2
            assemble_gif_from_keyframe_files(
                frame_paths=kf_paths,
                gif_output_path=gif_out,
                caption=args.caption or "",
                style=args.style,
                static_output_path=static_out,
                font_path=font_path,
                frame_duration_ms=args.gif_duration,
                target_frames=args.gif_frames,
                **_assemble_text_kwargs(args),
            )
        else:
            print("Error: Provide either --sprite-sheet or --keyframes", file=sys.stderr)
            return 2

        optimize_gif(gif_out, max_bytes=500_000)
        if static_out and static_out.exists():
            optimize_png(static_out, max_bytes=500_000)
        print(f"Assembled animated GIF: {gif_out}")
        if static_out:
            print(f"Exported static PNG:    {static_out}")
        return 0
    except Exception as e:
        print(f"Assemble GIF error: {e}", file=sys.stderr)
        return 4


def main() -> None:
    parser = argparse.ArgumentParser(prog="wechat-sticker-maker", description="WeChat AI Sticker Maker CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # doctor
    subparsers.add_parser("doctor", help="Check local dependencies, fonts, and API environment")

    # styles
    p_styles = subparsers.add_parser("styles", help="List available built-in sticker style presets")
    p_styles.add_argument("--json", action="store_true", help="Output style presets as JSON")
    p_styles.add_argument("--region", help="Filter by series: 韩系/kr, 日系/jp, 中式/cn, 通用 (comma list)")

    # duo
    p_duo = subparsers.add_parser("duo", help="List 108 real-person two-person interaction presets (闺蜜 / 情侣 / 百合)")
    p_duo.add_argument("--category", help="Filter by duo category: 闺蜜/besties, 情侣/couple, 百合/yuri (comma list)")
    p_duo.add_argument("--language", default="zh-CN", help="Caption language: zh-CN, zh-TW, en, ja, ko")
    p_duo.add_argument("--json", action="store_true", help="Output duo presets as JSON")

    # plan
    p_plan = subparsers.add_parser("plan", help="Plan expressions and create job.json")
    p_plan.add_argument("--input", "-i", required=True, help="Path to input photo (Person A)")
    p_plan.add_argument("--partner", "-p", help="Optional path to second person's photo (Person B) for two-person duo stickers")
    p_plan.add_argument("--partner-facts", help="Optional comma-separated identity traits for Person B")
    p_plan.add_argument("--output", "-o", required=True, help="Output directory")
    p_plan.add_argument("--job-id", help="Job identifier")
    p_plan.add_argument("--mode", choices=["both", "static", "animated"], default="both")
    p_plan.add_argument("--count", type=int, default=16, help="8/16/24 for WeChat; 1-120 for other platforms")
    p_plan.add_argument("--style", default="real-cutout", help="Real-person sticker style ID (e.g. real-cutout, kr-gyaru-peace, jp-purikura-sweet, cn-hanfu-daily)")
    p_plan.add_argument("--language", default="zh-CN", help="Caption language: zh-CN, zh-TW, en, ja, ko, or 'auto' to match style region")
    p_plan.add_argument("--languages", help="Comma-separated list of languages to output separate 100%% single-language packs from one AI generation (e.g. zh-CN,en,ja,ko)")
    p_plan.add_argument("--text-layout", choices=["auto", "caption", "bubble", "both", "none"], default="auto")
    p_plan.add_argument("--bubble-shape", choices=["round", "oval", "thought", "shout", "rect", "heart", "whisper"])
    p_plan.add_argument("--bubble-animation", choices=["none", "pop", "typewriter", "bob"], default="none")
    p_plan.add_argument("--categories", help="Comma-separated categories (greeting,reply,meme,work,...)")
    p_plan.add_argument("--expressions", help="Comma-separated explicit expression ids")
    p_plan.add_argument("--duo-category", help="Duo interaction category: 闺蜜/besties, 情侣/couple, 百合/yuri (comma list)")
    p_plan.add_argument("--duo-ids", help="Explicit duo preset IDs (e.g. d01_bestie_cheek_selfie,d73_yuri_chin_lift_gaze)")
    p_plan.add_argument("--captions-file", help="JSON file with custom captions / translations")
    p_plan.add_argument("--pack-type", choices=["expressions", "memes", "mixed", "duo"], default="expressions", help="Expression stickers, meme/abstract pack, mixed, or two-person duo pack")
    p_plan.add_argument("--meme-templates", help="Comma list of meme template ids/aliases (claude,中国ip,封号,m14 ...)")
    p_plan.add_argument("--meme-categories", help="ai-meme,ban-warning,chat-ui,abstract,classic-meme,work-life")
    p_plan.add_argument("--meme-text", action="append", help="Override meme text: TEMPLATE=TEXT (repeatable)")
    p_plan.add_argument("--platforms", default="wechat", help="Comma list: wechat,qq,douyin,xiaohongshu,soul,weibo,telegram,whatsapp,line,kakaotalk,discord,slack,imessage,signal,viber,giphy,instagram,tiktok,x,facebook,generic | groups china,global-chat,social | all")
    p_plan.add_argument("--master-size", type=int, default=720)
    p_plan.add_argument("--pack-title", help="Pack title used on covers/showcase pages")
    p_plan.add_argument(
        "--animation-backend",
        choices=["auto", "keyframes", "sprite-sheet", "native-gif"],
        default="auto",
    )
    p_plan.add_argument("--gif-frames", type=int, default=8)
    p_plan.add_argument("--gif-duration", type=int, default=180)
    p_plan.add_argument("--profile", default="wechat-conservative-2026-11")
    p_plan.add_argument("--font", help="Path to Chinese TTF/OTF font")
    p_plan.add_argument("--subject-type", default="human-portrait", help="Subject type (default: human-portrait, real-person only)")
    p_plan.add_argument("--matting", choices=["auto", "color", "rembg"], default="auto", help="Background removal engine: color flood-fill or neural rembg")
    p_plan.add_argument(
        "--resume",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Resume from existing raw keyframes in work/raw_static & work/raw_gif",
    )
    p_plan.add_argument(
        "--allow-cloud-upload",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Allow uploading reference image to cloud provider",
    )
    p_plan.add_argument(
        "--keep-source",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Retain normalized copy of source photo in work directory",
    )

    # generate
    p_gen = subparsers.add_parser("generate", help="Run generation pipeline")
    p_gen.add_argument("--job", "-j", required=True, help="Path to job.json")
    p_gen.add_argument("--provider", choices=["auto", "fake", "openai", "gemini", "ark"], default="auto")
    p_gen.add_argument("--animation-backend", choices=["auto", "keyframes", "sprite-sheet", "native-gif"])
    p_gen.add_argument("--style", help="Override style preset ID or custom style JSON path")
    p_gen.add_argument("--language", help="Override caption language (or 'auto' to match style region)")
    p_gen.add_argument("--languages", help="Comma-separated languages for zero-extra-cost multi-pack output (e.g. zh-CN,en,ja,ko)")
    p_gen.add_argument("--platforms", help="Override target platforms (comma list / group / all)")
    p_gen.add_argument("--sample", action="store_true", help="Run sample-first mode (2 static + 1 animated)")
    p_gen.add_argument("--max-parallel", type=int, help="Override maximum parallel item workers")
    p_gen.add_argument("--matting", choices=["auto", "color", "rembg"], help="Override background removal engine")
    p_gen.add_argument("--resume", action=argparse.BooleanOptionalAction, default=None, help="Resume from existing raw keyframes")

    # regenerate
    p_regen = subparsers.add_parser("regenerate", help="Regenerate a specific single item")
    p_regen.add_argument("--job", "-j", required=True, help="Path to job.json")
    p_regen.add_argument("--item", required=True, help="Expression item ID to regenerate (e.g. 05_shy)")
    p_regen.add_argument("--provider", choices=["auto", "fake", "openai", "gemini", "ark"], default="auto")

    # validate
    p_val = subparsers.add_parser("validate", help="Validate assets in output directory")
    p_val.add_argument("--output", "-o", required=True, help="Output directory containing assets")
    p_val.add_argument("--profile", default="wechat-conservative-2026-11")

    # package
    p_pkg = subparsers.add_parser("package", help="Create ZIP archives for platform submission")
    p_pkg.add_argument("--output", "-o", required=True, help="Output directory containing assets")
    p_pkg.add_argument(
        "--strict",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enforce passing QA report before creating ZIPs",
    )
    p_pkg.add_argument("--profile", default="wechat-conservative-2026-11")

    # catalog / language / platform discovery
    p_expr = subparsers.add_parser("expressions", help="List expression catalog by category")
    p_expr.add_argument("--language", default="zh-CN")
    p_expr.add_argument("--category", help="Filter by category (comma list)")
    p_expr.add_argument("--json", action="store_true")
    p_lang = subparsers.add_parser("languages", help="List supported caption languages and detected fonts")
    p_lang.add_argument("--json", action="store_true")
    p_plat = subparsers.add_parser("platforms", help="List supported social platforms and export specs")
    p_plat.add_argument("--json", action="store_true")
    p_exp = subparsers.add_parser("export", help="Re-export generated masters to more platforms")
    p_exp.add_argument("--job", "-j", required=True)
    p_exp.add_argument("--platforms", help="Comma list / group / all (default: job platforms)")
    p_exp.add_argument("--force", action="store_true", help="Overwrite existing exported files")
    p_ct = subparsers.add_parser("captions-template", help="Export a captions translation template for any language")
    p_ct.add_argument("--language", required=True)
    p_ct.add_argument("--output", "-o", required=True)
    p_ct.add_argument("--count", type=int, help="Only the first N planned expressions (default: whole catalog)")

    p_memes = subparsers.add_parser("memes", help="List meme / abstract templates (梗图模板)")
    p_memes.add_argument("--language", default="zh-CN")
    p_memes.add_argument("--category")
    p_memes.add_argument("--json", action="store_true")
    p_meme = subparsers.add_parser("meme", help="Render one meme template over character image(s)")
    p_meme.add_argument("--template", "-t", required=True, help="Template id or alias (claude, 中国ip, 封号, m14 ...)")
    p_meme.add_argument("--image", "-i", action="append", help="Character image(s); 2–8 images = animation frames")
    p_meme.add_argument("--sprite-sheet", help="2x2 AI action sheet for a fully animated meme")
    p_meme.add_argument("--output", "-o", help="Output GIF path (PNG saved next to it)")
    p_meme.add_argument("--static-output", help="Output PNG path")
    p_meme.add_argument("--text", help="Replace the meme's main text")
    p_meme.add_argument("--language", default="zh-CN")
    p_meme.add_argument("--style", default="real-cutout")
    p_meme.add_argument("--size", type=int, default=240)
    p_meme.add_argument("--color", help="Override accent colour (spinner/stamp/sign), e.g. #D97757")
    p_meme.add_argument("--font")
    p_meme.add_argument("--gif-frames", type=int, default=8)
    p_meme.add_argument("--gif-duration", type=int, default=150)

    # assemble-gif (for Codex built-in image generation workflow)
    p_asm = subparsers.add_parser(
        "assemble-gif",
        help="Slice & align AI-generated 2x2 sprite sheet or multi-pose keyframes into a 240x240 WeChat GIF",
    )
    p_asm_group = p_asm.add_mutually_exclusive_group(required=True)
    p_asm_group.add_argument("--sprite-sheet", help="Path to 2x2 4-frame action sprite sheet PNG generated by Codex")
    p_asm_group.add_argument("--keyframes", nargs="+", help="Paths to 2-8 sequential keyframe PNGs generated by Codex")
    p_asm.add_argument("--output", "-o", required=True, help="Output 240x240 GIF file path")
    p_asm.add_argument("--static-output", help="Optional output 240x240 static PNG path (exports Frame 1)")
    p_asm.add_argument("--caption", default="", help="Chinese caption to overlay at the bottom")
    p_asm.add_argument("--style", default="real-cutout", help="Real-person style preset ID (e.g. real-cutout, real-variety-meme, real-bobblehead)")
    p_asm.add_argument("--font", help="Path to Chinese TTF/OTF font")
    p_asm.add_argument("--gif-frames", type=int, default=8, help="Target loop frame count")
    p_asm.add_argument("--gif-duration", type=int, default=150, help="Frame duration in ms")
    p_asm.add_argument("--language", default="zh-CN", help="Text language for font selection / wrapping")
    p_asm.add_argument("--bubble-text", help="Speech bubble text")
    p_asm.add_argument("--bubble-shape", choices=["round", "oval", "thought", "shout", "rect", "heart", "whisper"])
    p_asm.add_argument("--bubble-position", choices=["auto", "top-left", "top-right"], default="auto")
    p_asm.add_argument("--bubble-animation", choices=["none", "pop", "typewriter", "bob"], default="none")
    p_asm.add_argument("--text-layout", choices=["auto", "caption", "bubble", "both", "none"], default="auto")

    args = parser.parse_args()
    setup_logging()

    cmd_map = {
        "doctor": cmd_doctor,
        "styles": cmd_styles,
        "duo": cmd_duo,
        "plan": cmd_plan,
        "generate": cmd_generate,
        "regenerate": cmd_regenerate,
        "validate": cmd_validate,
        "package": cmd_package,
        "assemble-gif": cmd_assemble_gif,
        "expressions": cmd_expressions,
        "languages": cmd_languages,
        "platforms": cmd_platforms,
        "export": cmd_export,
        "captions-template": cmd_captions_template,
        "memes": cmd_memes,
        "meme": cmd_meme,
    }

    exit_code = cmd_map[args.command](args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
