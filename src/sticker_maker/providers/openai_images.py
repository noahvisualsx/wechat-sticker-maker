"""OpenAI Images Provider for static sticker rendering and reference image edits."""

from __future__ import annotations

import base64
from contextlib import ExitStack
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


class OpenAIImagesProvider(StickerProvider):
    """Integrates with OpenAI /v1/images/edits and /v1/images/generations."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        image_model: str = "gpt-image-2.5-sunburst",
        max_retries: int = 2,
        timeout: int = 240,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.image_model = image_model or os.getenv("STICKER_IMAGE_MODEL", "gpt-image-2.5-sunburst")
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            edit_with_reference=True,
            transparent_png=True,
            native_gif=False,
            gif_max_frames=None,
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

        if resp.status_code in (401, 403):
            raise ProviderAuthError(f"OpenAI Auth Error ({resp.status_code}): {err_msg}")
        elif resp.status_code == 429:
            if "insufficient_quota" in err_code or "quota" in err_msg.lower():
                raise ProviderQuotaError(f"OpenAI Quota Exceeded: {err_msg}")
            raise ProviderRateLimitError(f"OpenAI Rate Limit: {err_msg}")
        else:
            raise ProviderError(f"OpenAI API Error ({resp.status_code}): {err_msg}")

    def _execute_with_retry(self, fn) -> requests.Response:
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = fn()
                if resp.status_code == 200:
                    return resp
                if resp.status_code == 429 or resp.status_code >= 500:
                    retry_after = resp.headers.get("Retry-After")
                    sleep_time = float(retry_after) if retry_after else (2 ** attempt * 2)
                    logger.warning("API returned %s; retrying in %.1fs...", resp.status_code, sleep_time)
                    time.sleep(sleep_time)
                    last_exc = resp
                    continue
                self._handle_response_error(resp)
            except (requests.RequestException, ConnectionError, TimeoutError) as e:
                logger.warning("Network request failed (attempt %d/%d): %s", attempt + 1, self.max_retries + 1, e)
                last_exc = e
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt * 2)
                    continue
                raise ProviderError(f"Network error communicating with OpenAI: {e}") from e

        if isinstance(last_exc, requests.Response):
            self._handle_response_error(last_exc)
        raise ProviderError(f"Failed after {self.max_retries} retries: {last_exc}")

    def render_anchor(
        self, reference_paths: List[Path], prompt: str, output: Path
    ) -> Path:
        """Generate or edit anchor image."""
        if reference_paths and reference_paths[0].exists():
            return self.render_static(reference_paths, prompt, output)

        # Fallback to text generation if no reference file
        def call():
            url = f"{self.base_url}/images/generations"
            payload = {
                "model": self.image_model,
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
                "response_format": "b64_json",
            }
            return self.session.post(url, headers=self._get_headers(), json=payload, timeout=self.timeout)

        resp = self._execute_with_retry(call)
        data = resp.json()
        b64_str = data["data"][0]["b64_json"]
        self._write_b64_to_file(b64_str, output)
        return output

    def render_static(
        self, reference_paths: List[Path], prompt: str, output: Path
    ) -> Path:
        """Edit reference image(s) to produce expression sticker, with multi-image to single-image fallback."""
        valid_refs = [p for p in reference_paths if p and p.exists()]
        if not valid_refs:
            raise FileNotFoundError(f"Reference image not found in: {reference_paths}")

        url = f"{self.base_url}/images/edits"
        headers = self._get_headers()

        def call_multi():
            with ExitStack() as stack:
                if len(valid_refs) > 1:
                    files = [
                        (
                            "image[]",
                            (p.name, stack.enter_context(p.open("rb")), mimetypes.guess_type(p.name)[0] or "image/png"),
                        )
                        for p in valid_refs
                    ]
                else:
                    p = valid_refs[0]
                    files = [
                        (
                            "image",
                            (p.name, stack.enter_context(p.open("rb")), mimetypes.guess_type(p.name)[0] or "image/png"),
                        )
                    ]
                data = {
                    "model": self.image_model,
                    "prompt": prompt,
                    "n": "1",
                    "size": "1024x1024",
                    "background": "transparent",
                }
                return self.session.post(url, headers=headers, files=files, data=data, timeout=self.timeout)

        def call_single():
            p = valid_refs[0]
            mime = mimetypes.guess_type(p.name)[0] or "image/png"
            with p.open("rb") as fp:
                files = {"image": (p.name, fp, mime)}
                data = {
                    "model": self.image_model,
                    "prompt": prompt,
                    "n": "1",
                    "size": "1024x1024",
                }
                return self.session.post(url, headers=headers, files=files, data=data, timeout=self.timeout)

        try:
            resp = self._execute_with_retry(call_multi)
        except ProviderError as e:
            if len(valid_refs) > 1 and "400" in str(e):
                logger.info("Multi-reference edit rejected by endpoint (%s); downgrading to single reference.", e)
                resp = self._execute_with_retry(call_single)
            else:
                raise

        data = resp.json()
        item_data = data["data"][0]
        b64_str = item_data.get("b64_json")
        if not b64_str and "url" in item_data:
            raw_bytes = self.session.get(item_data["url"], timeout=60).content
            output.parent.mkdir(parents=True, exist_ok=True)
            tmp = output.with_suffix(".tmp")
            tmp.write_bytes(raw_bytes)
            tmp.replace(output)
        else:
            self._write_b64_to_file(b64_str, output)
        return output

    def render_native_gif(
        self, prompt: str, output: Path, frames: int = 8, frame_duration_ms: int = 180
    ) -> Path:
        raise NotImplementedError("OpenAIImagesProvider does not support native GIF. Use OpenAINativeGifProvider.")

    def _write_b64_to_file(self, b64_str: str, output: Path) -> None:
        raw_bytes = base64.b64decode(b64_str)
        output.parent.mkdir(parents=True, exist_ok=True)
        tmp = output.with_suffix(".tmp")
        tmp.write_bytes(raw_bytes)
        tmp.replace(output)
