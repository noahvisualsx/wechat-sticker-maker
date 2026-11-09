"""Deterministic mock provider for offline testing and development (real-person portrait cutouts)."""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageDraw

from ..styles import hex_to_rgba, resolve_style_preset
from .base import (
    ProviderCapabilities,
    ProviderCapabilityError,
    ProviderRateLimitError,
    ProviderAuthError,
    StickerProvider,
)


class FakeStickerProvider(StickerProvider):
    """Generates synthetic transparent human-portrait sticker images and animations for offline verification."""

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

    def _extract_style_from_prompt(self, prompt: str) -> str:
        m = re.search(r"Style ID:\s*([a-zA-Z0-9_\-]+)", prompt)
        if m:
            return m.group(1)
        return "real-cutout"

    def render_anchor(
        self, reference_paths: List[Path], prompt: str, output: Path
    ) -> Path:
        self._check_simulation(prompt)
        style_id = self._extract_style_from_prompt(prompt)
        output.parent.mkdir(parents=True, exist_ok=True)
        img = self._create_character_frame(action_offset=0, size=(512, 512), style_id=style_id)
        img.save(output, format="PNG")
        return output

    def render_static(
        self, reference_paths: List[Path], prompt: str, output: Path
    ) -> Path:
        self._check_simulation(prompt)
        style_id = self._extract_style_from_prompt(prompt)
        output.parent.mkdir(parents=True, exist_ok=True)
        if "2x2 ANIMATION SPRITE SHEET" in prompt:
            sheet = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
            offsets = [(0, 0, 0), (512, 0, 1), (0, 512, 3), (512, 512, 2)]
            for qx, qy, act_off in offsets:
                cell = self._create_character_frame(action_offset=act_off, size=(512, 512), style_id=style_id)
                sheet.paste(cell, (qx, qy), cell)
            sheet.save(output, format="PNG")
            return output

        # Distinct action based on hash of prompt
        h = sum(ord(c) for c in prompt) % 8
        img = self._create_character_frame(action_offset=h, size=(512, 512), style_id=style_id)
        img.save(output, format="PNG")
        return output

    def render_native_gif(
        self, prompt: str, output: Path, frames: int = 8, frame_duration_ms: int = 180
    ) -> Path:
        if not self.can_native_gif:
            raise ProviderCapabilityError("Native GIF generation not supported by this provider")
        self._check_simulation(prompt)
        style_id = self._extract_style_from_prompt(prompt)
        output.parent.mkdir(parents=True, exist_ok=True)

        frame_imgs = []
        for i in range(frames):
            frame = self._create_character_frame(action_offset=i, size=(512, 512), style_id=style_id)
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

    def _create_character_frame(
        self,
        action_offset: int,
        size: tuple[int, int],
        style_id: str = "real-cutout",
    ) -> Image.Image:
        """Create a real-person portrait cutout with multi-frame hand/eye motion and style-specific lighting."""
        w, h = size
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        preset = resolve_style_preset(style_id)
        pal = preset.default_palette or ["#FFE5D9", "#F4A261", "#3D405B"]
        accent_fill = hex_to_rgba(pal[min(1, len(pal) - 1)], 255)
        scale = w / 240.0
        cx, cy = w / 2.0, h / 2.0
        bob = 0.0  # Keep lower torso anchored in place

        return self._create_human_portrait_frame(
            img=img,
            draw=draw,
            cx=cx,
            cy=cy,
            scale=scale,
            bob=bob,
            action_offset=action_offset,
            style_id=style_id,
            accent_fill=accent_fill,
        )

    def _create_human_portrait_frame(
        self,
        img: Image.Image,
        draw: ImageDraw.ImageDraw,
        cx: float,
        cy: float,
        scale: float,
        bob: float,
        action_offset: int,
        style_id: str,
        accent_fill: tuple[int, int, int, int],
    ) -> Image.Image:
        """Render a synthetic human portrait cutout for real-* styles in offline mode."""
        is_bobble = style_id == "real-bobblehead"
        is_mono = style_id == "real-high-contrast"
        head_rx = (52.0 if is_bobble else 42.0) * scale
        head_ry = (56.0 if is_bobble else 46.0) * scale
        head_cy = cy - (8.0 if is_bobble else 12.0) * scale + bob

        if is_mono:
            skin_fill = (242, 242, 242, 255)
            skin_outline = (35, 35, 35, 255)
            hair_fill = (20, 20, 20, 255)
            shirt_fill = (90, 90, 90, 255)
        elif style_id == "real-vintage-ccd":
            skin_fill = (255, 224, 198, 255)
            skin_outline = (148, 108, 90, 255)
            hair_fill = (52, 38, 34, 255)
            shirt_fill = accent_fill
        else:
            skin_fill = (255, 228, 212, 255)
            skin_outline = (160, 120, 105, 255)
            hair_fill = (45, 38, 42, 255)
            shirt_fill = accent_fill

        # Shoulders / Torso (anchored lower torso)
        shoulder_w = (34.0 if is_bobble else 54.0) * scale
        shoulder_top = head_cy + head_ry - 6.0 * scale
        shoulder_bot = head_cy + head_ry + (32.0 if is_bobble else 44.0) * scale
        draw.pieslice(
            [cx - shoulder_w, shoulder_top, cx + shoulder_w, shoulder_bot + 20 * scale],
            start=180,
            end=360,
            fill=shirt_fill,
            outline=skin_outline,
            width=max(1, int(2 * scale)),
        )

        # Back hair silhouette
        draw.ellipse(
            [
                cx - head_rx - 6 * scale,
                head_cy - head_ry - 6 * scale,
                cx + head_rx + 6 * scale,
                head_cy + head_ry * 0.65,
            ],
            fill=hair_fill,
        )

        # Human Ears
        ear_r = 9.0 * scale
        draw.ellipse(
            [cx - head_rx - ear_r * 0.6, head_cy - ear_r, cx - head_rx + ear_r * 0.6, head_cy + ear_r],
            fill=skin_fill,
            outline=skin_outline,
        )
        draw.ellipse(
            [cx + head_rx - ear_r * 0.6, head_cy - ear_r, cx + head_rx + ear_r * 0.6, head_cy + ear_r],
            fill=skin_fill,
            outline=skin_outline,
        )

        # Face oval
        draw.ellipse(
            [cx - head_rx, head_cy - head_ry, cx + head_rx, head_cy + head_ry],
            fill=skin_fill,
            outline=skin_outline,
            width=max(1, int(2 * scale)),
        )

        # Front bangs / Hairline
        draw.chord(
            [cx - head_rx, head_cy - head_ry - 4 * scale, cx + head_rx, head_cy - head_ry * 0.15],
            start=180,
            end=360,
            fill=hair_fill,
        )

        # Eyebrows
        brow_y = head_cy - 12.0 * scale
        draw.arc([cx - 26 * scale, brow_y - 4 * scale, cx - 8 * scale, brow_y + 4 * scale], start=190, end=350, fill=hair_fill, width=max(1, int(2 * scale)))
        draw.arc([cx + 8 * scale, brow_y - 4 * scale, cx + 26 * scale, brow_y + 4 * scale], start=190, end=350, fill=hair_fill, width=max(1, int(2 * scale)))

        # Eyes (blinking across action_offset frames)
        eye_y = head_cy - 2.0 * scale
        if action_offset in (1, 3, 4):
            draw.arc([cx - 24 * scale, eye_y - 4 * scale, cx - 10 * scale, eye_y + 4 * scale], start=0, end=180, fill=hair_fill, width=max(1, int(2 * scale)))
            draw.arc([cx + 10 * scale, eye_y - 4 * scale, cx + 24 * scale, eye_y + 4 * scale], start=0, end=180, fill=hair_fill, width=max(1, int(2 * scale)))
        else:
            draw.ellipse([cx - 23 * scale, eye_y - 6 * scale, cx - 11 * scale, eye_y + 6 * scale], fill=(50, 40, 38, 255))
            draw.ellipse([cx + 11 * scale, eye_y - 6 * scale, cx + 23 * scale, eye_y + 6 * scale], fill=(50, 40, 38, 255))
            draw.ellipse([cx - 20 * scale, eye_y - 4 * scale, cx - 16 * scale, eye_y], fill=(255, 255, 255, 255))
            draw.ellipse([cx + 14 * scale, eye_y - 4 * scale, cx + 18 * scale, eye_y], fill=(255, 255, 255, 255))

        # Nose & Smiling Mouth
        nose_y = head_cy + 8.0 * scale
        draw.line([(cx, nose_y - 4 * scale), (cx - 2 * scale, nose_y + 2 * scale)], fill=skin_outline, width=max(1, int(1.5 * scale)))
        mouth_y = head_cy + 16.0 * scale
        lip_color = (60, 60, 60, 255) if is_mono else (210, 95, 95, 255)
        draw.arc([cx - 10 * scale, mouth_y - 4 * scale, cx + 10 * scale, mouth_y + 8 * scale], start=10, end=170, fill=lip_color, width=max(1, int(2.5 * scale)))

        # Cheeks
        if not is_mono:
            blush_alpha = int(110 + 70 * math.sin(action_offset * math.pi / 4.0))
            draw.ellipse([cx - 34 * scale, head_cy + 6 * scale, cx - 20 * scale, head_cy + 16 * scale], fill=(255, 150, 165, blush_alpha))
            draw.ellipse([cx + 20 * scale, head_cy + 6 * scale, cx + 34 * scale, head_cy + 16 * scale], fill=(255, 150, 165, blush_alpha))

        if style_id == "real-purikura":
            sx, sy = cx - head_rx - 8 * scale, head_cy - 25 * scale
            draw.ellipse([sx - 5 * scale, sy - 5 * scale, sx + 5 * scale, sy + 5 * scale], fill=(255, 220, 100, 235))

        # Waving Arm + Hand (connected to right shoulder, zero floating island)
        hand_wave_x = math.sin(action_offset * math.pi / 2.0) * (8.0 * scale)
        hand_wave_y = math.cos(action_offset * math.pi / 2.0) * (10.0 * scale)
        hx = cx + head_rx + 8.0 * scale + hand_wave_x
        hy = head_cy + 18.0 * scale + hand_wave_y
        sx0 = cx + shoulder_w * 0.65
        sy0 = shoulder_top + 14.0 * scale
        draw.line([(sx0, sy0), (hx, hy)], fill=shirt_fill, width=max(3, int(11 * scale)))
        draw.ellipse([hx - 10 * scale, hy - 10 * scale, hx + 10 * scale, hy + 10 * scale], fill=skin_fill, outline=skin_outline, width=max(1, int(2 * scale)))

        return img
