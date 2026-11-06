"""Multi-platform export profiles (WeChat, QQ, Douyin, Xiaohongshu, Soul, Weibo, Telegram,
WhatsApp, LINE, KakaoTalk, Discord, Slack, iMessage, Signal, Viber, GIPHY, Instagram, TikTok, X...).

Profiles live in ``references/platform-profiles.json`` so new platforms can be added without code.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, Field

ExportFormat = Literal["png", "webp", "gif", "apng", "webm", "mp4", "jpg"]


class FormatSpec(BaseModel):
    format: ExportFormat
    size: Tuple[int, int]
    max_bytes: int
    fit: Literal["exact", "contain"] = "exact"
    margin_px: int = 0
    transparent: bool = True
    background: Optional[str] = None
    even_dims: bool = False
    max_duration_ms: Optional[int] = None
    min_frames: Optional[int] = None
    max_frames: Optional[int] = None
    max_fps: Optional[int] = None
    min_frame_ms: Optional[int] = None
    loop: int = 0

    @property
    def is_animated_format(self) -> bool:
        return self.format in ("gif", "apng", "webm", "mp4") or False

    @property
    def extension(self) -> str:
        return {"apng": "png", "jpg": "jpg"}.get(self.format, self.format)

    def output_size(self, src_size: Tuple[int, int] = (1, 1)) -> Tuple[int, int]:
        """Final canvas size. 'contain' keeps the source aspect inside the max box."""
        bw, bh = self.size
        if self.fit == "exact":
            return bw, bh
        sw, sh = src_size
        scale = min(bw / float(sw), bh / float(sh))
        w, h = max(2, int(sw * scale)), max(2, int(sh * scale))
        if self.even_dims:
            w -= w % 2
            h -= h % 2
        return w, h


class ExportSet(BaseModel):
    name: str
    static: Optional[FormatSpec] = None
    animated: Optional[FormatSpec] = None
    thumbnail: Optional[FormatSpec] = None


class PlatformAsset(BaseModel):
    name: str
    source: Literal["anchor", "first_static", "first_animated", "banner"] = "first_static"
    spec: FormatSpec


class ShowcaseSpec(BaseModel):
    name: str
    kind: Literal["cover", "grid", "single", "story", "nine_grid", "video_grid"]
    size: Tuple[int, int]
    format: Literal["jpg", "png", "mp4"] = "jpg"
    cols: int = 3
    rows: int = 3
    max_items: Optional[int] = None
    seconds: float = 6.0


class PlatformProfileSpec(BaseModel):
    id: str
    display_name: str
    display_name_zh: str
    region: str = "Global"
    kind: Literal["sticker-store", "chat-app", "content", "gif-library", "generic"] = "generic"
    description_zh: str = ""
    docs_url: Optional[str] = None
    legacy_root_layout: bool = False
    requires_manual_recheck: bool = True
    pack_counts: Optional[List[int]] = None
    min_count: Optional[int] = None
    max_count: Optional[int] = None
    file_pattern: str = "{id}"
    sets: List[ExportSet] = Field(default_factory=list)
    assets: List[PlatformAsset] = Field(default_factory=list)
    showcase: List[ShowcaseSpec] = Field(default_factory=list)

    def file_stem(self, item_id: str, index: int) -> str:
        return self.file_pattern.format(id=item_id, index=index)

    def count_issue(self, count: int) -> Optional[str]:
        if self.pack_counts and count not in self.pack_counts:
            return f"{self.display_name_zh} 要求每包 {self.pack_counts} 张，当前 {count} 张"
        if self.min_count is not None and count < self.min_count:
            return f"{self.display_name_zh} 每包至少 {self.min_count} 张，当前 {count} 张"
        if self.max_count is not None and count > self.max_count:
            return f"{self.display_name_zh} 每包最多 {self.max_count} 张，当前 {count} 张"
        return None


def get_platform_profiles_path() -> Path:
    repo_root = Path(__file__).resolve().parent.parent.parent
    return repo_root / "references" / "platform-profiles.json"


@lru_cache(maxsize=4)
def _load_raw(path_str: str) -> dict:
    with Path(path_str).open("r", encoding="utf-8") as f:
        return json.load(f)


def load_platform_profiles(path: Optional[Path] = None) -> Dict[str, PlatformProfileSpec]:
    raw = _load_raw(str(path or get_platform_profiles_path()))
    return {p["id"]: PlatformProfileSpec(**p) for p in raw.get("profiles", [])}


def platform_groups(path: Optional[Path] = None) -> Dict[str, List[str]]:
    return dict(_load_raw(str(path or get_platform_profiles_path())).get("groups", {}))


def platform_aliases(path: Optional[Path] = None) -> Dict[str, str]:
    return dict(_load_raw(str(path or get_platform_profiles_path())).get("aliases", {}))


def resolve_platforms(names: List[str] | str | None) -> List[str]:
    """Expand aliases ('ins', '小红书', 'tg'), groups ('china', 'social') and 'all' into profile ids."""
    if names is None:
        return ["wechat"]
    if isinstance(names, str):
        names = [n for n in names.replace("，", ",").split(",")]
    profiles = load_platform_profiles()
    groups = platform_groups()
    aliases = platform_aliases()
    out: List[str] = []
    for raw in names:
        key = raw.strip().lower()
        if not key:
            continue
        if key == "all":
            expanded = list(profiles.keys())
        elif key in groups:
            expanded = groups[key]
        else:
            pid = aliases.get(key, aliases.get(raw.strip(), key))
            if pid not in profiles:
                raise ValueError(
                    f"Unknown platform '{raw}'. Available: {', '.join(profiles)}; groups: {', '.join(groups)}; or 'all'"
                )
            expanded = [pid]
        for pid in expanded:
            if pid not in out:
                out.append(pid)
    return out or ["wechat"]


def get_platform(pid: str) -> PlatformProfileSpec:
    profiles = load_platform_profiles()
    resolved = resolve_platforms([pid])[0]
    return profiles[resolved]
