"""Export master sticker assets to every selected social platform.

Master assets (rendered once at ``JobConfig.master_size``, default 720px):
    work/master/{id}_static.png      composed static sticker (character + caption/bubble)
    work/master/{id}_anim.webp       lossless animated master (all frames, exact alpha)
    work/master/{id}_meta.json       frame duration, caption, language, ...

From these, each platform profile in ``references/platform-profiles.json`` produces its own files:
    WeChat (legacy layout)   static/ animated/ thumbnails/ platform/   (+ static-pack.zip / animated-pack.zip)
    other platforms          exports/<platform>/<set>/{static,animated}/..., assets/, showcase/, README.md,
                             qa-report.md/json, and exports/<platform>-pack.zip
"""

from __future__ import annotations

import json
import logging
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from PIL import Image, ImageSequence

from .i18n import localized_count_label, localized_pack_title
from .platforms import ExportSet, FormatSpec, PlatformProfileSpec, load_platform_profiles, resolve_platforms
from .processing.alpha import apply_safe_margin, remove_matte_background
from .processing.encoders import (
    ExportUnavailable,
    fit_to_canvas,
    probe_video,
    save_animated,
    save_mp4,
    save_static,
)
from .processing.resize import create_banner
from .processing.showcase import (
    make_cover,
    make_grid_pages,
    make_nine_grid,
    make_single_pages,
    make_story_pages,
    make_video_grid_frames,
)
from .styles import resolve_style_preset

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Master asset storage
# ---------------------------------------------------------------------------


@dataclass
class MasterAsset:
    item_id: str
    index: int
    caption: str = ""
    static_path: Optional[Path] = None
    anim_path: Optional[Path] = None
    frame_duration_ms: int = 150

    def load_static(self) -> Optional[Image.Image]:
        if self.static_path and self.static_path.exists():
            with Image.open(self.static_path) as img:
                return img.convert("RGBA")
        return None

    def load_frames(self) -> List[Image.Image]:
        if self.anim_path and self.anim_path.exists():
            with Image.open(self.anim_path) as img:
                return [f.convert("RGBA") for f in ImageSequence.Iterator(img)]
        return []

    def preview(self) -> Optional[Image.Image]:
        st = self.load_static()
        if st is not None:
            return st
        frames = self.load_frames()
        return frames[0] if frames else None


def master_dir(output_dir: Path) -> Path:
    return output_dir / "work" / "master"


