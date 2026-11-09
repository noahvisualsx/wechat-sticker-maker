---
name: wechat-sticker-maker
description: Create consistent real-person photorealistic static PNG and animated sticker packs (真人表情包 & 双人互动表情包 & 真人梗图) from 1 or 2 user portrait photos for WeChat and every social/chat platform (QQ, Douyin, Xiaohongshu, Soul, Weibo, Telegram, WhatsApp, LINE, KakaoTalk, Discord, Slack, iMessage, Signal, GIPHY/Instagram/TikTok, X ...), with 108 real-person styles, 168 two-person duo interactions (闺蜜 36 / 情侣 36 / 百合 36 / 双男主 20 / 欢喜冤家 20 / 亲子 20), 220 single-person expressions across 22 categories, 60 meme templates, 15 one-click theme packs, zero-cost text remix (`remix-text`), social poster generator (`collage`), speech bubbles, single-language multilingual captions (中文/繁中/English/日本語/한국어 + any language), and zero-extra-cost multi-language pack output (`--languages zh-CN,en,ja,ko`).
---

# Real-Person Sticker, Duo Interaction & Meme Maker (真人专属 · 单人220/双人168/热梗60 · 全平台 · 单语种)

## Trigger
Use when a user wants a set of real-person chat stickers / 真人表情包 / 闺蜜表情包 / 情侣表情包 / 百合双女主表情包 / 双男主表情包 / 欢喜冤家表情包 / 亲子姐弟表情包 / 真人梗图 / スタンプ / 이모티콘 / reaction GIFs from 1 or 2 photos, or wants an existing pack remixed (`remix-text`), turned into social posters (`collage`), or exported for another platform or language.

## Core Rules & Defaults
- **REAL-PERSON ONLY (`只做真人表情包`)**: Every sticker and meme MUST preserve the reference person(s)' authentic photorealistic facial identity, bone structure, real skin texture, eyes/nose/lips, hairstyle, and outfit (`subject_type="human-portrait"`). **NEVER cartoonize or turn the person into 2D anime, flat illustration, chibi drawing, 3D doll, or panda head.**
- **168 Two-Person Duo Interaction Presets across 6 Categories (`双人互动表情包`, `references/duo-presets.json`)**:
  - `besties` (`闺蜜互动`, 36 presets: `d01_bestie_cheek_selfie` .. `d36_bestie_number_one_hug`): 贴脸自拍、合体比心、干杯奶茶、吃瓜八卦、护短抱抱等
  - `couple` (`情侣互动`, 36 presets: `d37_couple_head_pat` .. `d72_couple_goodnight_hug`): 摸头杀、背后抱、捏脸宠溺、额头贴贴、围巾共戴等
  - `yuri` (`百合双女主`, 36 presets: `d73_yuri_chin_lift_gaze` .. `d108_yuri_eternal_vow_hands`): 指尖挑下巴对视、清冷姐姐壁咚、借肩浅眠发丝交织、红线绕指宿命对视、双女主十指紧扣等
  - `yaoi` (`双男主/兄弟耽美`, 20 presets: `d109_yaoi_tie_pull_gaze` .. `d128_yaoi_pinky_lock`): 指尖拽领带对视、西装背靠背、单手撑墙低声耳语、雨夜共撑黑伞、反手扣腕挽留等
  - `rivals` (`欢喜冤家/相爱相杀`, 20 presets: `d129_rival_pinch_cheeks` .. `d148_rival_make_up_hug`): 互相扯脸颊、石头剪刀布弹脑门、偷喝奶茶、吵完秒和好抱抱等
  - `family` (`亲子/姐弟兄妹萌娃`, 20 presets: `d149_fam_copy_paste_pose` .. `d168_fam_heart_crown`): 大小同款托腮、姐姐护短、宠溺捏软脸蛋、发红包摸摸头、辅导作业血压飙升等
  - Pass `--partner photo2.jpg --duo-category 闺蜜|情侣|百合|双男主|欢喜冤家|亲子` (or `--pack-type duo`).
