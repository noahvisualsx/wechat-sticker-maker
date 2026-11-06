"""Google Gemini / Nano Banana Image Provider for real-person sticker generation."""

from __future__ import annotations

import base64
import logging
import mimetypes
import os
import time
from pathlib import Path
from typing import List, Optional
import requests

from .base import (
    ProviderAuthError,
    ProviderCapabilities,
    ProviderError,
    ProviderQuotaError,
    ProviderRateLimitError,
    StickerProvider,
)

logger = logging.getLogger(__name__)


class GeminiImagesProvider(StickerProvider):
    """Integrates with Google Gemini generateContent image generation (Nano Banana / gemini-2.5-flash-image)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        image_model: str = "gemini-2.5-flash-image",
        max_retries: int = 2,
        timeout: int = 240,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
        self.base_url = (base_url or os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")).rstrip("/")
        self.image_model = image_model or os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            edit_with_reference=True,
            transparent_png=False,  # Gemini outputs RGB matte; Python flood-fill / rembg removes background
            native_gif=False,
            gif_max_frames=None,
        )

    def _build_parts(self, reference_paths: List[Path], prompt: str) -> list:
        parts = []
        for p in reference_paths:
            if p and p.exists():
                mime = mimetypes.guess_type(p.name)[0] or "image/png"
                b64 = base64.b64encode(p.read_bytes()).decode("ascii")
                parts.append({"inline_data": {"mime_type": mime, "data": b64}})
        parts.append({"text": prompt})
        return parts

    def _call_gemini(self, reference_paths: List[Path], prompt: str, output: Path) -> Path:
        if not self.api_key:
            raise ProviderAuthError("GEMINI_API_KEY is not set or empty.")

        url = f"{self.base_url}/models/{self.image_model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": self._build_parts(reference_paths, prompt)}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        }

        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = self.session.post(url, json=payload, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    for cand in data.get("candidates", []):
                        for part in cand.get("content", {}).get("parts", []):
                            inline = part.get("inlineData") or part.get("inline_data")
                            if inline and inline.get("data"):
                                raw = base64.b64decode(inline["data"])
                                output.parent.mkdir(parents=True, exist_ok=True)
                                tmp = output.with_suffix(".tmp")
                                tmp.write_bytes(raw)
                                tmp.replace(output)
                                return output
                    raise ProviderError(f"Gemini response contained no image data: {data}")
                if resp.status_code in (401, 403):
                    raise ProviderAuthError(f"Gemini Auth Error ({resp.status_code}): {resp.text}")
                if resp.status_code == 429:
                    if "quota" in resp.text.lower() or "resource_exhausted" in resp.text.lower():
                        if attempt >= self.max_retries:
                            raise ProviderQuotaError(f"Gemini Quota Exceeded: {resp.text}")
                    time.sleep(2 ** attempt * 2)
                    last_exc = ProviderRateLimitError(resp.text)
                    continue
                if resp.status_code >= 500:
                    time.sleep(2 ** attempt * 2)
                    last_exc = ProviderError(resp.text)
                    continue
                raise ProviderError(f"Gemini API Error ({resp.status_code}): {resp.text}")
            except (requests.RequestException, ConnectionError, TimeoutError) as e:
                last_exc = e
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt * 2)
                    continue
                raise ProviderError(f"Network error communicating with Gemini: {e}") from e

        raise ProviderError(f"Gemini failed after {self.max_retries} retries: {last_exc}")

    def render_anchor(self, reference_paths: List[Path], prompt: str, output: Path) -> Path:
        return self._call_gemini(reference_paths, prompt, output)

    def render_static(self, reference_paths: List[Path], prompt: str, output: Path) -> Path:
        return self._call_gemini(reference_paths, prompt, output)

    def render_native_gif(self, prompt: str, output: Path, frames: int = 8, frame_duration_ms: int = 180) -> Path:
        raise NotImplementedError("GeminiImagesProvider uses 2x2 action sprite sheets for animated GIFs.")
