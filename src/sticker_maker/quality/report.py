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
from .anatomy import audit_pack_directory
from .structural import validate_gif, validate_png
from .visual import check_visual_safety


def run_full_validation(
    output_dir: Path,
    profile_name: str = "wechat-conservative-2026-11",
    *,
    strict_qa: bool = False,
    vlm_qa: bool = False,
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

    if strict_qa or vlm_qa:
        strict_res = audit_pack_directory(output_dir, strict=strict_qa, use_vlm=vlm_qa, prefer_raw=True)
        stats["strict_audit_sheet"] = strict_res.get("audit_sheet")
        for item_entry in strict_res.get("items", []):
            for raw_chk in item_entry.get("checks", []):
                if raw_chk.get("status") in ("fail", "warn"):
                    all_checks.append(ValidationCheck(**raw_chk))

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


def generate_preview_html(output_dir: Path, manifest_data: dict | None = None) -> Path:
    """Generate an interactive WeChat chat preview & mobile saving page (preview.html)."""
    if manifest_data is None:
        mp = output_dir / "manifest.json"
        if mp.exists():
            try:
                manifest_data = json.loads(mp.read_text(encoding="utf-8"))
            except Exception:
                manifest_data = {}
        else:
            manifest_data = {}

    items = manifest_data.get("items", [])
    job_id = manifest_data.get("job_id", output_dir.name)
    lang = manifest_data.get("language", "zh-CN")

    # Discover language packs if multi-language export was used
    packs_dir = output_dir / "packs"
    extra_packs = []
    if packs_dir.exists():
        for d in sorted(packs_dir.iterdir()):
            if d.is_dir():
                extra_packs.append(d.name)

    cards_html = []
    for item in items:
        if item.get("status") == "FAILED":
            continue
        iid = item.get("id", "")
        cap = item.get("caption", "") or item.get("bubble_text", "") or iid
        static_rel = item.get("static_path") or ""
        anim_rel = item.get("animated_path") or ""
        preview_src = anim_rel if anim_rel else static_rel
        if not preview_src:
            continue
        badges = []
        if static_rel:
            badges.append(f'<a href="{static_rel}" download class="btn">PNG</a>')
        if anim_rel:
            badges.append(f'<a href="{anim_rel}" download class="btn btn-gif">GIF</a>')
        cards_html.append(
            f"""
            <div class="card" onclick="sendToChat('{preview_src}', '{cap}')">
              <div class="stage"><img src="{preview_src}" alt="{cap}" loading="lazy" /></div>
              <div class="meta">
                <span class="cap">{cap}</span>
                <span class="id">{iid}</span>
              </div>
              <div class="actions" onclick="event.stopPropagation()">{''.join(badges)}</div>
            </div>
            """
        )

    pack_links = ""
    if extra_packs:
        links = [f'<a class="pack-pill" href="packs/{p}/preview.html">{p}</a>' for p in extra_packs]
        pack_links = f'<div class="packs-bar"><span>多语言分包 (Multi-Language Packs):</span> {" ".join(links)}</div>'

    html = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>WeChat Sticker Preview — {job_id} ({lang})</title>
<style>
  :root {{
    --bg: #EDEDED;
    --card-bg: #F7F7F7;
    --text: #111111;
    --muted: #666666;
    --accent: #07C160;
    --border: rgba(0,0,0,0.08);
  }}
  body.dark {{
    --bg: #111111;
    --card-bg: #1E1E1E;
    --text: #F2F2F2;
    --muted: #999999;
    --border: rgba(255,255,255,0.12);
  }}
  body.checker .stage {{
    background-image: linear-gradient(45deg, #ccc 25%, transparent 25%),
      linear-gradient(-45deg, #ccc 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, #ccc 75%),
      linear-gradient(-45deg, transparent 75%, #ccc 75%);
    background-size: 16px 16px;
    background-position: 0 0, 0 8px, 8px -8px, -8px 0;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 24px 16px 60px;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Noto Sans CJK SC", sans-serif;
    background: var(--bg); color: var(--text);
    transition: background .2s ease, color .2s ease;
  }}
  .container {{ max-width: 1080px; margin: 0 auto; }}
  header {{
    display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
    gap: 12px; margin-bottom: 18px; padding-bottom: 14px; border-bottom: 1px solid var(--border);
  }}
  h1 {{ font-size: 20px; margin: 0; }}
  .controls {{ display: flex; gap: 8px; flex-wrap: wrap; }}
  button, .pack-pill {{
    border: 1px solid var(--border); background: var(--card-bg); color: var(--text);
    padding: 7px 13px; border-radius: 999px; cursor: pointer; font-size: 13px; text-decoration: none;
  }}
  button.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
  .packs-bar {{ margin-bottom: 16px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; font-size: 13px; }}
  .layout {{ display: grid; grid-template-columns: 1fr 330px; gap: 20px; align-items: start; }}
  @media (max-width: 820px) {{ .layout {{ grid-template-columns: 1fr; }} }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(175px, 1fr)); gap: 14px; }}
  .card {{
    background: var(--card-bg); border: 1px solid var(--border); border-radius: 14px;
    padding: 10px; cursor: pointer; transition: transform .15s ease;
  }}
  .card:hover {{ transform: translateY(-2px); }}
  .stage {{
    width: 100%; aspect-ratio: 1/1; display: flex; align-items: center; justify-content: center;
    background: var(--bg); border-radius: 10px; overflow: hidden;
  }}
  .stage img {{ width: 88%; height: 88%; object-fit: contain; }}
  .meta {{ display: flex; justify-content: space-between; align-items: center; margin-top: 8px; font-size: 13px; }}
  .cap {{ font-weight: 600; }}
  .id {{ color: var(--muted); font-size: 11px; }}
  .actions {{ display: flex; gap: 6px; margin-top: 6px; }}
  .btn {{
    font-size: 11px; padding: 3px 8px; border-radius: 6px; text-decoration: none;
    background: rgba(7,193,96,0.14); color: var(--accent); font-weight: 600;
  }}
  .chat-box {{
    background: var(--bg); border: 1px solid var(--border); border-radius: 16px;
    overflow: hidden; position: sticky; top: 16px;
  }}
  .chat-header {{
    background: var(--card-bg); padding: 11px 14px; font-weight: 600; font-size: 14px;
    border-bottom: 1px solid var(--border); display: flex; justify-content: space-between;
  }}
  .chat-messages {{ padding: 14px; min-height: 360px; max-height: 480px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }}
  .msg {{ display: flex; align-items: flex-start; gap: 8px; }}
  .msg.self {{ flex-direction: row-reverse; }}
  .avatar {{ width: 34px; height: 34px; border-radius: 6px; background: var(--accent); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; flex-shrink: 0; }}
  .bubble {{ background: #95EC69; color: #111; padding: 8px 12px; border-radius: 8px; font-size: 13px; max-width: 72%; }}
  .sticker-msg img {{ width: 128px; height: 128px; object-fit: contain; display: block; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <div>
      <h1>微信聊天实测预览 · {job_id} <small style="font-weight:400;color:var(--muted)">({lang})</small></h1>
      <div style="font-size:12px;color:var(--muted);margin-top:4px">点击任意表情即可发送到右侧微信对话框实测白边与文字清晰度；手机端可长按保存图片</div>
    </div>
    <div class="controls">
      <button id="btn-light" class="active" onclick="setMode('light')">微信浅色 (#EDEDED)</button>
      <button id="btn-dark" onclick="setMode('dark')">微信深色 (#111111)</button>
      <button id="btn-checker" onclick="setMode('checker')">透明棋盘格</button>
    </div>
  </header>
  {pack_links}
  <div class="layout">
    <div class="grid">
      {''.join(cards_html)}
    </div>
    <div class="chat-box">
      <div class="chat-header"><span>微信对话实测窗</span><span style="color:var(--muted);font-size:12px">点击左侧表情发送</span></div>
      <div class="chat-messages" id="chat-feed">
        <div class="msg"><div class="avatar">友</div><div class="bubble">发张新做的真人表情包看看！</div></div>
      </div>
    </div>
  </div>
</div>
<script>
function setMode(mode) {{
  document.body.className = mode === 'light' ? '' : mode;
  document.querySelectorAll('.controls button').forEach(b => b.classList.remove('active'));
  document.getElementById('btn-' + mode).classList.add('active');
}}
function sendToChat(src, cap) {{
  const feed = document.getElementById('chat-feed');
  const div = document.createElement('div');
  div.className = 'msg self';
  div.innerHTML = '<div class="avatar">我</div><div class="sticker-msg"><img src="' + src + '" alt="' + cap + '"/></div>';
  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
}}
</script>
</body>
</html>"""
    out = output_dir / "preview.html"
    out.write_text(html, encoding="utf-8")
    return out
