"""Data schemas and contracts for WeChat Sticker Maker."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


def sanitize_id(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_\-]", "_", value).strip("_")
    if not cleaned:
        raise ValueError("Identifier must contain alphanumeric characters")
    return cleaned


class AnimationConfig(BaseModel):
    backend: Literal["auto", "keyframes", "native-gif"] = "auto"
    frames: int = 8
    frame_duration_ms: int = 180
    loop: int = 0


class JobConfig(BaseModel):
    job_id: str
    source_image: str
    output_dir: str
    mode: Literal["static", "animated", "both"] = "both"
    count: int = 16
    style: str = "kawaii-flat"
    language: str = "zh-CN"
    background: str = "transparent"
    animation: AnimationConfig = Field(default_factory=AnimationConfig)
    export_profile: str = "wechat-conservative-2026-11"
    allow_cloud_upload: bool = True
    keep_source: bool = False
    font_path: Optional[str] = None

    @field_validator("job_id")
    @classmethod
    def validate_job_id(cls, v: str) -> str:
        return sanitize_id(v)

    @field_validator("count")
    @classmethod
    def validate_count(cls, v: int) -> int:
        if v not in (8, 16, 24):
            raise ValueError(f"Count must be 8, 16, or 24, got {v}")
        return v


class RenderStyle(BaseModel):
    outline: str = "round-uniform"
    palette: List[str] = Field(default_factory=lambda: ["#FFF6EA", "#F7BDC9", "#987C7B"])
    lighting: str = "soft-flat"
    composition: str = "single-character-centered"


class CharacterBible(BaseModel):
    character_id: str
    source_sha256: str
    subject_type: str = "pet-cat"
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
    duration_ms: int = 1440
    frames: int = 8
    loop: str = "seamless"
    amplitude: str = "small"
    stationary_parts: List[str] = Field(
        default_factory=lambda: ["hair_or_fur_pattern", "outfit", "body_silhouette"]
    )


class ExpressionItem(BaseModel):
    id: str
    caption: str
    mood: str
    static_pose: str
    motion: ActionMotion


class ManifestItem(BaseModel):
    id: str
    caption: str
    static_path: Optional[str] = None
    animated_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    checks: Dict[str, str] = Field(default_factory=dict)


class Manifest(BaseModel):
    schema_version: str = "1.0"
    job_id: str
    mode: str
    character_id: str
    generated_count: Dict[str, int] = Field(default_factory=lambda: {"static": 0, "animated": 0})
    items: List[ManifestItem] = Field(default_factory=list)
    validation_report: str = "qa/report.json"
    created_at: str


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