def save_master_asset(
    output_dir: Path,
    item_id: str,
    index: int,
    caption: str,
    static_img: Optional[Image.Image],
    frames: Optional[Sequence[Image.Image]],
    frame_duration_ms: int,
    extra_meta: Optional[dict] = None,
) -> MasterAsset:
    d = master_dir(output_dir)
    d.mkdir(parents=True, exist_ok=True)
    asset = MasterAsset(item_id, index, caption, frame_duration_ms=frame_duration_ms)
    if static_img is not None:
        p = d / f"{item_id}_static.png"
        tmp = p.with_name(p.name + ".tmp")
        static_img.save(tmp, format="PNG", compress_level=6)
        tmp.replace(p)
        asset.static_path = p
    if frames:
        p = d / f"{item_id}_anim.webp"
        tmp = p.with_name(p.name + ".tmp")
        fr = [f.convert("RGBA") for f in frames]
        fr[0].save(
            tmp, format="WEBP", save_all=True, append_images=fr[1:], duration=frame_duration_ms,
            loop=0, lossless=True, exact=True, method=0, quality=10,
        )
        tmp.replace(p)
        asset.anim_path = p
    meta = {
        "id": item_id,
        "index": index,
        "caption": caption,
        "frame_duration_ms": frame_duration_ms,
        "static": asset.static_path.name if asset.static_path else None,
        "animated": asset.anim_path.name if asset.anim_path else None,
        **(extra_meta or {}),
    }
    (d / f"{item_id}_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return asset


def load_master_assets(output_dir: Path, item_ids: Optional[Sequence[str]] = None) -> List[MasterAsset]:
    d = master_dir(output_dir)
    if not d.exists():
        return []
    assets: List[MasterAsset] = []
    for meta_path in sorted(d.glob("*_meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if item_ids is not None and meta["id"] not in item_ids:
            continue
        assets.append(
            MasterAsset(
                meta["id"],
                int(meta.get("index", 0)),
                meta.get("caption", ""),
                (d / meta["static"]) if meta.get("static") else None,
                (d / meta["animated"]) if meta.get("animated") else None,
                int(meta.get("frame_duration_ms", 150)),
            )
        )
    order = {iid: i for i, iid in enumerate(item_ids)} if item_ids else None
    assets.sort(key=lambda a: order.get(a.item_id, a.index) if order else a.index)
    return assets


# ---------------------------------------------------------------------------
# Platform export
# ---------------------------------------------------------------------------


@dataclass
class ExportedFile:
    path: Path
    spec: FormatSpec
    kind: str  # static | animated | thumbnail | asset | showcase
    item_id: Optional[str] = None
    set_name: Optional[str] = None


@dataclass
class PlatformExportResult:
    platform: str
    base_dir: Path
    files: List[ExportedFile] = field(default_factory=list)
    showcase: List[Path] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    zip_path: Optional[Path] = None
    report_path: Optional[Path] = None
    status: str = "pass"

    def item_files(self, item_id: str) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for f in self.files:
            if f.item_id == item_id:
                out[f"{f.set_name}:{f.kind}"] = str(f.path)
        return out


def _platform_base(output_dir: Path, profile: PlatformProfileSpec) -> Path:
    return output_dir if profile.legacy_root_layout else output_dir / "exports" / profile.id


def _set_paths(base: Path, profile: PlatformProfileSpec, export_set: ExportSet, kind: str, stem: str, ext: str) -> Path:
    if profile.legacy_root_layout and export_set.name == "main":
        sub = {"static": "static", "animated": "animated", "thumbnail": "thumbnails"}[kind]
        return base / sub / f"{stem}.{ext}"
    sub = {"static": "static", "animated": "animated", "thumbnail": "thumbnails"}[kind]
    return base / export_set.name / sub / f"{stem}.{ext}"


def _fit_cached(img: Image.Image, spec: FormatSpec, cache: Optional[dict], key_prefix: str) -> Image.Image:
    out_size = spec.output_size(img.size)
    key = (key_prefix, out_size, spec.margin_px, spec.transparent, spec.background)
    if cache is not None and key in cache:
        return cache[key]
    canvas = fit_to_canvas(img, out_size, spec.margin_px, spec.transparent, spec.background)
    if spec.transparent and spec.margin_px >= 2:
        canvas = apply_safe_margin(canvas, min(spec.margin_px, 2))
    if cache is not None:
        cache[key] = canvas
    return canvas


def _render_static(img: Image.Image, spec: FormatSpec, path: Path, cache: Optional[dict] = None) -> None:
    canvas = _fit_cached(img, spec, cache, "static")
    save_static(canvas, path, spec.format if spec.format != "apng" else "png", spec.max_bytes, spec.background)


def _render_animated(frames: List[Image.Image], spec: FormatSpec, path: Path, frame_ms: int, cache: Optional[dict] = None) -> None:
    fitted = [_fit_cached(f, spec, cache, f"frame{i}") for i, f in enumerate(frames)]
    save_animated(
        fitted, path, spec.format, frame_ms, spec.max_bytes, spec.loop,
        spec.max_duration_ms, spec.max_fps, spec.min_frame_ms, spec.min_frames, spec.max_frames,
    )


def _anchor_image(output_dir: Path) -> Optional[Image.Image]:
    p = output_dir / "work" / "character-anchor.png"
    if not p.exists():
        return None
    with Image.open(p) as img:
        cleaned = remove_matte_background(img.convert("RGBA"))
    bbox = cleaned.getchannel("A").getbbox()
    return cleaned.crop(bbox) if bbox else cleaned


def _export_item_files(
    base: Path,
    profile: PlatformProfileSpec,
    asset: MasterAsset,
    static_img: Optional[Image.Image],
    frames: List[Image.Image],
    result: PlatformExportResult,
    skip_existing: bool,
    cache: Optional[dict] = None,
) -> None:
    stem = profile.file_stem(asset.item_id, asset.index)
    for es in profile.sets:
        jobs: List[Tuple[str, FormatSpec]] = []
        if es.static and static_img is not None:
            jobs.append(("static", es.static))
        if es.animated and frames:
            jobs.append(("animated", es.animated))
        if es.thumbnail and (static_img is not None or frames):
            jobs.append(("thumbnail", es.thumbnail))
        for kind, spec in jobs:
            path = _set_paths(base, profile, es, kind, stem, spec.extension)
            if not (skip_existing and path.exists()):
                try:
                    if kind == "animated":
                        _render_animated(frames, spec, path, asset.frame_duration_ms, cache)
                    else:
                        src = static_img if static_img is not None else frames[0]
                        _render_static(src, spec, path, cache if static_img is not None else None)
                except ExportUnavailable as e:
                    result.skipped.append(f"{path.name}: {e}")
                    continue
                except Exception as e:  # keep exporting other files
                    logger.exception("Export failed for %s", path)
                    result.warnings.append(f"{path.name}: export error {e}")
                    continue
            result.files.append(ExportedFile(path, spec, kind, asset.item_id, es.name))


def _downscale(img: Image.Image, max_side: int) -> Image.Image:
    if max(img.size) <= max_side:
        return img
    s = max_side / float(max(img.size))
    return img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.Resampling.LANCZOS)


def _finish_platform(
    output_dir: Path,
    profile: PlatformProfileSpec,
    result: PlatformExportResult,
    masters: Sequence[MasterAsset],
    previews: List[Image.Image],
    animations: List[List[Image.Image]],
    style: str,
    language: str,
    title: str,
    font_path: Optional[str],
    skip_existing: bool,
    with_showcase: bool,
    anchor: Optional[Image.Image],
) -> None:
    base = result.base_dir
    # Platform pack assets (cover, icon, tray icon, tab, banner, main animation ...)
    for pa in profile.assets:
        if profile.legacy_root_layout:
            path = base / "platform" / f"{pa.name}.{pa.spec.extension}"
        else:
            path = base / "assets" / f"{pa.name}.{pa.spec.extension}"
        if skip_existing and path.exists():
            result.files.append(ExportedFile(path, pa.spec, "asset"))
            continue
        try:
            if pa.source == "banner":
                src = anchor if anchor is not None else (previews[0] if previews else None)
                if src is None:
                    continue
                banner = create_banner(src, tuple(pa.spec.size), style=style).convert("RGB")
                save_static(banner, path, "png" if pa.spec.format == "png" else pa.spec.format, pa.spec.max_bytes)
            elif pa.source == "first_animated":
                first_anim = animations[0] if animations else None
                if not first_anim:
                    continue
                _render_animated(first_anim, pa.spec, path, masters[0].frame_duration_ms if masters else 150)
            else:
                src = anchor if (pa.source == "anchor" and anchor is not None) else (previews[0] if previews else None)
                if src is None:
                    continue
                _render_static(src, pa.spec, path)
            result.files.append(ExportedFile(path, pa.spec, "asset"))
        except ExportUnavailable as e:
            result.skipped.append(f"{path.name}: {e}")

    if with_showcase and profile.showcase and previews:
        sc_dir = base / "showcase"
        for sc in profile.showcase:
            try:
                written = _render_showcase(sc, sc_dir, previews, animations, masters, style, language, title, font_path, skip_existing)
                result.showcase.extend(written)
            except ExportUnavailable as e:
                result.skipped.append(f"showcase {sc.name}: {e}")

    if not profile.legacy_root_layout:
        _write_platform_readme(base, profile, result, len(masters), language)


def export_platform(
    output_dir: Path,
    profile: PlatformProfileSpec,
    masters: Sequence[MasterAsset],
    style: str = "real-cutout",
    language: str = "zh-CN",
    pack_title: Optional[str] = None,
    font_path: Optional[str] = None,
    skip_existing: bool = True,
    with_showcase: bool = True,
) -> PlatformExportResult:
    """Export one platform (convenience wrapper around :func:`export_all_platforms`)."""
    results = export_all_platforms(
        output_dir, [profile.id], masters, style, language, pack_title, font_path,
        skip_existing, package=False, with_showcase=with_showcase, validate=False,
    )
    return results[profile.id]


def _render_showcase(sc, sc_dir: Path, previews, animations, masters, style, language, title, font_path, skip_existing) -> List[Path]:
    preset = resolve_style_preset(style)
    written: List[Path] = []
    ext = sc.format

    def save_pages(pages: List[Image.Image], prefix: str) -> None:
        for i, page in enumerate(pages, 1):
            p = sc_dir / f"{prefix}_{i:02d}.{ext}"
            if not (skip_existing and p.exists()):
                save_static(page, p, "jpg" if ext == "jpg" else "png", 8_000_000, preset.banner_bg)
            written.append(p)

    if sc.kind == "cover":
        save_pages([make_cover(tuple(sc.size), previews, title, localized_count_label(language, len(previews)), preset, language, font_path)], sc.name)
    elif sc.kind == "grid":
        save_pages(make_grid_pages(tuple(sc.size), previews, sc.cols, sc.rows, title, preset, language, font_path), sc.name)
    elif sc.kind == "single":
        save_pages(make_single_pages(tuple(sc.size), previews, preset, sc.max_items), sc.name)
    elif sc.kind == "story":
        save_pages(make_story_pages(tuple(sc.size), previews, title, preset, language, font_path, sc.max_items), sc.name)
    elif sc.kind == "nine_grid":
        save_pages(make_nine_grid(tuple(sc.size), previews, preset), sc.name)
    elif sc.kind == "video_grid":
        anims = animations or [[p] for p in previews]
        if not animations:
            return written  # no animated masters → no video
        per = sc.cols * sc.rows
        frame_ms = masters[0].frame_duration_ms if masters else 150
        for page in range(max(1, (len(anims) + per - 1) // per)):
            p = sc_dir / f"{sc.name}_{page + 1:02d}.mp4"
            if not (skip_existing and p.exists()):
                frames = make_video_grid_frames(tuple(sc.size), anims[page * per:(page + 1) * per], sc.cols, sc.rows, title, preset, language, font_path)
                save_mp4(frames, p, frame_ms, sc.seconds, preset.banner_bg)
            written.append(p)
    return written


_KIND_ZH = {
    "sticker-store": "表情商店 / 贴纸平台",
    "chat-app": "聊天软件自定义表情",
    "content": "内容社区（发布合集作品）",
    "gif-library": "GIF 贴纸库",
    "generic": "通用格式",
}


def _write_platform_readme(base: Path, profile: PlatformProfileSpec, result: PlatformExportResult, count: int, language: str) -> None:
    lines = [
        f"# {profile.display_name_zh} 导出包（{profile.display_name}）",
        "",
        f"- 平台类型：{_KIND_ZH.get(profile.kind, profile.kind)}",
        f"- 地区：{profile.region}",
        f"- 表情数量：{count}",
        f"- 文案语言：{language}",
        f"- 说明：{profile.description_zh}",
    ]
    if profile.docs_url:
        lines.append(f"- 官方文档：{profile.docs_url}")
    lines += ["", "## 目录", ""]
    for es in profile.sets:
        parts = []
        if es.static:
            parts.append(f"static/ → {es.static.format.upper()} {es.static.size[0]}×{es.static.size[1]} ≤{es.static.max_bytes // 1000}KB")
        if es.animated:
            parts.append(f"animated/ → {es.animated.format.upper()} {es.animated.size[0]}×{es.animated.size[1]} ≤{es.animated.max_bytes // 1000}KB")
        lines.append(f"- `{es.name}/`：" + "；".join(parts))
    if profile.assets:
        lines.append("- `assets/`：" + "、".join(f"{a.name}（{a.spec.size[0]}×{a.spec.size[1]} {a.spec.format.upper()}）" for a in profile.assets))
    if profile.showcase:
        lines.append("- `showcase/`：" + "、".join(f"{s.name}（{s.kind} {s.size[0]}×{s.size[1]} {s.format.upper()}）" for s in profile.showcase))
    if result.warnings:
        lines += ["", "## ⚠️ 注意", ""] + [f"- {w}" for w in result.warnings]
    if result.skipped:
        lines += ["", "## 跳过的文件", ""] + [f"- {s}" for s in result.skipped]
    lines += ["", "> 平台规格会变化：本包按 2026-11 工程基线生成，提交前请在官方创作者后台复核尺寸、体积、数量与审核要求。", ""]
    base.mkdir(parents=True, exist_ok=True)
    (base / "README.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Platform QA
# ---------------------------------------------------------------------------


def _check_file(f: ExportedFile) -> List[Tuple[str, str, str]]:
    """Return list of (status, check, message)."""
    out: List[Tuple[str, str, str]] = []
    spec = f.spec
    if not f.path.exists():
        return [("fail", "exists", "文件不存在")]
    size = f.path.stat().st_size
    out.append(("pass" if size <= spec.max_bytes else "fail", "bytes", f"{size} / {spec.max_bytes} bytes"))
    if spec.format in ("webm", "mp4"):
        info = probe_video(f.path)
        if info is None:
            out.append(("warn", "probe", "ffprobe 不可用，未校验视频参数"))
            return out
        exp = spec.output_size((1, 1)) if spec.fit == "exact" else spec.size
        dims_ok = (info["width"], info["height"]) == tuple(exp) if spec.fit == "exact" else (info["width"] <= exp[0] and info["height"] <= exp[1])
        out.append(("pass" if dims_ok else "fail", "dimensions", f"{info['width']}×{info['height']} (spec {exp[0]}×{exp[1]})"))
        if spec.max_duration_ms:
            ok = info["duration"] * 1000 <= spec.max_duration_ms + 50
            out.append(("pass" if ok else "fail", "duration", f"{info['duration']:.2f}s ≤ {spec.max_duration_ms / 1000:.1f}s"))
        if spec.format == "webm":
            out.append(("pass" if info.get("codec") == "vp9" else "fail", "codec", f"codec={info.get('codec')}"))
        return out
    try:
        with Image.open(f.path) as img:
            fmt = img.format
            dims = img.size
            n = getattr(img, "n_frames", 1)
            expected_fmt = {"png": "PNG", "apng": "PNG", "gif": "GIF", "webp": "WEBP", "jpg": "JPEG"}[spec.format]
            out.append(("pass" if fmt == expected_fmt else "fail", "format", f"{fmt} (expect {expected_fmt})"))
            if spec.fit == "exact":
                ok = tuple(dims) == tuple(spec.size)
            else:
                ok = dims[0] <= spec.size[0] and dims[1] <= spec.size[1] and (not spec.even_dims or (dims[0] % 2 == 0 and dims[1] % 2 == 0))
            out.append(("pass" if ok else "fail", "dimensions", f"{dims[0]}×{dims[1]} (spec {spec.size[0]}×{spec.size[1]} {spec.fit})"))
            if f.kind == "animated" or (f.kind == "asset" and spec.format in ("apng", "gif")):
                out.append(("pass" if n >= 2 else "fail", "frames", f"{n} frames"))
                if spec.min_frames and n < spec.min_frames:
                    out.append(("fail", "min_frames", f"{n} < {spec.min_frames}"))
                if spec.max_frames and n > spec.max_frames:
                    out.append(("fail", "max_frames", f"{n} > {spec.max_frames}"))
                if spec.max_duration_ms:
                    total = 0
                    for i in range(n):
                        img.seek(i)
                        total += int(img.info.get("duration", 0) or 0)
                    loops = img.info.get("loop", 0) or 1
                    play = total * (loops if spec.format == "apng" and loops else 1)
                    out.append(("pass" if play <= spec.max_duration_ms + 10 else "fail", "duration", f"{play}ms ≤ {spec.max_duration_ms}ms"))
            if spec.transparent and spec.format != "jpg":
                has_alpha = img.mode in ("RGBA", "LA", "PA") or "transparency" in img.info
                out.append(("pass" if has_alpha else "warn", "transparency", "alpha present" if has_alpha else "no alpha channel"))
    except Exception as e:
        out.append(("fail", "decode", str(e)))
    return out


def validate_platform_export(result: PlatformExportResult) -> PlatformExportResult:
    rows = []
    worst = "pass"
    for f in result.files:
        for status, check, msg in _check_file(f):
            rel = f.path.relative_to(result.base_dir) if f.path.is_relative_to(result.base_dir) else f.path
            rows.append({"file": str(rel), "kind": f.kind, "check": check, "status": status, "message": msg})
            if status == "fail":
                worst = "fail"
            elif status == "warn" and worst == "pass":
                worst = "warn"
    if result.warnings and worst == "pass":
        worst = "warn"
    result.status = worst
    if result.base_dir.exists() and result.base_dir.name != "":
        qa_name = "qa-report" if result.base_dir.parent.name == "exports" else f"qa/{result.platform}-platform-report"
        json_path = result.base_dir / f"{qa_name}.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps({"platform": result.platform, "status": worst, "warnings": result.warnings, "skipped": result.skipped, "checks": rows}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        md = [f"# {result.platform} 平台校验：**{worst.upper()}**", ""]
        md += [f"- ⚠️ {w}" for w in result.warnings]
        md += [f"- ⏭️ {s}" for s in result.skipped]
        md += ["", "| 文件 | 检查 | 状态 | 详情 |", "|---|---|---|---|"]
        icon = {"pass": "✅", "warn": "⚠️", "fail": "❌"}
        md += [f"| `{r['file']}` | {r['check']} | {icon[r['status']]} | {r['message']} |" for r in rows]
        md_path = result.base_dir / f"{qa_name}.md"
        md_path.write_text("\n".join(md), encoding="utf-8")
        result.report_path = md_path
    return result


def package_platform(result: PlatformExportResult, output_dir: Path) -> Optional[Path]:
    if result.base_dir == output_dir:
        return None  # legacy WeChat layout is packaged by package_deliverables()
    if not result.base_dir.exists():
        return None
    zip_path = output_dir / "exports" / f"{result.platform}-pack.zip"
    tmp = zip_path.with_name(zip_path.name + ".tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(result.base_dir.rglob("*")):
            if p.is_file() and not p.name.endswith(".tmp"):
                arc = f"{result.platform}/{p.relative_to(result.base_dir).as_posix()}"
                zf.write(p, arc)
    tmp.replace(zip_path)
    result.zip_path = zip_path
    return zip_path


def export_all_platforms(
    output_dir: Path,
    platforms: Sequence[str],
    masters: Sequence[MasterAsset],
    style: str = "real-cutout",
    language: str = "zh-CN",
    pack_title: Optional[str] = None,
    font_path: Optional[str] = None,
    skip_existing: bool = True,
    package: bool = True,
    with_showcase: bool = True,
    validate: bool = True,
) -> Dict[str, PlatformExportResult]:
    """Decode every master once and fan it out to all selected platforms."""
    profiles = load_platform_profiles()
    pids = resolve_platforms(list(platforms))
    title = pack_title or localized_pack_title(language)
    results: Dict[str, PlatformExportResult] = {}
    for pid in pids:
        prof = profiles[pid]
        res = PlatformExportResult(pid, _platform_base(output_dir, prof))
        issue = prof.count_issue(len(masters))
        if issue:
            res.warnings.append(issue)
        results[pid] = res

    need_showcase = with_showcase and any(profiles[p].showcase for p in pids)
    need_anim_showcase = need_showcase and any(s.kind == "video_grid" for p in pids for s in profiles[p].showcase)
    previews: List[Image.Image] = []
    animations: List[List[Image.Image]] = []

    for asset in masters:
        static_img = asset.load_static()
        frames = asset.load_frames()
        fit_cache: dict = {}
        for pid in pids:
            _export_item_files(results[pid].base_dir, profiles[pid], asset, static_img, frames, results[pid], skip_existing, fit_cache)
        preview = static_img if static_img is not None else (frames[0] if frames else None)
        if preview is not None:
            previews.append(_downscale(preview, 540))
        if frames and (need_anim_showcase or any(a.source == "first_animated" for p in pids for a in profiles[p].assets)):
            animations.append([_downscale(f, 360 if animations else 512) for f in frames])

    anchor = _anchor_image(output_dir)
    for pid in pids:
        prof = profiles[pid]
        res = results[pid]
        _finish_platform(
            output_dir, prof, res, masters, previews, animations, style, language, title,
            font_path, skip_existing, with_showcase, anchor,
        )
        if not prof.legacy_root_layout:
            if validate:
                validate_platform_export(res)
            if package:
                package_platform(res, output_dir)
    return results
