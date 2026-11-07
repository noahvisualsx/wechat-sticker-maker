"""Direct Telegram Sticker Pack Publisher via Telegram Bot API (`createNewStickerSet` / `addStickerToSet`).

Supports both:
- Live publishing (when `--bot-token` or `TELEGRAM_BOT_TOKEN` and `--user-id` are provided)
- Offline validation & manifest preparation (`--dry-run`, or when no token is provided), auto-converting
  PNGs to Telegram-compliant 512px WebP stickers and mapping expression categories to default emojis.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image
import requests

CATEGORY_EMOJI_MAP: Dict[str, str] = {
    "greeting": "👋",
    "positive": "😄",
    "negative": "😭",
    "surprise": "😱",
    "reply": "👌",
    "polite": "🙏",
    "love": "❤️",
    "praise": "👍",
    "daily": "☕",
    "work": "💼",
    "meme": "🤣",
    "festival": "🎉",
    "status": "🫠",
    "social": "🥂",
    "gaming": "🎮",
    "fandom": "💖",
    "wealth": "🧧",
    "foodie": "🧋",
    "campus": "📚",
    "sassy": "💅",
    "mental": "🌀",
    "pet_collab": "🐾",
    "besties": "👯‍♀️",
    "couple": "👩‍❤️‍👨",
    "yuri": "🌸",
    "yaoi": "🥂",
    "rivals": "⚡",
    "family": "🧸",
    "cat_boss": "🐱",
    "dog_happy": "🐶",
    "pet_meme": "🐾",
    "pet_festival": "🎊",
}


def _fit_telegram_512_webp(src_png: Path, dst_webp: Path) -> Path:
    """Convert any PNG sticker into a Telegram-compliant WebP where the longest side is exactly 512px."""
    dst_webp.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src_png) as im:
        rgba = im.convert("RGBA")
        w, h = rgba.size
        if max(w, h) != 512:
            if w >= h:
                new_w = 512
                new_h = max(1, int(round(h * (512.0 / w))))
            else:
                new_h = 512
                new_w = max(1, int(round(w * (512.0 / h))))
            rgba = rgba.resize((new_w, new_h), Image.Resampling.LANCZOS)
        rgba.save(dst_webp, format="WEBP", quality=92, method=6)
    return dst_webp


def _infer_emoji_for_filename(stem: str, default_emoji: str = "✨") -> str:
    lower = stem.lower()
    if any(k in lower for k in ("hello", "hi", "morning", "wave")):
        return "👋"
    if any(k in lower for k in ("laugh", "happy", "yay", "smile")):
        return "😂"
    if any(k in lower for k in ("cry", "sad", "tear", "wronged")):
        return "😭"
    if any(k in lower for k in ("angry", "mad", "rage", "scold", "rival")):
        return "😡"
    if any(k in lower for k in ("love", "heart", "kiss", "hug", "couple", "yuri", "yaoi")):
        return "❤️"
    if any(k in lower for k in ("shock", "surprise", "wtf", "quake")):
        return "😱"
    if any(k in lower for k in ("ok", "ack", "roger", "salute", "yes")):
        return "👌"
    if any(k in lower for k in ("thank", "bow", "polite")):
        return "🙏"
    if any(k in lower for k in ("sleep", "night", "tired")):
        return "😴"
    if any(k in lower for k in ("cat", "meow", "loaf")):
        return "🐱"
    if any(k in lower for k in ("dog", "woof", "puppy")):
        return "🐶"
    if any(k in lower for k in ("money", "rich", "red_envelope", "wealth", "koi")):
        return "🧧"
    if any(k in lower for k in ("boba", "tea", "eat", "food", "coffee")):
        return "🧋"
    if any(k in lower for k in ("game", "mvp", "gg", "carry")):
        return "🎮"
    return default_emoji


def prepare_telegram_sticker_files(output_dir: Path) -> List[Dict[str, str]]:
    """Locate or auto-convert 512px WebP stickers for Telegram upload and assign emojis."""
    tg_static = output_dir / "platforms" / "telegram" / "static"
    webps = sorted(tg_static.glob("*.webp")) if tg_static.exists() else []

    if not webps:
        # Auto-convert from work/master or static/
        work_master = output_dir / "work" / "master"
        static_dir = output_dir / "static"
        pngs = sorted(work_master.glob("*_static.png")) if work_master.exists() else []
        if not pngs and static_dir.exists():
            pngs = sorted(static_dir.glob("*.png"))
        if not pngs:
            raise FileNotFoundError(f"No sticker PNGs or Telegram WebPs found in {output_dir}")
        tg_static.mkdir(parents=True, exist_ok=True)
        for idx, p in enumerate(pngs, 1):
            dst = tg_static / f"{idx:02d}_{p.stem}.webp"
            _fit_telegram_512_webp(p, dst)
            webps.append(dst)

    # Check manifest.json if available to map categories to emojis
    cat_by_id: Dict[str, str] = {}
    manifest_p = output_dir / "manifest.json"
    if manifest_p.exists():
        try:
            mdata = json.loads(manifest_p.read_text(encoding="utf-8"))
            for it in mdata.get("items", []):
                if it.get("id") and it.get("category"):
                    cat_by_id[it["id"]] = it["category"]
        except Exception:
            pass

    entries: List[Dict[str, str]] = []
    for p in webps[:120]:
        emoji = _infer_emoji_for_filename(p.stem)
        for item_id, cat in cat_by_id.items():
            if item_id in p.stem and cat in CATEGORY_EMOJI_MAP:
                emoji = CATEGORY_EMOJI_MAP[cat]
                break
        with Image.open(p) as im:
            w, h = im.size
        entries.append(
            {
                "file": str(p),
                "filename": p.name,
                "emoji": emoji,
                "width": str(w),
                "height": str(h),
                "size_bytes": str(p.stat().st_size),
            }
        )
    return entries


def publish_to_telegram_bot(
    output_dir: Path,
    pack_short_name: str,
    pack_title: str,
    user_id: Optional[int] = None,
    bot_token: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, object]:
    """Validate and optionally upload a sticker set to Telegram via Bot API.

    Returns a dictionary containing ``status``, ``share_url``, ``manifest_path``, and ``sticker_count``.
    """
    token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
    entries = prepare_telegram_sticker_files(output_dir)
    clean_short = re.sub(r"[^a-zA-Z0-9_]", "_", pack_short_name).strip("_")
    if not clean_short or not clean_short[0].isalpha():
        clean_short = "real_pack_" + (clean_short or "01")

    manifest_data: Dict[str, object] = {
        "pack_short_name": clean_short,
        "pack_title": pack_title,
        "user_id": user_id,
        "sticker_format": "static",
        "sticker_count": len(entries),
        "stickers": entries,
        "status": "dry_run" if (dry_run or not token or not user_id) else "ready",
        "share_url": f"https://t.me/addstickers/{clean_short}",
    }

    manifest_p = output_dir / "platforms" / "telegram" / "telegram_publish_manifest.json"
    manifest_p.parent.mkdir(parents=True, exist_ok=True)

    if dry_run or not token or not user_id:
        manifest_p.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "status": "dry_run",
            "sticker_count": len(entries),
            "manifest_path": str(manifest_p),
            "share_url": f"https://t.me/addstickers/{clean_short}",
        }

    base_url = f"https://api.telegram.org/bot{token}"
    me_resp = requests.get(f"{base_url}/getMe", timeout=15)
    me_json = me_resp.json()
    if not me_json.get("ok"):
        raise RuntimeError(f"Telegram getMe failed: {me_json}")
    bot_username = me_json["result"]["username"]
    suffix = f"_by_{bot_username}"
    if not clean_short.lower().endswith(suffix.lower()):
        clean_short = f"{clean_short}{suffix}"

    first = entries[0]
    with open(first["file"], "rb") as f0:
        sticker_obj = {
            "sticker": "attach://file0",
            "format": "static",
            "emoji_list": [first["emoji"]],
        }
        resp = requests.post(
            f"{base_url}/createNewStickerSet",
            data={
                "user_id": int(user_id),
                "name": clean_short,
                "title": pack_title,
                "stickers": json.dumps([sticker_obj]),
            },
            files={"file0": (first["filename"], f0, "image/webp")},
            timeout=30,
        )
    res_json = resp.json()
    if not res_json.get("ok"):
        raise RuntimeError(f"Telegram createNewStickerSet failed: {res_json}")

    for idx, entry in enumerate(entries[1:], 2):
        with open(entry["file"], "rb") as fn:
            s_obj = {
                "sticker": "attach://file_n",
                "format": "static",
                "emoji_list": [entry["emoji"]],
            }
            r_add = requests.post(
                f"{base_url}/addStickerToSet",
                data={
                    "user_id": int(user_id),
                    "name": clean_short,
                    "sticker": json.dumps(s_obj),
                },
                files={"file_n": (entry["filename"], fn, "image/webp")},
                timeout=30,
            )
            r_add_json = r_add.json()
            if not r_add_json.get("ok"):
                raise RuntimeError(f"Telegram addStickerToSet (#{idx}) failed: {r_add_json}")

    share_url = f"https://t.me/addstickers/{clean_short}"
    manifest_data["pack_short_name"] = clean_short
    manifest_data["status"] = "published"
    manifest_data["share_url"] = share_url
    manifest_p.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "status": "published",
        "sticker_count": len(entries),
        "manifest_path": str(manifest_p),
        "share_url": share_url,
    }
