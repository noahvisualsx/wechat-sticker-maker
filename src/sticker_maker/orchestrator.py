"""Pipeline orchestrator: plan → AI keyframes → master composition (multilingual captions &
speech bubbles) → multi-platform export (WeChat, QQ, Douyin, Xiaohongshu, Soul, Weibo, Telegram,
WhatsApp, LINE, KakaoTalk, Discord, Slack, iMessage, Signal, GIPHY, Instagram, TikTok, X ...)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image

from .analyzer import create_or_load_character_bible, normalize_source_image
from .config import AppSettings
from .duo import DUO_CATEGORIES, build_duo_sprite_sheet_prompt, build_duo_static_prompt
from .pets import PET_CATEGORIES, build_pet_sprite_sheet_prompt, build_pet_static_prompt
from .exporters import (
    MasterAsset,
    PlatformExportResult,
    export_all_platforms,
    load_master_assets,
    master_dir,
    save_master_asset,
)
from .i18n import load_captions_file
from .package import package_deliverables
from .planner import language_issues, localize_meme, plan_pack, resolve_text_spec
from .platforms import load_platform_profiles, resolve_platforms
from .processing.compose import compose_sticker_frames
from .processing.gif_encoder import load_gif_frames, slice_sprite_sheet, synthesize_motion_frames
from .prompts import (
    build_anchor_prompt,
    build_keyframe_prompt,
    build_native_gif_prompt,
    build_sprite_sheet_prompt,
    build_static_prompt,
)
from .styles import resolve_style_preset
from .providers.base import (
    ProviderAuthError,
    ProviderCapabilityError,
    ProviderQuotaError,
    StickerProvider,
)
from .providers.fake import FakeStickerProvider
from .providers.gemini_images import GeminiImagesProvider
from .providers.openai_images import OpenAIImagesProvider
from .providers.openai_native_gif import OpenAINativeGifProvider
from .quality.report import generate_preview_html, generate_preview_sheet, run_full_validation
from .schemas import (
    CharacterBible,
    ExpressionItem,
    JobConfig,
    Manifest,
    ManifestItem,
    TextSpec,
)

logger = logging.getLogger(__name__)

NUM_AI_KEYFRAMES = 4


class StickerOrchestrator:
    """Manages the lifecycle of sticker pack creation from planning to multi-platform packaging."""

    def __init__(
        self,
        job: JobConfig,
        provider: Optional[StickerProvider] = None,
        native_gif_provider: Optional[StickerProvider] = None,
        max_parallel: Optional[int] = None,
    ) -> None:
        self.job = job
        self.state = "CREATED"
        self.output_dir = Path(job.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.platforms = resolve_platforms(job.platforms)
        self.legacy_wechat = "wechat" in self.platforms

        settings = AppSettings()
        self.max_parallel = max(1, max_parallel if max_parallel is not None else settings.sticker_max_parallel)

        self.provider = provider or self._resolve_default_provider()
        self.native_gif_provider = native_gif_provider or self._resolve_default_gif_provider()

        self.work_dir = self.output_dir / "work"
        self.work_raw_static = self.work_dir / "raw_static"
        self.work_raw_gif = self.work_dir / "raw_gif"
        self.work_master = master_dir(self.output_dir)
        self.static_dir = self.output_dir / "static"
        self.animated_dir = self.output_dir / "animated"
        self.thumbnails_dir = self.output_dir / "thumbnails"
        self.platform_dir = self.output_dir / "platform"
        self.qa_dir = self.output_dir / "qa"

        dirs = [self.work_raw_static, self.work_raw_gif, self.work_master, self.qa_dir]
        if self.legacy_wechat:
            dirs += [self.static_dir, self.animated_dir, self.thumbnails_dir, self.platform_dir]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        self.custom_captions = load_captions_file(job.captions_file)
        self.export_results: Dict[str, PlatformExportResult] = {}

    # ------------------------------------------------------------------ providers

    def _resolve_default_provider(self) -> StickerProvider:
        settings = AppSettings()
        if settings.openai_api_key:
            return OpenAIImagesProvider(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                image_model=settings.sticker_image_model,
                max_retries=settings.sticker_max_retries,
            )
        if settings.gemini_api_key:
            return GeminiImagesProvider(
                api_key=settings.gemini_api_key,
                image_model=settings.gemini_image_model,
                max_retries=settings.sticker_max_retries,
            )
        if settings.ark_api_key:
            return OpenAIImagesProvider(
                api_key=settings.ark_api_key,
                base_url=settings.ark_base_url,
                image_model=settings.ark_image_model,
                max_retries=settings.sticker_max_retries,
            )
        logger.info("No API key detected; using FakeStickerProvider for offline operation.")
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

    def _check_cloud_permission(self) -> None:
        if not self.job.allow_cloud_upload:
            cloud_classes = (OpenAIImagesProvider, OpenAINativeGifProvider, GeminiImagesProvider)
            if isinstance(self.provider, cloud_classes) or isinstance(self.native_gif_provider, cloud_classes):
                raise PermissionError(
                    "Cloud upload is disabled by job configuration (allow_cloud_upload=False). "
                    "Cannot send source image to remote cloud provider."
                )

    def _write_manifest(self, manifest: Manifest) -> None:
        manifest_path = self.output_dir / "manifest.json"
        tmp_path = self.output_dir / "manifest.tmp.json"
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(manifest.model_dump(), f, indent=2, ensure_ascii=False)
        tmp_path.replace(manifest_path)

    def _plan(self) -> List[ExpressionItem]:
        return plan_pack(self.job, strict_counts=self.legacy_wechat)

    @property
    def canvas(self) -> Tuple[int, int]:
        return (self.job.master_size, self.job.master_size)

    # ------------------------------------------------------------------ run

    def run(self, sample_only: bool = False) -> Manifest:
        """Run generation → master composition → multi-platform export → validation → packaging."""
        self._check_cloud_permission()
        logger.info(
            "Starting job %s (mode=%s, count=%d, language=%s, platforms=%s, sample_only=%s)",
            self.job.job_id, self.job.mode, self.job.count, self.job.language, ",".join(self.platforms), sample_only,
        )

        source_in = Path(self.job.source_image)
        norm_source = self.work_dir / f"source_normalized_{source_in.name}"
        if not norm_source.exists():
            normalize_source_image(source_in, norm_source)

        norm_partner: Optional[Path] = None
        if self.job.partner_image:
            partner_in = Path(self.job.partner_image)
            if partner_in.exists():
                norm_partner = self.work_dir / f"partner_normalized_{partner_in.name}"
                if not norm_partner.exists():
                    normalize_source_image(partner_in, norm_partner)
        self.norm_partner = norm_partner
        self.state = "SOURCE_VALIDATED"

        use_vision = isinstance(self.provider, OpenAIImagesProvider) and self.job.allow_cloud_upload
        bible = create_or_load_character_bible(
            source_image=norm_source,
            output_dir=self.output_dir,
            character_id=self.job.job_id,
            subject_type=self.job.subject_type,
            custom_facts=self.job.custom_facts,
            allow_cloud_upload=self.job.allow_cloud_upload,
            use_vision=use_vision,
            style=self.job.style,
        )

        anchor_path = Path(bible.master_anchor)
        if not anchor_path.exists():
            logger.info("Generating canonical master anchor...")
            anchor_prompt = build_anchor_prompt(
                bible.subject_type, bible.identity_facts, style=self.job.style, palette=bible.render_style.palette,
            )
            anchor_refs = [norm_source] + ([norm_partner] if norm_partner else [])
            self.provider.render_anchor(anchor_refs, anchor_prompt, anchor_path)
        self.state = "CHARACTER_READY"

        expressions = self._plan()
        if sample_only:
            expressions = expressions[:2]
        if not self.job.resume:
            for idx_r, exp_r in enumerate(expressions, 1):
                self._delete_item_outputs(exp_r, idx_r)
        issues = language_issues(expressions, self.job, self.custom_captions)
        if issues:
            raise ValueError(
                f"Single-language check failed for language '{self.job.language}' "
                f"({len(issues)} issue(s)); each sticker must use exactly one language:\n  - "
                + "\n  - ".join(issues[:20])
            )
        self.state = "PLANNED"
        self.state = "RENDERING_STATIC" if self.job.mode != "animated" else "RENDERING_ANIMATED"

        def process_entry(idx_item: Tuple[int, ExpressionItem]) -> Tuple[ManifestItem, Optional[MasterAsset]]:
            idx, item = idx_item
            force_static_only = sample_only and idx >= 1 and self.job.mode == "both"
            try:
                spec, asset = self._process_single_expression(
                    item, idx + 1, bible, norm_source, anchor_path,
                    override_mode="static" if force_static_only else None,
                )
                return self._manifest_item(item, spec, asset), asset
            except (ProviderAuthError, ProviderQuotaError, PermissionError):
                raise
            except Exception as e:
                logger.error("Failed generating expression %s: %s", item.id, e)
                return (
                    ManifestItem(
                        id=item.id, caption=item.caption, status="FAILED", error=str(e),
                        category=item.category, checks={"structural": "fail", "visual": "failed"},
                    ),
                    None,
                )

        indexed = list(enumerate(expressions))
        if self.max_parallel > 1 and len(indexed) > 1:
            with ThreadPoolExecutor(max_workers=self.max_parallel) as pool:
                results = list(pool.map(process_entry, indexed))
        else:
            results = [process_entry(pair) for pair in indexed]

        manifest_items = [r[0] for r in results]
        masters = [r[1] for r in results if r[1] is not None]
        failed_items = [m for m in manifest_items if m.status == "FAILED"]

        # Multi-platform export
        self.state = "EXPORTING"
        do_package = not sample_only and not failed_items
        self.export_results = export_all_platforms(
            self.output_dir, self.platforms, masters, style=self.job.style, language=self.job.language,
            pack_title=self.job.pack_title, font_path=self.job.font_path, skip_existing=True,
            package=do_package, with_showcase=not sample_only,
        )
        self._attach_exports(manifest_items)

        if not self.job.keep_source and norm_source.exists():
            norm_source.unlink(missing_ok=True)

        if len(failed_items) == len(manifest_items) and manifest_items:
            self.state = "FAILED"
        elif failed_items:
            self.state = "PARTIAL"
        elif sample_only:
            self.state = "SAMPLE_COMPLETED"
        else:
            self.state = "COMPLETED"

        manifest = Manifest(
            job_id=self.job.job_id,
            mode=self.job.mode,
            character_id=bible.character_id,
            state=self.state,
            generated_count={
                "static": sum(1 for m in manifest_items if m.static_path),
                "animated": sum(1 for m in manifest_items if m.animated_path),
            },
            items=manifest_items,
            validation_report="qa/report.json",
            created_at=datetime.now(timezone.utc).isoformat(),
            language=self.job.language,
            platforms=self.platforms,
            platform_reports={
                pid: str(r.report_path.relative_to(self.output_dir)) for pid, r in self.export_results.items() if r.report_path
            },
        )
        self._write_manifest(manifest)

        self.state = "VALIDATING"
        run_full_validation(self.output_dir, profile_name=self.job.export_profile)
        generate_preview_sheet(self.output_dir, files=self._preview_files(masters))

        # Multi-language zero-extra-cost pack generation from the same raw AI cutouts
        if self.job.languages:
            self._render_extra_language_packs(expressions, sample_only=sample_only)

        generate_preview_html(self.output_dir, manifest.model_dump())

        if do_package and self.legacy_wechat:
            self.state = "PACKAGING"
            try:
                package_deliverables(self.output_dir, strict=True, profile_name=self.job.export_profile)
                logger.info("WeChat packaging completed successfully.")
            except Exception as e:
                logger.warning("Packaging warning/deferral: %s", e)
        if do_package:
            self.state = "COMPLETED"

        if manifest.state == "FAILED":
            first_err = failed_items[0].error if failed_items else "All items failed"
            raise RuntimeError(f"All sticker items failed to generate. First error: {first_err}")
        return manifest

    def _render_extra_language_packs(self, expressions: List[ExpressionItem], sample_only: bool = False) -> None:
        """Re-compose already-generated raw AI frames into separate single-language packs (packs/<lang>/)."""
        from .i18n import normalize_language

        preset = resolve_style_preset(self.job.style)
        font = self.job.font_path
        anim_cfg = self.job.animation
        for raw_lang in self.job.languages or []:
            lang = normalize_language(raw_lang)
            pack_dir = self.output_dir / "packs" / lang
            pack_dir.mkdir(parents=True, exist_ok=True)
            lang_job = self.job.model_copy(update={"language": lang, "output_dir": str(pack_dir)})
            lang_masters: List[MasterAsset] = []
            lang_manifest_items: List[ManifestItem] = []

            for idx, item in enumerate(expressions, 1):
                force_static = sample_only and idx >= 2 and lang_job.mode == "both"
                eff_mode = "static" if force_static else lang_job.mode
                do_static = eff_mode in ("static", "both")
                do_anim = eff_mode in ("animated", "both")
                spec = resolve_text_spec(item, lang_job, self.custom_captions)
                meme = localize_meme(item, lang_job, self.custom_captions)

                static_master: Optional[Image.Image] = None
                raw_static = self.work_raw_static / f"{item.id}_raw.png"
                if do_static and raw_static.exists():
                    with Image.open(raw_static) as raw_img:
                        static_master = compose_sticker_frames(
                            [raw_img.convert("RGBA")], spec, preset, self.canvas, 1, font,
                            meme=meme, matting=self.job.matting,
                        )[0]

                frames: Optional[List[Image.Image]] = None
                frame_ms = anim_cfg.frame_duration_ms
                if do_anim:
                    sheet_path = self.work_raw_gif / f"{item.id}_sheet_raw.png"
                    if sheet_path.exists():
                        with Image.open(sheet_path) as sheet:
                            cells = slice_sprite_sheet(sheet)
                        frames = compose_sticker_frames(
                            cells, spec, preset, self.canvas, anim_cfg.frames, font,
                            meme=meme, matting=self.job.matting,
                        )
                    elif static_master is not None:
                        frames = synthesize_motion_frames(static_master, motion_type=item.motion.type, frames=anim_cfg.frames)

                asset = save_master_asset(
                    pack_dir, item.id, idx, spec.caption or spec.bubble_text, static_master, frames, frame_ms,
                    extra_meta={"language": spec.language, "text_layout": spec.layout, "category": item.category},
                )
                lang_masters.append(asset)
                lang_manifest_items.append(
                    ManifestItem(
                        id=item.id,
                        caption=spec.caption or spec.bubble_text or item.caption,
                        static_path=str(asset.static_path.relative_to(pack_dir)) if asset.static_path else None,
                        animated_path=str(asset.anim_path.relative_to(pack_dir)) if asset.anim_path else None,
                        status="SUCCESS",
                        checks={"structural": "pass", "visual": "reviewed"},
                        category=item.category,
                        language=spec.language,
                        text_layout=spec.layout,
                        bubble_text=spec.bubble_text or None,
                    )
                )

            export_res = export_all_platforms(
                pack_dir, self.platforms, lang_masters, style=self.job.style, language=lang,
                pack_title=self.job.pack_title, font_path=font, skip_existing=False,
                package=not sample_only, with_showcase=not sample_only,
            )
            if "wechat" in export_res:
                wx_res = export_res["wechat"]
                for m in lang_manifest_items:
                    files = {k: str(Path(v).relative_to(pack_dir)) for k, v in wx_res.item_files(m.id).items()}
                    m.static_path = files.get("main:static") or m.static_path
                    m.animated_path = files.get("main:animated") or m.animated_path
            generate_preview_html(
                pack_dir,
                {
                    "job_id": f"{self.job.job_id}-{lang}",
                    "language": lang,
                    "items": [m.model_dump() for m in lang_manifest_items],
                },
            )

    # ------------------------------------------------------------------ helpers

    def _preview_files(self, masters: List[MasterAsset]) -> Optional[List[Path]]:
        if self.legacy_wechat:
            return None
        return [m.static_path for m in masters if m.static_path] or None

    def _manifest_item(self, item: ExpressionItem, spec: TextSpec, asset: MasterAsset) -> ManifestItem:
        return ManifestItem(
            id=item.id,
            caption=spec.caption or spec.bubble_text or item.caption,
            static_path=str(asset.static_path.relative_to(self.output_dir)) if asset.static_path else None,
            animated_path=str(asset.anim_path.relative_to(self.output_dir)) if asset.anim_path else None,
            status="SUCCESS",
            checks={"structural": "pass", "visual": "reviewed"},
            category=item.category,
            language=spec.language,
            text_layout=spec.layout,
            bubble_text=spec.bubble_text or None,
            needs_translation=spec.needs_translation,
        )

    def _attach_exports(self, manifest_items: List[ManifestItem]) -> None:
        """Point manifest paths at the WeChat files (legacy) and record every platform file per item."""
        for m in manifest_items:
            if m.status == "FAILED":
                continue
            for pid, res in self.export_results.items():
                files = {k: str(Path(v).relative_to(self.output_dir)) for k, v in res.item_files(m.id).items()}
                if files:
                    m.exports[pid] = files
            if self.legacy_wechat:
                wx = m.exports.get("wechat", {})
                m.static_path = wx.get("main:static") if m.static_path else None
                m.animated_path = wx.get("main:animated") if m.animated_path else None
                m.thumbnail_path = wx.get("main:thumbnail")

    def _is_duo_item(self, item: ExpressionItem) -> bool:
        return self.job.pack_type == "duo" or item.id.startswith("d") or item.category in DUO_CATEGORIES

    def _is_pet_item(self, item: ExpressionItem) -> bool:
        return self.job.pack_type == "pet" or item.id.startswith("p") or item.category in PET_CATEGORIES

    def _reference_images(self, anchor_img: Path, source_img: Path) -> List[Path]:
        partner = getattr(self, "norm_partner", None)
        return [p for p in (anchor_img, source_img, partner) if p and p.exists()]

    def _render_raw_static(self, item: ExpressionItem, bible: CharacterBible, source_img: Path, anchor_img: Path, spec: TextSpec) -> Path:
        raw_path = self.work_raw_static / f"{item.id}_raw.png"
        if not raw_path.exists():
            if self._is_duo_item(item):
                prompt = build_duo_static_prompt(
                    bible, item, partner_facts=self.job.partner_facts, style=self.job.style, text_layout=spec.layout
                )
            elif self._is_pet_item(item):
                prompt = build_pet_static_prompt(
                    bible, item, style=self.job.style, text_layout=spec.layout
                )
            else:
                prompt = build_static_prompt(bible, item, style=self.job.style, text_layout=spec.layout)
            refs = self._reference_images(anchor_img, source_img)
            self.provider.render_static(refs, prompt, raw_path)
        return raw_path

    def _ai_sprite_sheet_cells(self, item, bible, source_img, anchor_img, spec) -> List[Image.Image]:
        sheet_path = self.work_raw_gif / f"{item.id}_sheet_raw.png"
        if not sheet_path.exists():
            if self._is_duo_item(item):
                prompt = build_duo_sprite_sheet_prompt(
                    bible, item, partner_facts=self.job.partner_facts, style=self.job.style, text_layout=spec.layout
                )
            elif self._is_pet_item(item):
                prompt = build_pet_sprite_sheet_prompt(
                    bible, item, style=self.job.style, text_layout=spec.layout
                )
            else:
                prompt = build_sprite_sheet_prompt(bible, item, style=self.job.style, text_layout=spec.layout)
            refs = self._reference_images(anchor_img, source_img)
            self.provider.render_static(refs, prompt, sheet_path)
        with Image.open(sheet_path) as sheet:
            return slice_sprite_sheet(sheet)

    def _ai_multipass_keyframes(self, item, bible, source_img, anchor_img, spec) -> List[Image.Image]:
        """Codex-style multi-pass: frame 1 from references, frames 2..N reference frame 1."""
        paths: List[Path] = []
        for i in range(NUM_AI_KEYFRAMES):
            kp = self.work_raw_gif / f"{item.id}_kf{i + 1}.png"
            if not kp.exists():
                prompt = build_keyframe_prompt(bible, item, i, NUM_AI_KEYFRAMES, style=self.job.style, text_layout=spec.layout)
                refs = [p for p in ((paths[0] if paths else None), anchor_img, source_img) if p and p.exists()]
                self.provider.render_static(refs, prompt, kp)
            paths.append(kp)
        frames = []
        for p in paths:
            with Image.open(p) as img:
                frames.append(img.convert("RGBA"))
        return frames

    def _process_single_expression(
        self,
        item: ExpressionItem,
        index: int,
        bible: CharacterBible,
        source_img: Path,
        anchor_img: Path,
        override_mode: Optional[str] = None,
    ) -> Tuple[TextSpec, MasterAsset]:
        effective_mode = override_mode or self.job.mode
        do_static = effective_mode in ("static", "both")
        do_anim = effective_mode in ("animated", "both")
        preset = resolve_style_preset(self.job.style)
        spec = resolve_text_spec(item, self.job, self.custom_captions)
        meme = localize_meme(item, self.job, self.custom_captions)
        font = self.job.font_path
        anim_cfg = self.job.animation

        static_master: Optional[Image.Image] = None
        if do_static:
            raw = self._render_raw_static(item, bible, source_img, anchor_img, spec)
            with Image.open(raw) as raw_img:
                static_master = compose_sticker_frames([raw_img.convert("RGBA")], spec, preset, self.canvas, 1, font, meme=meme)[0]

        frames: Optional[List[Image.Image]] = None
        frame_ms = anim_cfg.frame_duration_ms
        if do_anim:
            backend = anim_cfg.backend
            try_native = backend == "native-gif" or (backend == "auto" and not preset.prefer_keyframes)
            if try_native:
                try:
                    if self.native_gif_provider.capabilities().native_gif:
                        raw_gif = self.work_raw_gif / f"{item.id}_native_raw.gif"
                        if not raw_gif.exists():
                            self.native_gif_provider.render_native_gif(
                                prompt=build_native_gif_prompt(bible, item, style=self.job.style),
                                output=raw_gif, frames=anim_cfg.frames, frame_duration_ms=frame_ms,
                            )
                        raw_frames, native_ms = load_gif_frames(raw_gif)
                        frame_ms = anim_cfg.frame_duration_ms or native_ms
                        frames = compose_sticker_frames(raw_frames, spec, preset, self.canvas, len(raw_frames), font, meme=meme)
                except ProviderCapabilityError as e:
                    logger.info("Native GIF unavailable (%s); using AI action keyframes.", e)
                except (ProviderAuthError, ProviderQuotaError):
                    raise
                except Exception as e:
                    logger.warning("Native GIF attempt failed: %s; using AI action keyframes.", e)

            if frames is None:
                try:
                    if backend == "keyframes":
                        cells = self._ai_multipass_keyframes(item, bible, source_img, anchor_img, spec)
                    else:
                        cells = self._ai_sprite_sheet_cells(item, bible, source_img, anchor_img, spec)
                    frames = compose_sticker_frames(cells, spec, preset, self.canvas, anim_cfg.frames, font, meme=meme)
                except (ProviderAuthError, ProviderQuotaError):
                    raise
                except Exception as e:
                    if backend == "keyframes":
                        raise
                    logger.warning("AI keyframe generation failed for %s (%s); emergency fallback.", item.id, e)

            if frames is None:
                base = static_master
                if base is None:
                    raw = self._render_raw_static(item, bible, source_img, anchor_img, spec)
                    with Image.open(raw) as raw_img:
                        base = compose_sticker_frames([raw_img.convert("RGBA")], spec, preset, self.canvas, 1, font, meme=meme)[0]
                frames = synthesize_motion_frames(base, motion_type=item.motion.type, frames=anim_cfg.frames)

        asset = save_master_asset(
            self.output_dir, item.id, index, spec.caption or spec.bubble_text, static_master, frames, frame_ms,
            extra_meta={"language": spec.language, "text_layout": spec.layout, "category": item.category},
        )
        return spec, asset

    # ------------------------------------------------------------------ re-export & regenerate

    def export_only(self, platforms: Optional[List[str]] = None, force: bool = False) -> Dict[str, PlatformExportResult]:
        """Re-export existing master assets to (additional) platforms without regenerating images."""
        ids = [e.id for e in self._plan()]
        masters = load_master_assets(self.output_dir, ids)
        if not masters:
            raise FileNotFoundError("No master assets found in work/master — run generation first.")
        targets = resolve_platforms(platforms) if platforms else self.platforms
        self.export_results = export_all_platforms(
            self.output_dir, targets, masters, style=self.job.style, language=self.job.language,
            pack_title=self.job.pack_title, font_path=self.job.font_path, skip_existing=not force,
        )
        if "wechat" in targets:
            run_full_validation(self.output_dir, profile_name=self.job.export_profile)
            try:
                package_deliverables(self.output_dir, strict=True, profile_name=self.job.export_profile)
            except Exception as e:
                logger.warning("WeChat packaging warning: %s", e)
        return self.export_results

    def _delete_item_outputs(self, item: ExpressionItem, index: int) -> None:
        for p in (
            self.work_raw_static / f"{item.id}_raw.png",
            self.work_raw_gif / f"{item.id}_native_raw.gif",
            self.work_raw_gif / f"{item.id}_sheet_raw.png",
            *[self.work_raw_gif / f"{item.id}_kf{i + 1}.png" for i in range(NUM_AI_KEYFRAMES)],
            self.work_master / f"{item.id}_static.png",
            self.work_master / f"{item.id}_anim.webp",
            self.work_master / f"{item.id}_meta.json",
        ):
            p.unlink(missing_ok=True)
        profiles = load_platform_profiles()
        for pid in self.platforms:
            prof = profiles[pid]
            stem = prof.file_stem(item.id, index)
            base = self.output_dir if prof.legacy_root_layout else self.output_dir / "exports" / pid
            if prof.legacy_root_layout:
                candidates = [base / d for d in ("static", "animated", "thumbnails")]
            else:
                candidates = [base]
            for c in candidates:
                if not c.exists():
                    continue
                for f in c.rglob(f"{stem}.*"):
                    if f.is_file():
                        f.unlink()
            sc = base / "showcase"
            if sc.exists() and not prof.legacy_root_layout:
                for f in sc.glob("*"):
                    f.unlink()

    def regenerate_single_item(self, item_id: str) -> ManifestItem:
        """Regenerate one expression (AI frames + master + every platform export) and refresh manifest/QA."""
        self._check_cloud_permission()
        expressions = self._plan()
        matched = [(i, e) for i, e in enumerate(expressions) if e.id == item_id]
        if not matched:
            raise ValueError(f"Item ID {item_id} not found in planned expressions")
        idx, item = matched[0]
        self._delete_item_outputs(item, idx + 1)

        source_in = Path(self.job.source_image)
        norm_source = self.work_dir / f"source_normalized_{source_in.name}"
        if not norm_source.exists() and source_in.exists():
            normalize_source_image(source_in, norm_source)
        ref_for_bible = norm_source if norm_source.exists() else Path(self.output_dir / "work" / "character-anchor.png")
        bible = create_or_load_character_bible(ref_for_bible, self.output_dir, style=self.job.style)
        anchor_path = Path(bible.master_anchor)

        spec, _asset = self._process_single_expression(item, idx + 1, bible, norm_source, anchor_path)
        masters = load_master_assets(self.output_dir, [e.id for e in expressions])
        self.export_results = export_all_platforms(
            self.output_dir, self.platforms, masters, style=self.job.style, language=self.job.language,
            pack_title=self.job.pack_title, font_path=self.job.font_path, skip_existing=True,
        )
        asset = next(m for m in masters if m.item_id == item.id)
        updated_item = self._manifest_item(item, spec, asset)
        self._attach_exports([updated_item])

        manifest_path = self.output_dir / "manifest.json"
        if manifest_path.exists():
            try:
                with manifest_path.open("r", encoding="utf-8") as f:
                    manifest = Manifest(**json.load(f))
                replaced = False
                for i, m_item in enumerate(manifest.items):
                    if m_item.id == item_id:
                        manifest.items[i] = updated_item
                        replaced = True
                        break
                if not replaced:
                    manifest.items.append(updated_item)
                manifest.generated_count = {
                    "static": sum(1 for m in manifest.items if m.static_path),
                    "animated": sum(1 for m in manifest.items if m.animated_path),
                }
                if all(m.status == "SUCCESS" for m in manifest.items):
                    manifest.state = "COMPLETED"
                self._write_manifest(manifest)
            except Exception as e:
                logger.warning("Could not update manifest.json after regenerate: %s", e)

        if not self.job.keep_source and norm_source.exists():
            norm_source.unlink(missing_ok=True)

        run_full_validation(self.output_dir, profile_name=self.job.export_profile)
        generate_preview_sheet(self.output_dir, files=self._preview_files(masters))
        logger.info("Successfully regenerated item %s", item_id)
        return updated_item
