"""Configuration definitions and platform profiles."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .styles import load_style_presets, resolve_style_preset

load_dotenv()


STYLE_PRESETS: Dict[str, str] = {
    k: v.prompt_lock for k, v in load_style_presets().items()
}


def get_style_description(style: str) -> str:
    """Return detailed style lock prompt for a given style name."""
    return resolve_style_preset(style).prompt_lock


class AssetSpec(BaseModel):
    size: Tuple[int, int]
    max_bytes: int


class PlatformProfile(BaseModel):
    name: str
    sticker: AssetSpec = Field(default_factory=lambda: AssetSpec(size=(240, 240), max_bytes=500_000))
    thumbnail: AssetSpec = Field(default_factory=lambda: AssetSpec(size=(120, 120), max_bytes=50_000))
    cover: AssetSpec = Field(default_factory=lambda: AssetSpec(size=(240, 240), max_bytes=500_000))
    icon: AssetSpec = Field(default_factory=lambda: AssetSpec(size=(50, 50), max_bytes=100_000))
    banner: AssetSpec = Field(default_factory=lambda: AssetSpec(size=(750, 400), max_bytes=500_000))
    allowed_counts: List[int] = Field(default_factory=lambda: [8, 16, 24])
    requires_manual_platform_recheck: bool = True


PROFILES: Dict[str, PlatformProfile] = {
    "wechat-conservative-2026-11": PlatformProfile(
        name="wechat-conservative-2026-11",
        sticker=AssetSpec(size=(240, 240), max_bytes=500_000),
        thumbnail=AssetSpec(size=(120, 120), max_bytes=50_000),
        cover=AssetSpec(size=(240, 240), max_bytes=500_000),
        icon=AssetSpec(size=(50, 50), max_bytes=100_000),
        banner=AssetSpec(size=(750, 400), max_bytes=500_000),
        allowed_counts=[8, 16, 24],
        requires_manual_platform_recheck=True,
    )
}


def get_profile(name: str = "wechat-conservative-2026-11") -> PlatformProfile:
    if name not in PROFILES:
        raise ValueError(f"Unknown platform profile: {name}. Available: {list(PROFILES.keys())}")
    return PROFILES[name]


class AppSettings(BaseModel):
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_base_url: str = Field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    sticker_image_model: str = Field(default_factory=lambda: os.getenv("STICKER_IMAGE_MODEL", "gpt-image-2.5-sunburst"))
    sticker_gif_model: str = Field(default_factory=lambda: os.getenv("STICKER_GIF_MODEL", "gpt-image-2.6-sunburst"))
    sticker_vision_model: str = Field(default_factory=lambda: os.getenv("STICKER_VISION_MODEL", "gpt-4o-mini"))
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", ""))
    gemini_image_model: str = Field(default_factory=lambda: os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image"))
    ark_api_key: str = Field(default_factory=lambda: os.getenv("ARK_API_KEY", ""))
    ark_base_url: str = Field(default_factory=lambda: os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"))
    ark_image_model: str = Field(default_factory=lambda: os.getenv("ARK_IMAGE_MODEL", "doubao-seedream-3-0-t2i-250415"))
    sticker_max_retries: int = Field(default_factory=lambda: int(os.getenv("STICKER_MAX_RETRIES", "2")))
    sticker_max_parallel: int = Field(default_factory=lambda: int(os.getenv("STICKER_MAX_PARALLEL", "2")))
    sticker_font_path: str = Field(default_factory=lambda: os.getenv("STICKER_FONT_PATH", ""))
    sticker_log_level: str = Field(default_factory=lambda: os.getenv("STICKER_LOG_LEVEL", "INFO"))


def get_default_font_path() -> str | None:
    """Find a system font that supports Simplified Chinese."""
    custom = os.getenv("STICKER_FONT_PATH")
    if custom and Path(custom).exists():
        return custom

    candidate_paths = [
        # macOS paths
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        # Linux paths
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
        # Windows paths
        "C:\\Windows\\Fonts\\msyh.ttc",
        "C:\\Windows\\Fonts\\simhei.ttf",
    ]
    for p in candidate_paths:
        if Path(p).exists():
            return p
    return None
