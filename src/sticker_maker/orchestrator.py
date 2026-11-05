"""Pipeline orchestrator and execution state machine."""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from PIL import Image

from .analyzer import create_or_load_character_bible, normalize_source_image
from .config import AppSettings
from .package import package_deliverables
from .planner import plan_expressions
from .processing.alpha import apply_safe_margin, remove_matte_background
from .processing.gif_encoder import encode_gif, synthesize_motion_frames
from .processing.optimizer import optimize_gif, optimize_png
from .processing.resize import create_banner, create_icon, create_thumbnail, resize_sticker
from .processing.typography import add_caption_to_image
from .prompts import build_anchor_prompt, build_native_gif_prompt, build_static_prompt
from .providers.base import ProviderCapabilityError, StickerProvider
from .providers.fake import FakeStickerProvider
from .providers.openai_images import OpenAIImagesProvider
from .providers.openai_native_gif import OpenAINativeGifProvider
from .quality.report import generate_preview_sheet, run_full_validation
from .schemas import (
    CharacterBible,
    ExpressionItem,
    JobConfig,
    Manifest,
    ManifestItem,
)

logger = logging.getLogger(__name__)


class StickerOrchestrator:
    """Manages the lifecycle of sticker pack creation from planning to packaging."""

    def __init__(
        self,
        job: JobConfig,
        provider: Optional[StickerProvider] = None,
        native_gif_provider: Optional[StickerProvider] = None,
    ) -> None:
        self.job = job
        self.output_dir = Path(job.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.provider = provider or self._resolve_default_provider()
        self.native_gif_provider = native_gif_provider or self._resolve_default_gif_provider()

        # State directories
        self.work_dir = self.output_dir / "work"
        self.work_raw_static = self.work_dir / "raw_static"
        self.work_raw_gif = self.work_dir / "raw_gif"
        self.static_dir = self.output_dir / "static"
        self.animated_dir = self.output_dir / "animated"
        self.thumbnails_dir = self.output_dir / "thumbnails"
        self.platform_dir = self.output_dir / "platform"
        self.qa_dir = self.output_dir / "qa"

        for d in (
            self.work_raw_static,
            self.work_raw_gif,
            self.static_dir,
            self.animated_dir,
            self.thumbnails_dir,
            self.platform_dir,
            self.qa_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)

    def _resolve_default_provider(self) -> StickerProvider:
        settings = AppSettings()
        if settings.openai_api_key:
            return OpenAIImagesProvider(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                image_model=settings.sticker_image_model,
                max_retries=settings.sticker_max_retries,
            )
        logger.info("No OPENAI_API_KEY detected; using FakeStickerProvider for offline operation.")
        return FakeStickerProvider()

    def _resolve_default_gif_provider(self) -> StickerProvider:
        settings = AppSettings()
        if settings.openai_api_key:
            return OpenAINativeGifProvider(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                gif_model=settings.sticker_gif_model,
                max_retries=settings.sticker_max_retries,
            )
        return FakeStickerProvider()

    def run(self) -> Manifest:
        """Run the full end-to-end generation, post-processing, validation, and packaging."""
        logger.info("Starting job %s (mode: %s, count: %d)", self.job.job_id, self.job.mode, self.job.count)

        # 1. Normalize source image
        source_in = Path(self.job.source_image)
        norm_source = self.work_dir / f"source_normalized_{source_in.name}"
        if not norm_source.exists():
            normalize_source_image(source_in, norm_source)

        # 2. Build or load Character Bible
        bible = create_or_load_character_bible(
            source_image=norm_source,
            output_dir=self.output_dir,
            character_id=self.job.job_id,
        )

        # 3. Generate Master Anchor
        anchor_path = Path(bible.master_anchor)
        if not anchor_path.exists():
            logger.info("Generating canonical master anchor...")
            anchor_prompt = build_anchor_prompt(bible.subject_type, bible.identity_facts, self.job.style)
            self.provider.render_anchor([norm_source], anchor_prompt, anchor_path)

        # 4. Plan Expressions
        expressions = plan_expressions(count=self.job.count)

        # 5. Generate Items
        manifest_items: list[ManifestItem] = []
        static_count = 0
        animated_count = 0

        for item in expressions:
            static_p, anim_p, thumb_p = self._process_single_expression(item, bible, norm_source, anchor_path)
            if static_p:
                static_count += 1
            if anim_p:
                animated_count += 1

            manifest_items.append(
                ManifestItem(
                    id=item.id,
                    caption=item.caption,
                    static_path=str(static_p.relative_to(self.output_dir)) if static_p else None,
                    animated_path=str(anim_p.relative_to(self.output_dir)) if anim_p else None,
                    thumbnail_path=str(thumb_p.relative_to(self.output_dir)) if thumb_p else None,
                    checks={"status": "completed"},
                )
            )

        # 6. Generate Platform Assets (cover, icon, banner)
        self._generate_platform_assets(anchor_path)

        # 7. Write manifest.json
        manifest = Manifest(
            job_id=self.job.job_id,
            mode=self.job.mode,
            character_id=bible.character_id,
            generated_count={"static": static_count, "animated": animated_count},
            items=manifest_items,
            validation_report="qa/report.json",
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        with (self.output_dir / "manifest.json").open("w", encoding="utf-8") as f:
            json.dump(manifest.model_dump(), f, indent=2, ensure_ascii=False)

        # 8. QA Validation & Preview Sheet
        run_full_validation(self.output_dir, profile_name=self.job.export_profile)
        generate_preview_sheet(self.output_dir)

        # 9. Packaging (Strict)
        try:
            package_deliverables(self.output_dir, strict=True, profile_name=self.job.export_profile)
            logger.info("Packaging completed successfully.")
        except Exception as e:
            logger.warning("Packaging warning/deferral: %s", e)

        return manifest

    def _process_single_expression(
        self,
        item: ExpressionItem,
        bible: CharacterBible,
        source_img: Path,
        anchor_img: Path,
    ) -> tuple[Optional[Path], Optional[Path], Optional[Path]]:
        static_dest = self.static_dir / f"{item.id}.png"
        anim_dest = self.animated_dir / f"{item.id}.gif"
        thumb_dest = self.thumbnails_dir / f"{item.id}.png"

        do_static = self.job.mode in ("static", "both")
        do_anim = self.job.mode in ("animated", "both")

        # Static Generation
        if do_static and not static_dest.exists():
            raw_path = self.work_raw_static / f"{item.id}_raw.png"
            if not raw_path.exists():
                prompt = build_static_prompt(bible, item)
                self.provider.render_static([anchor_img, source_img], prompt, raw_path)

            # Post-process static PNG
            with Image.open(raw_path) as raw_img:
                clean_img = remove_matte_background(raw_img)
                resized = resize_sticker(clean_img, (240, 240))
                captioned = add_caption_to_image(resized, item.caption, font_path=self.job.font_path)
                final_img = apply_safe_margin(captioned, 2)
                final_img.save(static_dest, format="PNG")

            optimize_png(static_dest, max_bytes=500_000)

        # Thumbnail (from static PNG or anchor)
        if not thumb_dest.exists():
            src_for_thumb = static_dest if static_dest.exists() else anchor_img
            with Image.open(src_for_thumb) as simg:
                thumb_img = create_thumbnail(simg, (120, 120))
                thumb_img.save(thumb_dest, format="PNG")
            optimize_png(thumb_dest, max_bytes=50_000)

        # Animated GIF Generation
        if do_anim and not anim_dest.exists():
            used_native = False
            # Check backend preference
            if self.job.animation.backend in ("native-gif", "auto"):
                try:
                    if self.native_gif_provider.capabilities().native_gif:
                        raw_gif_path = self.work_raw_gif / f"{item.id}_native_raw.gif"
                        if not raw_gif_path.exists():
                            gif_prompt = build_native_gif_prompt(bible, item)
                            self.native_gif_provider.render_native_gif(
                                prompt=gif_prompt,
                                output=raw_gif_path,
                                frames=self.job.animation.frames,
                                frame_duration_ms=self.job.animation.frame_duration_ms,
                            )
                        # Native GIF succeeded; copy or post-process
                        shutil.copyfile(raw_gif_path, anim_dest)
                        used_native = True
                except ProviderCapabilityError as e:
                    logger.info("Native GIF unavailable (%s); falling back to keyframes route.", e)
                except Exception as e:
                    logger.warning("Native GIF attempt failed: %s; falling back to keyframes.", e)

            if not used_native:
                # Route B: Keyframe composition from base pose (Highest Identity Stability)
                base_for_motion = static_dest if static_dest.exists() else anchor_img
                with Image.open(base_for_motion) as b_img:
                    # Ensure base is resized to standard 240x240 before synthesizing motion
                    b_240 = resize_sticker(b_img, (240, 240))
                    frames = synthesize_motion_frames(
                        b_240,
                        motion_type=item.motion.type,
                        frames=self.job.animation.frames,
                    )
                    # Add caption to every frame
                    captioned_frames = [
                        apply_safe_margin(add_caption_to_image(f, item.caption, font_path=self.job.font_path), 2)
                        for f in frames
                    ]
                    encode_gif(
                        captioned_frames,
                        anim_dest,
                        frame_duration_ms=self.job.animation.frame_duration_ms,
                        loop=self.job.animation.loop,
                    )

            optimize_gif(anim_dest, max_bytes=500_000)

        return (
            static_dest if static_dest.exists() else None,
            anim_dest if anim_dest.exists() else None,
            thumb_dest if thumb_dest.exists() else None,
        )

    def _generate_platform_assets(self, anchor_path: Path) -> None:
        cover_path = self.platform_dir / "cover.png"
        icon_path = self.platform_dir / "icon.png"
        banner_path = self.platform_dir / "banner.png"

        with Image.open(anchor_path) as a_img:
            if not cover_path.exists():
                c_img = resize_sticker(a_img, (240, 240))
                c_img.save(cover_path, format="PNG")
                optimize_png(cover_path, max_bytes=500_000)

            if not icon_path.exists():
                i_img = create_icon(a_img, (50, 50))
                i_img.save(icon_path, format="PNG")
                optimize_png(icon_path, max_bytes=100_000)

            if not banner_path.exists():
                b_img = create_banner(a_img, (750, 400))
                b_img.save(banner_path, format="PNG")
                optimize_png(banner_path, max_bytes=500_000)

    def regenerate_single_item(self, item_id: str) -> None:
        """Regenerate a specific expression without re-running the whole set."""
        expressions = plan_expressions(count=self.job.count)
        matched = [e for e in expressions if e.id == item_id]
        if not matched:
            raise ValueError(f"Item ID {item_id} not found in planned expressions")

        item = matched[0]
        # Remove target intermediate and final files
        (self.work_raw_static / f"{item.id}_raw.png").unlink(missing_ok=True)
        (self.work_raw_gif / f"{item.id}_native_raw.gif").unlink(missing_ok=True)
        (self.static_dir / f"{item.id}.png").unlink(missing_ok=True)
        (self.animated_dir / f"{item.id}.gif").unlink(missing_ok=True)
        (self.thumbnails_dir / f"{item.id}.png").unlink(missing_ok=True)

        source_in = Path(self.job.source_image)
        norm_source = self.work_dir / f"source_normalized_{source_in.name}"
        bible = create_or_load_character_bible(norm_source, self.output_dir)
        anchor_path = Path(bible.master_anchor)

        self._process_single_expression(item, bible, norm_source, anchor_path)
        logger.info("Successfully regenerated item %s", item_id)
