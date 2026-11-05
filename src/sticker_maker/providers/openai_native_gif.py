"""OpenAI Native GIF Provider using Image Generation 2.6 endpoint."""

from __future__ import annotations

import base64
import logging
import os
import time
from pathlib import Path
from typing import List, Optional
import requests

from .base import (
    ProviderAuthError,
    ProviderCapabilities,
    ProviderCapabilityError,
    ProviderError,
    ProviderQuotaError,
    ProviderRateLimitError,
    StickerProvider,
)

logger = logging.getLogger(__name__)


class OpenAINativeGifProvider(StickerProvider):
    """Integrates with OpenAI Image 2.6 Native GIF generation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        gif_model: str = "gpt-image-2.6-sunburst",
        max_retries: int = 2,
        timeout: int = 240,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.gif_model = gif_model or os.getenv("STICKER_GIF_MODEL", "gpt-image-2.6-sunburst")
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            edit_with_reference=False,  # Generation endpoint does not edit with photo references directly
            transparent_png=True,
            native_gif=True,
            gif_max_frames=64,
        )

    def _get_headers(self) -> dict[str, str]:
        if not self.api_key:
            raise ProviderAuthError("OPENAI_API_KEY is not set or empty.")
        return {"Authorization": f"Bearer {self.api_key}"}

    def _handle_response_error(self, resp: requests.Response) -> None:
        try:
            data = resp.json()
            err_msg = data.get("error", {}).get("message", resp.text)
            err_code = data.get("error", {}).get("code", "")
        except Exception:
            err_msg = resp.text
            err_code = ""

        # Check for capability mismatch / unsupported format
        if resp.status_code == 400:
            lower = err_msg.lower()
            if "output_format" in lower or "gif" in lower or "not supported" in lower or "unrecognized parameter" in lower:
                raise ProviderCapabilityError(f"Native GIF not supported on this endpoint/model: {err_msg}")

        if resp.status_code in (401, 403):
            raise ProviderAuthError(f"OpenAI Auth Error ({resp.status_code}): {err_msg}")
        elif resp.status_code == 404:
            raise ProviderCapabilityError(f"Model or endpoint not found ({resp.status_code}): {err_msg}")
        elif resp.status_code == 429:
            if "insufficient_quota" in err_code or "quota" in err_msg.lower():
                raise ProviderQuotaError(f"OpenAI Quota Exceeded: {err_msg}")
            raise ProviderRateLimitError(f"OpenAI Rate Limit: {err_msg}")
        else:
            raise ProviderError(f"OpenAI API Error ({resp.status_code}): {err_msg}")

    def render_anchor(self, reference_paths: List[Path], prompt: str, output: Path) -> Path:
        raise NotImplementedError("Use OpenAIImagesProvider for anchor rendering")

    def render_static(self, reference_paths: List[Path], prompt: str, output: Path) -> Path:
        raise NotImplementedError("Use OpenAIImagesProvider for static reference editing")

    def render_native_gif(
        self, prompt: str, output: Path, frames: int = 8, frame_duration_ms: int = 180
    ) -> Path:
        url = f"{self.base_url}/images/generations"
        payload = {
            "model": self.gif_model,
            "prompt": prompt,
            "output_format": "gif",
            "frame_count": frames,
            "frame_duration_ms": frame_duration_ms,
            "size": "512x512",
        }

        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = self.session.post(url, headers=self._get_headers(), json=payload, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    b64_str = data["data"][0].get("b64_json")
                    if not b64_str and "url" in data["data"][0]:
                        # Download from URL if returned
                        r = requests.get(data["data"][0]["url"], timeout=60)
                        raw_bytes = r.content
                    else:
                        raw_bytes = base64.b64decode(b64_str)

                    output.parent.mkdir(parents=True, exist_ok=True)
                    tmp = output.with_suffix(".tmp")
                    tmp.write_bytes(raw_bytes)
                    tmp.replace(output)
                    return output

                self._handle_response_error(resp)
            except ProviderCapabilityError:
                raise
            except (requests.RequestException, ConnectionError, TimeoutError) as e:
                logger.warning("GIF generation network attempt %d failed: %s", attempt + 1, e)
                last_exc = e
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt * 2)
                    continue
                raise ProviderError(f"Network error in native GIF generation: {e}") from e

        if last_exc:
            raise ProviderError(f"Failed to generate native GIF: {last_exc}")
        raise ProviderError("Failed to generate native GIF")
