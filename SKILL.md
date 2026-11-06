---
name: wechat-sticker-maker
description: Create consistent real-person photorealistic static PNG and animated sticker packs (真人表情包 & 真人梗图) from one user portrait photo for WeChat and every social/chat platform (QQ, Douyin, Xiaohongshu, Soul, Weibo, Telegram, WhatsApp, LINE, KakaoTalk, Discord, Slack, iMessage, Signal, GIPHY/Instagram/TikTok, X ...), with 132 expressions in 14 categories, 38 meme templates, speech bubbles, single-language multilingual captions (中文/繁中/English/日本語/한국어 + any language), validation and per-platform packaging.
---

# Real-Person Sticker & Meme Maker (真人专属 · 全平台 · 全动作 · 单语种)

## Trigger
Use when a user wants a set of real-person chat stickers / 真人表情包 / 真人梗图 / スタンプ / 이모티콘 / reaction GIFs from a photo, or wants an existing pack exported for another platform.

## Core Rules & Defaults
- **REAL-PERSON ONLY (`只做真人表情包`)**: Every sticker and meme MUST preserve the reference person's authentic photorealistic facial identity, bone structure, real skin texture, eyes/nose/lips, hairstyle, and outfit (`subject_type="human-portrait"`). **NEVER cartoonize or turn the person into 2D anime, flat illustration, chibi drawing, 3D doll, or panda head.**
- Default style: `real-cutout`. 108 built-in real-person styles in 4 series (`wechat-sticker-maker styles --region <series>`):
  - 通用 (18): `real-cutout`, `real-bobblehead`, `real-street-cool`, `real-vintage-ccd`, `real-work-emo`, `real-high-contrast`, `real-polaroid-instant`, `real-fisheye-y2k`, `real-paparazzi-flash`, `real-golden-hour`, `real-blue-hour`, `real-cyber-neon`, `real-film-kodak-gold`, `real-film-cinestill-800t`, `real-vogue-editorial`, `real-french-effortless`, `real-american-yearbook`, `real-thermal-ir`
  - 韩系 (`kr`, 30): `real-kr-idol-selfie`, `real-kr-glass-skin`, `real-kr-photocard`, `real-kr-cafe-film`, `real-kr-drama`, `real-kr-variety`, `real-purikura`, `real-kr-music-bank`, `real-kr-fansign-soft`, `real-kr-airport-snap`, `real-kr-hongdae-street`, `real-kr-seongsu-industrial`, `real-kr-hannam-oldmoney`, `real-kr-apgujeong-glam`, `real-kr-jeju-breeze`, `real-kr-hanok-sunlight`, `real-kr-winter-snow`, `real-kr-cherry-blossom`, `real-kr-rainy-pocha`, `real-kr-high-teen`, `real-kr-y2k-metallic`, `real-kr-balletcore`, `real-kr-clean-fit`, `real-kr-id-photo`, `real-kr-high-angle-booth`, `real-kr-bw-fourcut`, `real-kr-practice-mirror`, `real-kr-convenience-night`, `real-kr-magazine-dazed`, `real-kr-webtoon-real`
  - 日系 (`jp`, 30): `real-jp-airy`, `real-jp-fuji-film`, `real-jp-purikura`, `real-jp-summer`, `real-jp-harajuku`, `real-jp-showa`, `real-jp-rinko-pastel`, `real-jp-hideaki-clean`, `real-jp-moriyama-bw`, `real-jp-ninagawa-vivid`, `real-jp-shibuya-neon`, `real-jp-shimokita-vintage`, `real-jp-daikanyama-morning`, `real-jp-ginza-luxury`, `real-jp-kyoto-komorebi`, `real-jp-hokkaido-snow`, `real-jp-okinawa-sun`, `real-jp-sakura-film`, `real-jp-autumn-icho`, `real-jp-rainy-hydrangea`, `real-jp-onsen-steam`, `real-jp-izakaya-warm`, `real-jp-kissaten-retro`, `real-jp-school-rooftop`, `real-jp-matsuri-fireworks`, `real-jp-nonno-magazine`, `real-jp-popeye-cityboy`, `real-jp-utsurundesu`, `real-jp-drama-subtitle`, `real-jp-variety-telop`
  - 中式 (`cn`, 30): `real-cn-new-chinese`, `real-cn-hk-retro`, `real-cn-xhs-vibe`, `real-cn-douyin`, `real-cn-studio-retro`, `real-cn-tw-youth`, `real-variety-meme`, `real-cn-jiangnan-mist`, `real-cn-palace-redwall`, `real-cn-song-minimal`, `real-cn-tang-splendor`, `real-cn-dunhuang-sunset`, `real-cn-ink-wash-light`, `real-cn-republican-velvet`, `real-cn-shanghai-bund`, `real-cn-hk-tvb-90s`, `real-cn-hk-cyber-rain`, `real-cn-tw-nightmarket`, `real-cn-chengdu-teahouse`, `real-cn-chongqing-cyber`, `real-cn-dali-sunshine`, `real-cn-hulunbuir-wind`, `real-cn-80s-factory`, `real-cn-90s-calendar`, `real-cn-cny-festive`, `real-cn-wuxia-breeze`, `real-cn-tea-zen`, `real-cn-guochao-street`, `real-cn-work-survival`, `real-cn-bazi-lucky`
  - Styles only change lighting, color grading and mood. Face, face shape, eye size, hairstyle and outfit always stay as in the photo. When the user asks for "韩系 / 日系 / 中式", pick from that series; if no style is specified, use `real-cutout`.
