---
name: wechat-sticker-maker
description: Create consistent WeChat static PNG and animated GIF sticker packs from a single user-supplied photo, including captions, validation, and packaging. Use for sticker pack or 微信表情包 requests.
---

# WeChat Sticker Maker

## Trigger
Use when a user wants a set of WeChat/chat stickers or reaction GIFs from one image.
Do not trigger for ordinary photo edits unrelated to sticker packs.

## Defaults
- One user image; 16 stickers; style `kawaii-flat`; mode `both`.
- Transparent background; Simplified Chinese captions.
- One unique PNG and/or GIF file per expression. Never substitute a collage.
- Keep the same recognizable character in every result.

## Workflow
1. Identify the actual source image and check permissions / available tools.
2. Read `references/character-consistency.md` and make a stable character bible.
3. Read `references/expression-presets.json` and create an action plan.
4. Render a canonical neutral character anchor and check it against the photo.
5. Generate each static image separately using references and fixed style locks.
6. For animated mode, read `references/animation-policy.md`:
   - Prefer reference-anchored keyframe composition for identity-critical work.
   - Use native GIF generation only when supported and quality is acceptable.
7. Add Chinese captions with a licensed font in deterministic post-processing.
8. Read `references/wechat-export.md`; resize, optimize, and validate each asset.
9. Package static and animated outputs separately, create manifests and reports.
10. Report actual files and failed checks. Do not claim completion without verifying.

## Tool boundaries
- Skills do not grant image API access or filesystem capability on their own.
- If file operations are unavailable, do what is possible and disclose limits.
- If no GIF-capable generation or frame encoder exists, do not fake an animated result.
- Do not upload or store a source photo without appropriate permission.
- Do not save character references for future sessions unless user requests it.

## Delivery
Provide individual files, separate static/animated ZIPs if possible, and a
quality report. Never use a collage as the only deliverable.