- Default style: `real-cutout`. 108 built-in real-person styles in 4 series (`wechat-sticker-maker styles --region <series>`):
  - 通用 (18): `real-cutout`, `real-bobblehead`, `real-street-cool`, `real-vintage-ccd`, `real-work-emo`, `real-high-contrast`, `real-polaroid-instant`, `real-fisheye-y2k`, `real-paparazzi-flash`, `real-golden-hour`, `real-blue-hour`, `real-cyber-neon`, `real-film-kodak-gold`, `real-film-cinestill-800t`, `real-vogue-editorial`, `real-french-effortless`, `real-american-yearbook`, `real-thermal-ir`
  - 韩系 (`kr`, 30): `real-kr-idol-selfie`, `real-kr-glass-skin`, `real-kr-photocard`, `real-kr-cafe-film`, `real-kr-drama`, `real-kr-variety`, `real-purikura`, `real-kr-music-bank`, `real-kr-fansign-soft`, `real-kr-airport-snap`, `real-kr-hongdae-street`, `real-kr-seongsu-industrial`, `real-kr-hannam-oldmoney`, `real-kr-apgujeong-glam`, `real-kr-jeju-breeze`, `real-kr-hanok-sunlight`, `real-kr-winter-snow`, `real-kr-cherry-blossom`, `real-kr-rainy-pocha`, `real-kr-high-teen`, `real-kr-y2k-metallic`, `real-kr-balletcore`, `real-kr-clean-fit`, `real-kr-id-photo`, `real-kr-high-angle-booth`, `real-kr-bw-fourcut`, `real-kr-practice-mirror`, `real-kr-convenience-night`, `real-kr-magazine-dazed`, `real-kr-webtoon-real`
  - 日系 (`jp`, 30): `real-jp-airy`, `real-jp-fuji-film`, `real-jp-purikura`, `real-jp-summer`, `real-jp-harajuku`, `real-jp-showa`, `real-jp-rinko-pastel`, `real-jp-hideaki-clean`, `real-jp-moriyama-bw`, `real-jp-ninagawa-vivid`, `real-jp-shibuya-neon`, `real-jp-shimokita-vintage`, `real-jp-daikanyama-morning`, `real-jp-ginza-luxury`, `real-jp-kyoto-komorebi`, `real-jp-hokkaido-snow`, `real-jp-okinawa-sun`, `real-jp-sakura-film`, `real-jp-autumn-icho`, `real-jp-rainy-hydrangea`, `real-jp-onsen-steam`, `real-jp-izakaya-warm`, `real-jp-kissaten-retro`, `real-jp-school-rooftop`, `real-jp-matsuri-fireworks`, `real-jp-nonno-magazine`, `real-jp-popeye-cityboy`, `real-jp-utsurundesu`, `real-jp-drama-subtitle`, `real-jp-variety-telop`
  - 中式 (`cn`, 30): `real-cn-new-chinese`, `real-cn-hk-retro`, `real-cn-xhs-vibe`, `real-cn-douyin`, `real-cn-studio-retro`, `real-cn-tw-youth`, `real-variety-meme`, `real-cn-jiangnan-mist`, `real-cn-palace-redwall`, `real-cn-song-minimal`, `real-cn-tang-splendor`, `real-cn-dunhuang-sunset`, `real-cn-ink-wash-light`, `real-cn-republican-velvet`, `real-cn-shanghai-bund`, `real-cn-hk-tvb-90s`, `real-cn-hk-cyber-rain`, `real-cn-tw-nightmarket`, `real-cn-chengdu-teahouse`, `real-cn-chongqing-cyber`, `real-cn-dali-sunshine`, `real-cn-hulunbuir-wind`, `real-cn-80s-factory`, `real-cn-90s-calendar`, `real-cn-cny-festive`, `real-cn-wuxia-breeze`, `real-cn-tea-zen`, `real-cn-guochao-street`, `real-cn-work-survival`, `real-cn-bazi-lucky`
  - Styles only change lighting, color grading and mood. Face, face shape, eye size, hairstyle and outfit always stay as in the photo. When the user asks for "韩系 / 日系 / 中式", pick from that series; if no style is specified, use `real-cutout`.