- Default count: 16 stickers; mode `both`; language `zh-CN`; platforms `wechat`.
- Transparent background with crisp WeChat-style die-cut white border (`die_cut_border_px >= 4`); one unique file per expression; never substitute a collage.

## Workflow
1. Identify the source portrait photo; check permissions and available tools (image generation, Python, ffmpeg).
2. Read `references/character-consistency.md`; build the real-person character bible + neutral portrait anchor (Codex built-in image generation).
3. Plan expressions from `references/expression-presets.json` (132 expressions, 14 categories: greeting, positive, negative, surprise, reply, polite, love, praise, daily, work, meme, festival, status, social; motions in `references/motion-library.json`). Pick by `--categories` / `--expressions` or the curated defaults.
4. Read `references/text-bubbles-and-languages.md`:
   - each expression has a text layout: `caption` (bottom text), `bubble` (speech bubble), `both`, or `none`;
   - bubble shapes: round, oval, thought, shout, rect, heart, whisper — for static AND animated stickers;
   - built-in captions for `zh-CN` / `zh-TW` / `en` / `ja` / `ko`; for any other language, export a template (`captions-template --language xx`), write natural colloquial translations yourself, pass `--captions-file`;
   - **ONE language per pack**: every caption, bubble and meme element on every sticker uses only the job language (`--language`). Never mix languages (no `"你好 / Hi there!"`). The pipeline refuses to run if a translation is missing or a text mixes languages; short acronyms in chat slang (`IP`, `CPU`, `OK`, `BAN`) are fine.
   - **Never ask the image model to draw text or bubbles.** Prompts reserve empty space; Python overlays text.
5. Static stickers: generate each real-person pose with `build_static_prompt` (enforces `[REAL_PERSON_HARD_LOCK]` and layout composition hint).
   Memes / abstract images (真人梗图、抽象图, e.g. `"AI 正在思考"` with a spinner on the head, `"检测到中国IP 禁止靠近"`, `"再说话封你号"`): read `references/memes.md`; use `--pack-type memes|mixed` or the one-shot `wechat-sticker-maker meme -t <template|alias> -i char.png -o out.gif`. AI draws only the real-person character; all meme UI/text/stamps/signs/filters are overlaid by code.
6. Animated stickers — read `references/animation-policy.md`:
   - **STRICT BAN**: never animate by floating/bobbing/shaking one static image, scaling the caption, or warping/painting the face with PIL.
   - Use Codex built-in image generation to draw **real multi-frame human actions**: one `2×2` 4-frame action sheet (`build_sprite_sheet_prompt`) or 2–4 sequential keyframes referencing frame 1 (`build_keyframe_sequence_prompts`).
   - Assemble with `assemble_gif_from_sprite_sheet()` / `assemble_gif_from_keyframe_files()` or `wechat-sticker-maker assemble-gif`.
7. Export — read `references/platform-export.md`. One master (720px) per sticker is exported to every platform in `references/platform-profiles.json` with correct size, margin, format (`PNG`/`WEBP`/`GIF`/`APNG`/`WEBM`/`MP4`), byte budget, frame/duration limits, pack assets and social showcase content.
8. Validate: WeChat → `qa/report.md`; other platforms → `exports/<platform>/qa-report.md`. Fix any FAIL.
9. Deliver individual files + per-platform ZIPs (`static-pack.zip`, `animated-pack.zip`, `exports/<platform>-pack.zip`) and the quality reports.

## CLI quick reference
```bash
wechat-sticker-maker styles --region 韩系               # list real-person styles (韩系/日系/中式/通用)
wechat-sticker-maker expressions --language ko          # browse catalog
wechat-sticker-maker memes --language zh-CN             # browse 38 real-person meme templates
wechat-sticker-maker plan -i photo.jpg -o out --style real-cutout --language zh-CN \
  --platforms wechat,line,telegram,xiaohongshu,instagram --categories greeting,reply,meme --count 24
wechat-sticker-maker generate -j out/job.json
wechat-sticker-maker export -j out/job.json --platforms all
```

## Tool boundaries
- Codex built-in image generation draws every real-person pose, hand wave, blink and expression; Python only removes backgrounds, slices sheets, aligns the lower-torso baseline, adds die-cut borders, overlays captions/bubbles/meme UI, encodes and validates.
- WEBM/MP4 exports need ffmpeg; Arabic/Persian/Hindi shaping needs Pillow with libraqm — disclose if missing.
- Do not upload or store a source photo without permission; do not save character references unless asked.
