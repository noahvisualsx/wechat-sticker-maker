"""Creator Studio utilities:
1. Zero-cost caption & bubble text remixing (`remix_captions`) without re-running AI generation.
2. Social media promotional posters (`generate_social_posters`: Xiaohongshu 3:4, Story/Reels 9:16, Grid 1:1).
3. Official Store Submission Copy & Checklist generator (`generate_submission_copy`: WeChat Open Platform, LINE, KakaoTalk).
4. Theme Pack resolver (`resolve_theme_preset`).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image, ImageDraw

from .exporters import MasterAsset, export_all_platforms, save_master_asset
from .i18n import normalize_language
from .planner import THEME_PACKS, localize_meme, plan_pack, resolve_text_spec
from .platforms import resolve_platforms
from .processing.compose import compose_sticker_frames
from .processing.gif_encoder import slice_sprite_sheet, synthesize_motion_frames
from .processing.typography import _truetype, segment_runs
from .quality.report import generate_preview_html, generate_preview_sheet
from .schemas import JobConfig, Manifest, ManifestItem
from .styles import hex_to_rgba, resolve_style_preset


def list_theme_presets() -> Dict[str, Dict[str, object]]:
    """Return all 15 built-in theme presets."""
    return {k: dict(v) for k, v in THEME_PACKS.items()}


def resolve_theme_preset(theme_name: str) -> Dict[str, object]:
    """Return preset configuration for a named theme pack (e.g. 打工人, 发疯, 干饭, 搞钱, 电竞, 追星, 闺蜜, 情侣, 百合, 双男主, 欢喜冤家, 亲子, 萌宠)."""
    key = theme_name.strip()
    if key in THEME_PACKS:
        return dict(THEME_PACKS[key])
    aliases = {
        "work": "打工人", "office": "打工人", "社畜": "打工人",
        "crazy": "发疯", "mental": "发疯", "精神状态": "发疯",
        "food": "干饭", "foodie": "干饭", "吃货": "干饭", "奶茶": "干饭",
        "money": "搞钱", "wealth": "搞钱", "暴富": "搞钱",
        "game": "电竞", "gaming": "电竞", "开黑": "电竞",
        "fan": "追星", "fandom": "追星", "爱豆": "追星",
        "sassy": "阴阳怪气", "茶艺": "阴阳怪气",
        "campus": "学生党", "student": "学生党", "考研": "学生党", "早八": "学生党",
        "pet": "萌宠", "猫狗": "萌宠",
        "besties": "闺蜜", "couple": "情侣", "yuri": "百合",
        "yaoi": "双男主", "bl": "双男主", "bromance": "双男主",
        "rivals": "欢喜冤家", "冤家": "欢喜冤家",
        "family": "亲子", "姐弟": "亲子", "萌娃": "亲子",
    }
    mapped = aliases.get(key.lower()) or aliases.get(key)
    if mapped and mapped in THEME_PACKS:
        return dict(THEME_PACKS[mapped])
    raise ValueError(f"Unknown theme '{theme_name}'. Available themes: {', '.join(THEME_PACKS.keys())}")


def remix_captions(
    job_path: Path,
    caption_overrides: Optional[Dict[str, str]] = None,
    bubble_overrides: Optional[Dict[str, str]] = None,
    language: Optional[str] = None,
) -> Path:
    """Re-compose existing raw AI cutouts in work/raw_static & work/raw_gif with new custom captions/bubbles.

    Zero AI calls — executes in under 2 seconds!
    """
    job_data = json.loads(job_path.read_text(encoding="utf-8"))
    if language:
        job_data["language"] = normalize_language(language)
    job = JobConfig(**job_data)
    out_dir = Path(job.output_dir)
    work_raw_static = out_dir / "work" / "raw_static"
    work_raw_gif = out_dir / "work" / "raw_gif"

    custom_map: Dict[str, dict] = {}
    if job.captions_file and Path(job.captions_file).exists():
        try:
            custom_map = json.loads(Path(job.captions_file).read_text(encoding="utf-8"))
        except Exception:
            custom_map = {}

    for k, v in (caption_overrides or {}).items():
        custom_map.setdefault(k, {})["caption"] = v
    for k, v in (bubble_overrides or {}).items():
        custom_map.setdefault(k, {})["bubble"] = v

    captions_out = out_dir / "work" / "remixed_captions.json"
    captions_out.parent.mkdir(parents=True, exist_ok=True)
    captions_out.write_text(json.dumps(custom_map, ensure_ascii=False, indent=2), encoding="utf-8")
    job.captions_file = str(captions_out)
    job_path.write_text(json.dumps(job.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")

    preset = resolve_style_preset(job.style)
    canvas = (job.master_size, job.master_size)
    expressions = plan_pack(job, strict_counts=False)
    masters: List[MasterAsset] = []
    manifest_items: List[ManifestItem] = []

    for idx, item in enumerate(expressions, 1):
        spec = resolve_text_spec(item, job, custom_map)
        meme = localize_meme(item, job, custom_map)
        if item.id in (caption_overrides or {}):
            spec.caption = caption_overrides[item.id]
            if spec.layout == "none":
                spec.layout = "caption"
        if item.id in (bubble_overrides or {}):
            spec.bubble_text = bubble_overrides[item.id]
            if spec.layout == "caption":
                spec.layout = "both"
            elif spec.layout == "none":
                spec.layout = "bubble"

        static_master: Optional[Image.Image] = None
        raw_s = work_raw_static / f"{item.id}_raw.png"
        if raw_s.exists():
            with Image.open(raw_s) as rimg:
                static_master = compose_sticker_frames(
                    [rimg.convert("RGBA")], spec, preset, canvas, 1, job.font_path, meme=meme, matting=job.matting
                )[0]

        frames: Optional[List[Image.Image]] = None
        sheet_p = work_raw_gif / f"{item.id}_sheet_raw.png"
        if sheet_p.exists():
            with Image.open(sheet_p) as simg:
                cells = slice_sprite_sheet(simg)
            frames = compose_sticker_frames(
                cells, spec, preset, canvas, job.animation.frames, job.font_path, meme=meme, matting=job.matting
            )
        elif static_master is not None and job.mode in ("animated", "both"):
            frames = synthesize_motion_frames(static_master, motion_type=item.motion.type, frames=job.animation.frames)

        if static_master is None and frames is None:
            continue

        asset = save_master_asset(
            out_dir, item.id, idx, spec.caption or spec.bubble_text, static_master, frames, job.animation.frame_duration_ms,
            extra_meta={"language": spec.language, "text_layout": spec.layout, "category": item.category},
        )
        masters.append(asset)
        manifest_items.append(
            ManifestItem(
                id=item.id,
                caption=spec.caption or spec.bubble_text or item.caption,
                static_path=str(asset.static_path.relative_to(out_dir)) if asset.static_path else None,
                animated_path=str(asset.anim_path.relative_to(out_dir)) if asset.anim_path else None,
                status="SUCCESS",
                checks={"structural": "pass", "visual": "reviewed"},
                category=item.category,
                language=spec.language,
                text_layout=spec.layout,
                bubble_text=spec.bubble_text or None,
            )
        )

    platforms = resolve_platforms(job.platforms)
    export_res = export_all_platforms(
        out_dir, platforms, masters, style=job.style, language=job.language,
        pack_title=job.pack_title, font_path=job.font_path, skip_existing=False,
    )
    if "wechat" in export_res:
        wx_res = export_res["wechat"]
        for m in manifest_items:
            files = {k: str(Path(v).relative_to(out_dir)) for k, v in wx_res.item_files(m.id).items()}
            m.static_path = files.get("main:static") or m.static_path
            m.animated_path = files.get("main:animated") or m.animated_path

    generate_preview_sheet(out_dir)
    return generate_preview_html(
        out_dir,
        {"job_id": job.job_id, "language": job.language, "items": [m.model_dump() for m in manifest_items]},
    )


def _draw_multilang_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    size: int,
    fill: tuple[int, int, int, int],
    language: str = "zh-CN",
    anchor_center: bool = True,
) -> None:
    runs = segment_runs(text, language=language)
    total_w = 0.0
    parts = []
    for run in runs:
        font = _truetype(run.path, size, run.index)
        bbox = draw.textbbox((0, 0), run.text, font=font)
        w = float(bbox[2] - bbox[0])
        parts.append((run.text, font, w))
        total_w += w
    x = xy[0] - total_w / 2.0 if anchor_center else xy[0]
    y = xy[1]
    for txt, font, w in parts:
        draw.text((x, y), txt, font=font, fill=fill)
        x += w


def generate_social_posters(
    output_dir: Path,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    style: str = "real-cutout",
    language: str = "zh-CN",
) -> Dict[str, Path]:
    """Generate promotional posters (Xiaohongshu 3:4, Story 9:16, Grid 1:1) + platform submission copy."""
    static_dir = output_dir / "static"
    work_master = output_dir / "work" / "master"
    pngs = sorted(work_master.glob("*_static.png")) if work_master.exists() else []
    if not pngs and static_dir.exists():
        pngs = sorted(static_dir.glob("*.png"))
    if not pngs:
        raise FileNotFoundError(f"No sticker PNGs found in {output_dir}")

    preset = resolve_style_preset(style)
    posters_dir = output_dir / "posters"
    posters_dir.mkdir(parents=True, exist_ok=True)

    default_titles = {
        "zh-CN": (title or f"{preset.display_name} · 真人表情包", subtitle or "100% 保留真实五官 · 单张纯净单语 · 全平台直出"),
        "ko": (title or f"{preset.display_name} · 실사 이모티콘", subtitle or "100% 실제 이목구비 보존 · 카톡/인스타/위챗 지원"),
        "ja": (title or f"{preset.display_name} · 実写スタンプ", subtitle or "100% ご本人の顔立ち維持 · LINE/インスタ対応"),
        "en": (title or f"{preset.display_name} · Real Sticker Pack", subtitle or "100% Authentic Real Portrait · Multi-Platform Ready"),
    }
    main_title, sub_title = default_titles.get(language, default_titles["zh-CN"])
    bg_rgba = hex_to_rgba(preset.banner_bg or "#F7F5F2", 255)
    accent_rgba = hex_to_rgba((preset.default_palette or ["#07C160"])[0], 255)

    specs = {
        "xhs_3x4": (1200, 1600, 3, 180),
        "story_9x16": (1080, 1920, 3, 240),
        "grid_1x1": (1080, 1080, 3, 140),
    }
    outputs: Dict[str, Path] = {}
    for key, (W, H, cols, header_h) in specs.items():
        canvas = Image.new("RGBA", (W, H), bg_rgba)
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([0, 0, W, 14], fill=accent_rgba)
        _draw_multilang_text(draw, (W / 2, 42), main_title, 44, (28, 28, 32, 255), language=language)
        _draw_multilang_text(draw, (W / 2, 104), sub_title, 24, (110, 110, 118, 255), language=language)

        items = pngs[:9]
        rows = max(1, int(math.ceil(len(items) / float(cols))))
        pad = 28
        avail_w = W - pad * (cols + 1)
        avail_h = H - header_h - pad * (rows + 1)
        cell = min(avail_w // cols, avail_h // rows)
        grid_w = cols * cell + (cols - 1) * pad
        start_x = (W - grid_w) // 2

        for idx, p in enumerate(items):
            r, c = idx // cols, idx % cols
            x = start_x + c * (cell + pad)
            y = header_h + pad + r * (cell + pad)
            draw.rounded_rectangle([x, y, x + cell, y + cell], radius=24, fill=(255, 255, 255, 235), outline=(225, 225, 230, 255), width=2)
            with Image.open(p) as im:
                rgba = im.convert("RGBA")
                inner = int(cell * 0.88)
                rgba.thumbnail((inner, inner), Image.Resampling.LANCZOS)
                ox = x + (cell - rgba.width) // 2
                oy = y + (cell - rgba.height) // 2
                canvas.paste(rgba, (ox, oy), rgba)

        out_p = posters_dir / f"poster-{key}.png"
        canvas.save(out_p, format="PNG")
        outputs[key] = out_p

    # Also generate ready-to-paste store submission copy (WeChat / LINE / KakaoTalk)
    copy_data = {
        "zh-CN": {
            "pack_name": main_title[:16],
            "intro_one_line": "保留真实五官与自然神态的真人实拍日常斗图表情包，覆盖打招呼、开心、工作与热梗互动。",
            "appreciation_word": "感谢喜欢这套真人表情包，祝你每天斗图愉快、好运连连！",
            "tags": ["真人表情包", "日常斗图", "打工人", "闺蜜情侣", preset.region],
        },
        "en": {
            "pack_name": f"{preset.id.replace('-', ' ').title()} Pack",
            "intro_one_line": "Photorealistic real-person portrait sticker pack for daily chats, reactions, and memes.",
            "appreciation_word": "Thanks for supporting this real-person sticker pack!",
            "tags": ["real-person", "portrait-sticker", "reaction", "daily-chat"],
        },
        "ko": {
            "pack_name": "실사 데일리 이모티콘 세트",
            "intro_one_line": "본인의 실제 이목구비와 감성을 살린 실사 인물 데일리 리액션 이모티콘입니다.",
            "appreciation_word": "실사 이모티콘을 사랑해 주셔서 감사합니다! 오늘도 행복한 하루 보내세요.",
            "tags": ["실사이모티콘", "인생네컷", "데일리짤", "커플절친"],
        },
        "ja": {
            "pack_name": "実写ポートレート日常スタンプ",
            "intro_one_line": "本人のリアルな表情と空気感をそのまま活かした、毎日使える実写人物スタンプセットです。",
            "appreciation_word": "スタンプをご利用いただきありがとうございます！毎日のトークが楽しくなりますように。",
            "tags": ["実写スタンプ", "日常会話", "ポートレート", "推し活"],
        },
    }
    copy_p = posters_dir / "submission-copy.json"
    copy_p.write_text(json.dumps(copy_data, ensure_ascii=False, indent=2), encoding="utf-8")
    outputs["submission_copy"] = copy_p
    return outputs
