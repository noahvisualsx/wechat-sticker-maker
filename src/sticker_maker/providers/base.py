"""Base interfaces and exceptions for image and animation providers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Protocol


class ProviderError(Exception):
    """Base error for sticker provider issues."""


class ProviderAuthError(ProviderError):
    """Authentication or authorization failure (e.g. 401/403)."""


class ProviderQuotaError(ProviderError):
    """Quota or billing balance exhausted."""


class ProviderRateLimitError(ProviderError):
    """Rate limit hit (429)."""


class ProviderCapabilityError(ProviderError):
    """Requested capability not supported by this model or endpoint."""


@dataclass
class ProviderCapabilities:
    edit_with_reference: bool
    transparent_png: bool
    native_gif: bool
    gif_max_frames: Optional[int] = None


class StickerProvider(Protocol):
    def capabilities(self) -> ProviderCapabilities:
        ...

    def render_anchor(
        self, reference_paths: List[Path], prompt: str, output: Path
    ) -> Path:
        ...

    def render_static(
        self, reference_paths: List[Path], prompt: str, output: Path
    ) -> Path:
        ...

    def render_native_gif(
        self, prompt: str, output: Path, frames: int = 8, frame_duration_ms: int = 180
    ) -> Path:
        ...
