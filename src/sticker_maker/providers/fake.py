"""Deterministic mock provider for offline testing and development."""

from __future__ import annotations

import math
from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageDraw

from .base import (
    ProviderCapabilities,
    ProviderCapabilityError,
    ProviderRateLimitError,
    ProviderAuthError,
    StickerProvider,
)


class FakeStickerProvider(StickerProvider):
    """Generates synthetic transparent images and animations for offline verification."""

    def __init__(
        self,
        can_native_gif: bool = True,
        fail_item_ids: Optional[List[str]] = None,
        simulate_error: Optional[str] = None,
    ) -> None:
        self.can_native_gif = can_native_gif
        self.fail_item_ids = set(fail_item_ids or [])
        self.simulate_error = simulate_error

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            edit_with_reference=True,
            transparent_png=True,
            native_gif=self.can_native_gif,
            gif_max_frames=32,
        )

    def _check_simulation(self, prompt: str) -> None:
        if self.simulate_error == "auth":
            raise ProviderAuthError("Simulated 401 Unauthorized")
        if self.simulate_error == "rate_limit":
            raise ProviderRateLimitError("Simulated 429 Rate Limit")
        for fail_id in self.fail_item_ids:
            if fail_id in prompt:
                raise RuntimeError(f"Simulated failure for item {fail_id}")

    def render_anchor(
        self, reference_paths: List[Path], prompt: str, output: Path
    ) -> Path:
        self._check_simulation(prompt)
        output.parent.mkdir(parents=True, exist_ok=True)
        img = self._create_character_frame(action_offset=0, size=(512, 512))
        img.save(output, format="PNG")
        return output

    def render_static(
        self, reference_paths: List[Path], prompt: str, output: Path
    ) -> Path:
        self._check_simulation(prompt)
        output.parent.mkdir(parents=True, exist_ok=True)
        # Distinct action based on hash of prompt
        h = sum(ord(c) for c in prompt) % 8
        img = self._create_character_frame(action_offset=h, size=(512, 512))
        img.save(output, format="PNG")
        return output

    def render_native_gif(
        self, prompt: str, output: Path, frames: int = 8, frame_duration_ms: int = 180
    ) -> Path:
        if not self.can_native_gif:
            raise ProviderCapabilityError("Native GIF generation not supported by this provider")
        self._check_simulation(prompt)
        output.parent.mkdir(parents=True, exist_ok=True)

        frame_imgs = []
        for i in range(frames):
            frame = self._create_character_frame(action_offset=i, size=(240, 240))
            frame_imgs.append(frame)

        frame_imgs[0].save(
            output,
            format="GIF",
            save_all=True,
            append_images=frame_imgs[1:],
            duration=[frame_duration_ms] * frames,
            loop=0,
            disposal=2,
            transparency=0,
        )
        return output

    def _create_character_frame(self, action_offset: int, size: tuple[int, int]) -> Image.Image:
        """Create a cute character with motion offset on a transparent background."""
        w, h = size
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Scale coordinates to size
        scale = w / 240.0
        cx, cy = w / 2.0, h / 2.0

        # Motion bobbing
        bob = math.sin(action_offset * math.pi / 4.0) * (3.0 * scale)

        # Body / Head (cream color, soft rounded)
        head_radius = 50.0 * scale
        head_bbox = [cx - head_radius, cy - head_radius + bob, cx + head_radius, cy + head_radius + bob]
        draw.ellipse(head_bbox, fill=(255, 246, 234, 255), outline=(152, 124, 123, 255), width=int(3 * scale))

        # Ears
        ear_offset = 35.0 * scale
        # Left ear
        draw.polygon(
            [
                (cx - ear_offset, cy - head_radius + 15 * scale + bob),
                (cx - ear_offset - 15 * scale, cy - head_radius - 20 * scale + bob),
                (cx - ear_offset + 10 * scale, cy - head_radius - 5 * scale + bob),
            ],
            fill=(255, 246, 234, 255),
            outline=(152, 124, 123, 255),
        )
        # Right ear (with distinct gray patch)
        draw.polygon(
            [
                (cx + ear_offset, cy - head_radius + 15 * scale + bob),
                (cx + ear_offset + 15 * scale, cy - head_radius - 20 * scale + bob),
                (cx + ear_offset - 10 * scale, cy - head_radius - 5 * scale + bob),
            ],
            fill=(200, 200, 205, 255),
            outline=(152, 124, 123, 255),
        )

        # Eyes (moving/blinking with offset)
        eye_y = cy - 5.0 * scale + bob
        if action_offset in (3, 4):
            # Closed curved happy eyes
            draw.arc([cx - 25 * scale, eye_y - 5 * scale, cx - 10 * scale, eye_y + 5 * scale], start=0, end=180, fill=(152, 124, 123, 255), width=int(2 * scale))
            draw.arc([cx + 10 * scale, eye_y - 5 * scale, cx + 25 * scale, eye_y + 5 * scale], start=0, end=180, fill=(152, 124, 123, 255), width=int(2 * scale))
        else:
            # Open round eyes
            draw.ellipse([cx - 24 * scale, eye_y - 6 * scale, cx - 14 * scale, eye_y + 6 * scale], fill=(80, 70, 70, 255))
            draw.ellipse([cx + 14 * scale, eye_y - 6 * scale, cx + 24 * scale, eye_y + 6 * scale], fill=(80, 70, 70, 255))
            # Catchlights
            draw.ellipse([cx - 22 * scale, eye_y - 4 * scale, cx - 18 * scale, eye_y], fill=(255, 255, 255, 255))
            draw.ellipse([cx + 16 * scale, eye_y - 4 * scale, cx + 20 * scale, eye_y], fill=(255, 255, 255, 255))

        # Nose & Mouth
        nose_y = cy + 8.0 * scale + bob
        draw.polygon([(cx - 4 * scale, nose_y), (cx + 4 * scale, nose_y), (cx, nose_y + 4 * scale)], fill=(247, 189, 201, 255))

        # Blushing cheeks
        blush_alpha = int(140 + 80 * math.sin(action_offset * math.pi / 4.0))
        draw.ellipse([cx - 38 * scale, cy + 6 * scale + bob, cx - 22 * scale, cy + 18 * scale + bob], fill=(247, 189, 201, blush_alpha))
        draw.ellipse([cx + 22 * scale, cy + 6 * scale + bob, cx + 38 * scale, cy + 18 * scale + bob], fill=(247, 189, 201, blush_alpha))

        # Hand wave gesture
        hand_wave = math.sin(action_offset * math.pi / 2.0) * (12.0 * scale)
        hand_x = cx + head_radius + 5.0 * scale
        hand_y = cy + bob + hand_wave
        draw.ellipse([hand_x - 10 * scale, hand_y - 10 * scale, hand_x + 10 * scale, hand_y + 10 * scale], fill=(255, 246, 234, 255), outline=(152, 124, 123, 255), width=int(2 * scale))

        return img
