"""Data schemas and contracts for WeChat Sticker Maker."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


def sanitize_id(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_\-]", "_", value).strip("_")
    if not cleaned:
        raise ValueError("Identifier must contain alphanumeric characters")
    return cleaned


class AnimationConfig(BaseModel):
    backend: Literal["auto", "keyframes", "sprite-sheet", "native-gif"] = "auto"
    frames: int = 8
    frame_duration_ms: int = 160
    loop: int = 0


BubbleShape = Literal["round", "oval", "thought", "shout", "rect", "heart", "whisper"]
BubblePosition = Literal["auto", "top-left", "top-right"]
BubbleAnimation = Literal["none", "pop", "typewriter", "bob", "dots"]
TextLayoutMode = Literal["caption", "bubble", "both", "none"]

WECHAT_ALLOWED_COUNTS = (8, 16, 24)


class JobConfig(BaseModel):
    job_id: str
    source_image: str
    output_dir: str
    mode: Literal["static", "animated", "both"] = "both"
    count: int = 16
    style: str = "real-cutout"
    language: str = "zh-CN"  # exactly ONE language per pack — never mix languages on a sticker
    text_layout: Literal["auto", "caption", "bubble", "both", "none"] = "auto"
    bubble_shape: Optional[BubbleShape] = None
    bubble_animation: BubbleAnimation = "none"
    categories: Optional[List[str]] = None
    expression_ids: Optional[List[str]] = None
    pack_type: Literal["expressions", "memes", "mixed"] = "expressions"
    meme_templates: Optional[List[str]] = None
    meme_categories: Optional[List[str]] = None
    meme_texts: Optional[Dict[str, str]] = None  # override main text of single-template memes
    captions_file: Optional[str] = None
    platforms: List[str] = Field(default_factory=lambda: ["wechat"])
    master_size: int = 720
    pack_title: Optional[str] = None
    background: str = "transparent"
    animation: AnimationConfig = Field(default_factory=AnimationConfig)
    export_profile: str = "wechat-conservative-2026-11"
    allow_cloud_upload: bool = True
    keep_source: bool = False
    font_path: Optional[str] = None
    subject_type: Optional[str] = "human-portrait"
    custom_facts: Optional[List[str]] = None

    @field_validator("job_id")
    @classmethod
    def validate_job_id(cls, v: str) -> str:
        return sanitize_id(v)

    @field_validator("platforms")
    @classmethod
    def validate_platforms(cls, v: List[str]) -> List[str]:
        cleaned = [p.strip().lower() for p in v if p and p.strip()]
        return cleaned or ["wechat"]

    @field_validator("master_size")
    @classmethod
    def validate_master_size(cls, v: int) -> int:
        if v < 240 or v > 2048:
            raise ValueError(f"master_size must be between 240 and 2048, got {v}")
        return v

    @model_validator(mode="after")
    def validate_count_for_platforms(self) -> "JobConfig":
        if self.count < 1 or self.count > 120:
            raise ValueError(f"Count must be between 1 and 120, got {self.count}")
        if "wechat" in self.platforms and self.count not in WECHAT_ALLOWED_COUNTS:
            raise ValueError(
                f"Count must be 8, 16, or 24 when exporting to WeChat, got {self.count} "
                f"(remove 'wechat' from platforms to use other counts)"
            )
        return self


class RenderStyle(BaseModel):
    style_id: str = "real-cutout"
    outline: str = "die-cut-white-border"
    palette: List[str] = Field(default_factory=lambda: ["#FFE5D9", "#F4A261", "#3D405B"])
    lighting: str = "studio-portrait"
    composition: str = "single-character-centered"


class TypographyStyle(BaseModel):
    text_color: str = "#1F2421"
    stroke_color: str = "#FFFFFF"
    stroke_width: int = 4
    start_font_size: int = 27


class BubbleStyle(BaseModel):
    """Speech-bubble colours; omitted fields are derived from the style typography."""

    fill: Optional[str] = None
    outline: Optional[str] = None
    text_color: Optional[str] = None
    outline_width: float = 2.5
    default_shape: BubbleShape = "round"
    font_size: int = 20


class StylePreset(BaseModel):
    id: str
    display_name: str
    category: str = "真人专属"
    region: str = "通用"  # 通用 / 韩系 / 日系 / 中式
    description: str = ""
    prompt_lock: str
    negative_extra: str = ""
    outline: str = "die-cut-white-border"
    lighting: str = "studio-portrait"
    default_palette: List[str] = Field(default_factory=lambda: ["#FFE5D9", "#F4A261", "#3D405B"])
    banner_bg: str = "#F8F9FA"
    die_cut_border_px: int = 4
    prefer_keyframes: bool = True
    caption_animation: Literal["none", "pulse", "bounce", "shake"] = "none"
    typography: TypographyStyle = Field(default_factory=TypographyStyle)
    bubble: BubbleStyle = Field(default_factory=BubbleStyle)


class CharacterBible(BaseModel):
    character_id: str
    source_sha256: str
    subject_type: str = "human-portrait"
    identity_facts: List[str] = Field(default_factory=list)
    locked_attributes: List[str] = Field(default_factory=list)
    allowed_variation: List[str] = Field(default_factory=list)
    render_style: RenderStyle = Field(default_factory=RenderStyle)
    master_anchor: str
    reference_image: str

    @field_validator("character_id")
    @classmethod
    def validate_char_id(cls, v: str) -> str:
        return sanitize_id(v)


class ActionMotion(BaseModel):
    type: str
    duration_ms: int = 1280
    frames: int = 8
    loop: str = "seamless"
    amplitude: str = "medium"
    keyframe_poses: List[str] = Field(default_factory=list)
    stationary_parts: List[str] = Field(
        default_factory=lambda: ["lower_torso", "shoulders", "hairstyle", "outfit"]
    )


class BubbleSpec(BaseModel):
    shape: BubbleShape = "round"
    position: BubblePosition = "auto"
    texts: Dict[str, str] = Field(default_factory=dict)
    animation: Optional[BubbleAnimation] = None


MemeElementType = Literal[
    "spinner",        # AI "thinking" starburst icon (on head / corner), can rotate
    "prohibition",    # red no-entry circle with slash (+ optional text)
    "hazard_tape",    # yellow/black caution tape band with text
    "stamp",          # red rubber stamp (封号 / BANNED / 已阅), can slam in
    "dialog",         # generic system dialog box (title, message, button, icon)
    "chat",           # IM chat bubble screenshot style
    "notice",         # gray group-chat system notice pill (你已被禁言…)
    "chip",           # small rounded label (已深度思考（用时 30 秒）)
    "progress",       # loading / progress bar with label
    "big_text",       # huge glitchy text (404 / 403 / ？？？)
    "impact",         # classic top/bottom meme text (white with black outline)
    "top_bar",        # white caption bar above the image (Twitter-style meme)
    "speed_lines",    # radial manga speed lines (background)
    "light_rays",     # radial light rays / enlightenment glow (background)
    "crack",          # broken-glass cracks over the image (我裂开了)
    "smoke",          # smoke puffs above head (CPU 干烧了)
    "battery",        # low battery icon with %
    "typing",         # 对方正在输入… indicator
    "read_receipt",   # 已读 label
    "sparkles",       # twinkling stars
    "question_marks", # floating ??? around the head
    "mute",           # muted speaker badge
]
MemePosition = Literal[
    "head", "top", "bottom", "center", "top-left", "top-right", "bottom-left", "bottom-right", "cross", "full"
]
MemeAnimation = Literal["none", "rotate", "pulse", "slam", "flash", "drift", "progress", "dots", "twinkle", "shake", "glitch"]
MemeFilter = Literal["deep_fry", "glitch", "patina", "grayscale", "hue_cycle", "vignette", "high_contrast", "posterize"]


class MemeElement(BaseModel):
    type: MemeElementType
    text: Dict[str, str] = Field(default_factory=dict)  # localized main text (any language key)
    title: Dict[str, str] = Field(default_factory=dict)  # dialog title / secondary text
    button: Dict[str, str] = Field(default_factory=dict)  # dialog button label
    position: MemePosition = "top"
    color: Optional[str] = None
    size: float = 1.0
    angle: float = 0.0
    value: Optional[float] = None  # progress / battery percent, chip seconds ...
    icon: Optional[Literal["warning", "error", "info", "ban", "question"]] = None
    animate: MemeAnimation = "none"
    layer: Literal["back", "front"] = "front"


class MemeSpec(BaseModel):
    elements: List[MemeElement] = Field(default_factory=list)
    filters: List[MemeFilter] = Field(default_factory=list)
    style_hint: str = ""  # extra prompt guidance for the AI image (pose / vibe / abstract look)
    background: Optional[str] = None  # opaque meme background colour (None = transparent sticker)


class ExpressionItem(BaseModel):
    id: str
    caption: str
    mood: str
    static_pose: str
    motion: ActionMotion
    category: str = "general"
    captions: Dict[str, str] = Field(default_factory=dict)
    text_layout: TextLayoutMode = "caption"
    bubble: Optional[BubbleSpec] = None
    meme: Optional[MemeSpec] = None
    name_zh: Optional[str] = None


class TextSpec(BaseModel):
    """Fully resolved text to overlay on one sticker (language-specific)."""

    language: str = "zh-CN"
    layout: TextLayoutMode = "caption"
    caption: str = ""
    bubble_text: str = ""
    bubble_shape: BubbleShape = "round"
    bubble_position: BubblePosition = "auto"
    bubble_animation: BubbleAnimation = "none"
    needs_translation: bool = False

    @property
    def has_caption(self) -> bool:
        return self.layout in ("caption", "both") and bool(self.caption)

    @property
    def has_bubble(self) -> bool:
        return self.layout in ("bubble", "both") and bool(self.bubble_text)


class ManifestItem(BaseModel):
    id: str
    caption: str
    static_path: Optional[str] = None
    animated_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    status: Literal["PENDING", "RUNNING", "SUCCESS", "WARNING", "FAILED"] = "SUCCESS"
    error: Optional[str] = None
    checks: Dict[str, str] = Field(default_factory=dict)
    category: Optional[str] = None
    language: Optional[str] = None
    text_layout: Optional[str] = None
    bubble_text: Optional[str] = None
    needs_translation: bool = False
    exports: Dict[str, Dict[str, str]] = Field(default_factory=dict)


class Manifest(BaseModel):
    schema_version: str = "2.0"
    job_id: str
    mode: str
    character_id: str
    state: str = "COMPLETED"
    generated_count: Dict[str, int] = Field(default_factory=lambda: {"static": 0, "animated": 0})
    items: List[ManifestItem] = Field(default_factory=list)
    validation_report: str = "qa/report.json"
    created_at: str
    language: str = "zh-CN"
    platforms: List[str] = Field(default_factory=lambda: ["wechat"])
    platform_reports: Dict[str, str] = Field(default_factory=dict)


class ValidationCheck(BaseModel):
    name: str
    target: str
    status: Literal["pass", "warn", "fail"]
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class ValidationReport(BaseModel):
    job_id: str
    profile: str
    overall_status: Literal["pass", "warn", "fail"]
    timestamp: str
    checks: List[ValidationCheck] = Field(default_factory=list)
    stats: Dict[str, Any] = Field(default_factory=dict)