- Default count: 16 stickers; mode `both`; language `zh-CN`; platforms `wechat`.
- Transparent background with crisp WeChat-style die-cut white border (`die_cut_border_px >= 4`); one unique file per expression; never substitute a collage.
- **STRICT ANATOMY, FACIAL PROPORTION & CLEAN ALPHA GATE (`references/quality-standards.md` — ZERO TOLERANCE)**:
  - **Limb & Hand Count Hard Lock**: Single person = strictly `<= 2` arms & `<= 2` hands (`1 left + 1 right`); Two-person duo = strictly `<= 4` arms & `<= 4` hands (`max 2 per person`). **NEVER generate a "3rd hand" or same-shoulder dual-arm split** (if an arm is raised to touch hair/head/cheek/prop, that side's sleeve MUST lift upward with it — NEVER draw a downward-hanging sleeve/arm at the side AND a second raised arm emerging from behind the same shoulder). Natural 5-finger human hands only; zero disembodied floating hands.
  - **Craniofacial Aspect-Ratio Lock**: Preserve the exact facial width-to-height ratio (~`1:1.25`) from the reference photo(s). **NEVER vertically elongate/stretch the midface, nose bridge, philtrum, or chin ("no horse-face distortion")**; in two-person (`duo`) shots, overlap shoulders naturally by `15%–25%` instead of horizontally squishing faces.
  - **Zero Baked-In Checkerboard**: Render raw cutouts on a flat solid `#FFFFFF` pure white studio backdrop or native RGBA `alpha=0` — **NEVER paint grey-and-white checkerboard squares into RGB pixels**.
  - **Zero 2D Cartoon Symbols on Real Faces**: Express emotion with real human irises and facial muscles — NEVER draw `@_@` swirl eyes, star/heart/coin eyeball stickers, or anime lines.

## Workflow
1. Identify the source portrait photo; check permissions and available tools (image generation, Python, ffmpeg).
2. Read `references/character-consistency.md` and `references/quality-standards.md`; build the real-person character bible + neutral portrait anchor (Codex built-in image generation).
3. Plan expressions from `references/expression-presets.json` (220 expressions, 22 categories: greeting, positive, negative, surprise, reply, polite, love, praise, daily, work, meme, festival, status, social, gaming, fandom, wealth, foodie, campus, sassy, mental, pet_collab; motions in `references/motion-library.json`). Pick by `--theme`, `--categories`, `--expressions` or the curated defaults.
4. Read `references/text-bubbles-and-languages.md`:
   - each expression has a text layout: `caption` (bottom text), `bubble` (speech bubble), `both`, or `none`;
   - bubble shapes: round, oval, thought, shout, rect, heart, whisper — for static AND animated stickers;
   - built-in captions for `zh-CN` / `zh-TW` / `en` / `ja` / `ko`; for any other language, export a template (`captions-template --language xx`), write natural colloquial translations yourself, pass `--captions-file`;
   - **ONE language per pack**: every caption, bubble and meme element on every sticker uses only the job language (`--language`). Never mix languages (no `"你好 / Hi there!"`). The pipeline refuses to run if a translation is missing or a text mixes languages; short acronyms in chat slang (`IP`, `CPU`, `OK`, `BAN`) are fine.
   - **Never ask the image model to draw text or bubbles.** Prompts reserve empty space; Python overlays text.
5. Static stickers: generate each real-person pose with `build_static_prompt` / `build_duo_static_prompt` (enforces `[REAL_PERSON_HARD_LOCK]`, `[ANATOMY & PROPORTION LOCK]`, `[CLEAN CUTOUT BACKGROUND RULE]`, and layout composition hint).
   Memes / abstract images (真人梗图、抽象图, 60 built-in templates in `references/meme-templates.json`, e.g. `"AI 正在思考"`, `"检测到中国IP"`, `"再说话封你号"`, `"MBTI快乐小狗"`, `"赛博木鱼功德+1"`, `"转账520"`, `"已老实求放过"`): read `references/memes.md`; use `--pack-type memes|mixed` or the one-shot `wechat-sticker-maker meme -t <template|alias> -i char.png -o out.gif`. AI draws only the real-person character; all meme UI/text/stamps/signs/filters are overlaid by code.
6. Animated stickers — read `references/animation-policy.md`:
   - **STRICT BAN**: never animate by floating/bobbing/shaking one static image, scaling the caption, or warping/painting the face with PIL.
   - Use Codex built-in image generation to draw **real multi-frame human actions**: one `2×2` 4-frame action sheet (`build_sprite_sheet_prompt`) or 2–4 sequential keyframes referencing frame 1 (`build_keyframe_sequence_prompts`).
   - Assemble with `assemble_gif_from_sprite_sheet()` / `assemble_gif_from_keyframe_files()` or `wechat-sticker-maker assemble-gif`.
7. **MANDATORY POST-GENERATION STRICT ANATOMY & 2× ZOOM AUDIT (NEVER SKIP)**:
   - Immediately run `wechat-sticker-maker audit -o <out_dir> --strict` (or `wechat-sticker-maker audit -i <raw_image.png> [--duo]`), which checks for baked-in checkerboards, detached limb islands, vertical stretching, tiny distant figures, and `2×2` quadrant cross-bleed, and generates `<out_dir>/qa/strict-audit-sheet.jpg`.
   - **Open and visually inspect `<out_dir>/qa/strict-audit-sheet.jpg`** (check both the `2x Face & Shoulders` and `2x Sleeves & Hands` zoom panels against the reference photo):
     1. Count every shoulder, sleeve, and arm (`<= 2` per person; confirm ZERO hanging-sleeve + raised-arm duplication and ZERO 6-finger or disembodied hands);
     2. Check facial width-to-height ratio (confirm ZERO vertical midface/chin elongation or horizontal duo squishing);
     3. Confirm 100% real eyes/skin and clean transparency (ZERO grey/white checkerboard squares).
   - If ANY sticker fails programmatic or visual red-lines, **immediately regenerate it** with targeted corrective instructions (`wechat-sticker-maker regenerate -j <out_dir>/job.json --item <id> --defect third_hand_or_extra_limb,stretched_or_warped_face,baked_checkerboard` or re-run Codex image generation with the `Suggested Corrective Retry Prompt Block` from `audit`) and re-audit until `0` failures remain.
8. Export — read `references/platform-export.md`. One master (720px) per sticker is exported to every platform in `references/platform-profiles.json` with correct size, margin, format (`PNG`/`WEBP`/`GIF`/`APNG`/`WEBM`/`MP4`), byte budget, frame/duration limits, pack assets and social showcase content.
9. Validate: WeChat → `qa/report.md` (`wechat-sticker-maker validate -o <out_dir> --strict`); other platforms → `exports/<platform>/qa-report.md`. Fix any FAIL.
10. Deliver individual files + per-platform ZIPs (`static-pack.zip`, `animated-pack.zip`, `exports/<platform>-pack.zip`) and the quality reports.

## CLI quick reference
```bash
wechat-sticker-maker themes                              # list 18 one-click theme packs (打工人/发疯/电竞/追星/猫主子/快乐修勾/闺蜜/情侣/百合/双男主/欢喜冤家/亲子...)
wechat-sticker-maker styles --region 韩系               # list 108 real-person styles (韩系/日系/中式/通用)
wechat-sticker-maker duo --category 百合 --language ko  # browse 168 two-person duo presets across 6 categories
wechat-sticker-maker pets --category 猫主子             # browse 40 real-pet presets across 4 categories
wechat-sticker-maker expressions --language ko          # browse 220 single-person expressions across 22 categories
wechat-sticker-maker memes --language zh-CN             # browse 60 real-person meme templates
wechat-sticker-maker plan -i photo1.jpg -p photo2.jpg --duo-category 百合 -o out \
  --style real-kr-idol-selfie --language auto --languages zh-CN,en,ja,ko --count 16
wechat-sticker-maker generate -j out/job.json --provider auto --strict-qa
wechat-sticker-maker audit -o out --strict               # run strict anatomy/checkerboard QA + generate 2x zoom sheet
wechat-sticker-maker regenerate -j out/job.json --item d03_bestie_hype_queen \
  --defect third_hand_or_extra_limb,stretched_or_warped_face
wechat-sticker-maker remix-text -j out/job.json --set d73_yuri_chin_lift_gaze="姐姐只看我"
wechat-sticker-maker collage -o out --title "双女主贴贴包" --animated --wechat-kit
wechat-sticker-maker publish-telegram -o out --name my_real_pack --title "My Real Pack" --dry-run
wechat-sticker-maker serve --port 7860
wechat-sticker-maker export -j out/job.json --platforms all
```

## Tool boundaries
- Codex built-in image generation draws every real-person pose, hand wave, blink and expression; Python only removes backgrounds, slices sheets, aligns the lower-torso baseline, adds die-cut borders, overlays captions/bubbles/meme UI, encodes and validates.
- WEBM/MP4 exports need ffmpeg; Arabic/Persian/Hindi shaping needs Pillow with libraqm — disclose if missing.
- Do not upload or store a source photo without permission; do not save character references unless asked.
