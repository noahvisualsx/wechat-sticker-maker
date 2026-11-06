<p align="right">
  <strong>Language:</strong>
  <a href="README.md"><b>简体中文</b></a> |
  <a href="README.en.md"><b>English</b></a> |
  <a href="README.ko.md"><b>한국어</b></a> |
  <a href="README.ja.md"><b>日本語</b></a>
</p>

# WeChat Sticker Maker · Real-Person AI Sticker & Meme Pack Engine

> **Your Face, Your Vibe, Your Sticker Pack.**  
> An end-to-end ChatGPT / Codex skill and Python toolkit exclusively dedicated to **real-person (`human-portrait`)** sticker packs and memes (static PNG/WebP + multi-frame animated GIF/APNG/WebM). Strictly preserves your exact facial features, bone structure, skin texture, hairstyle, and outfit—**never turning real people into 2D anime or generic cartoons**—and exports across **WeChat and 23 global social platforms** in a single run.

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Real Person Only](https://img.shields.io/badge/Subject-100%25%20Real%20Person%20Portrait-ff69b4.svg)](#26-built-in-real-person-photographic-styles-referencesstyle-presetsjson)
[![Styles](https://img.shields.io/badge/Photographic%20Styles-26%20Presets%20(General%20%7C%20KR%20%7C%20JP%20%7C%20CN)-blue.svg)](#26-built-in-real-person-photographic-styles-referencesstyle-presetsjson)
[![Expressions & Memes](https://img.shields.io/badge/Catalog-132%20Expressions%20%7C%2038%20Memes%20%7C%20129%20Motions-success.svg)](#14-real-person-expression-categories)
[![Languages](https://img.shields.io/badge/Single--Language%20Bubbles-zh--CN%20%7C%20zh--TW%20%7C%20en%20%7C%20ja%20%7C%20ko-orange.svg)](#7-speech-bubble-shapes--5-strict-single-language-packs)
[![Platforms](https://img.shields.io/badge/Export-23%20Social%20Platforms-purple.svg)](#23-platform-export--social-media-covers)

</div>

![Real-Person Sticker Showcase](docs/gallery/images/hero.jpg)

> **[Explore the Full Real-Person Visual Gallery (26 Styles / 10 Animated GIFs / 38 Memes / 14 Categories) → `docs/gallery/README.md`](docs/gallery/README.md)**

Exports simultaneously to **WeChat and 23 major social & messaging platforms**: WeChat, QQ, Douyin/Kuaishou, Xiaohongshu (RED), Soul, Weibo, DingTalk, Feishu/Lark, Telegram, WhatsApp, LINE, KakaoTalk, Discord, Slack, iMessage, Signal, Viber, GIPHY (Instagram / TikTok / Snapchat sticker source), Instagram, TikTok, X (Twitter), Facebook, and Universal packs.

---

## Core Highlights

- **26 Real-Person Photographic Styles across 4 Series (General / Korean / Japanese / Chinese)**: Defaults to `real-cutout` with classic 4px die-cut white sticker borders. Changes lighting, color grading, and photographic mood while keeping your real face 100% authentic.
- **True Multi-Frame AI Animation Powered by Codex Native Image Generation**: Every wave, blink, head tilt, and micro-expression is drawn by Codex AI via `2×2` 4-frame action sprite sheets (`build_sprite_sheet_prompt`) or sequential reference keyframes. Python only handles non-destructive alpha matting, torso-anchored frame registration, die-cut borders, typography, and encoding—never fake affine warping.
- **Comprehensive Expression & Motion Catalog**: 132 expressions across 14 categories and 129 motion types (`references/motion-library.json`), each with a 4-frame AI storyboard.
- **38 Real-Person Meme & Abstract Templates**: Includes viral templates (`references/meme-templates.json`) such as AI "Thinking..." spinner, "China IP Detected — Keep Back", "One More Word & You're Banned", "Thought for 999 Seconds", "Rate Limit Exceeded", "CPU Overheated", and high-contrast B&W photographic memes.
- **Speech Bubbles & Strict Single-Language Isolation**: Supports `caption` / `bubble` / `both` / `none` text modes and 7 bubble shapes across `zh-CN`, `zh-TW`, `en`, `ja`, and `ko`. **Every sticker uses a single language—zero bilingual mixing.**
- **One Master, 23 Platform Exports**: Generates a 720px transparent master once and automatically compiles platform-specific dimensions, file size budgets, and social showcase cards (3:4 Xiaohongshu cover, 9:16 Instagram Story/Reels, 3×3 grid).

See [`references/text-bubbles-and-languages.md`](references/text-bubbles-and-languages.md), [`references/memes.md`](references/memes.md), and [`references/platform-export.md`](references/platform-export.md) for full details.

---

## 26 Built-In Real-Person Photographic Styles (`references/style-presets.json`)

Grouped into **General / Korean / Japanese / Chinese** series. Filter by region via CLI: `wechat-sticker-maker styles --region kr` (supports `general` / `kr` / `jp` / `cn`).

![Four Photographic Style Series Comparison](docs/gallery/images/four-series.jpg)

![26 Real-Person Sticker Styles Overview](docs/gallery/images/styles-overview.jpg)

### General Series (6)
| Style ID (`--style`) | Name | Highlights |
|---|---|---|
| `real-cutout` | **Real Photo Die-Cut Sticker (Default)** | Preserves exact facial features & skin texture with a 4px white die-cut border |
| `real-bobblehead` | Real Caricature Bobblehead | Real photographic face + playful oversized head proportion & 5px cutout border |
| `real-street-cool` | Real Editorial Street Flash | Direct-flash magazine street portrait with crisp high-contrast lighting |
| `real-vintage-ccd` | Real Y2K CCD Digicam | Early-2000s warm CCD point-and-shoot flash aesthetic |
| `real-work-emo` | Real Office Deadpan Candid | Candid deadpan / exhausted coworker reactions |
| `real-high-contrast` | Real High-Contrast B&W Meme | Classic high-contrast black-and-white photographic meme cutout |

### Korean Series (`韩系` · 7)
![Korean Series 7 Styles](docs/gallery/images/series-kr.jpg)

| Style ID | Name | Highlights |
|---|---|---|
| `real-kr-idol-selfie` | K-Pop Idol Selfie | Soft ring-light catchlights, glossy gradient lips, finger-hearts & winks |
| `real-kr-glass-skin` | Korean Dewy Glass Skin | Luminous dewy complexion with soft neutral pastel studio lighting |
| `real-kr-photocard` | K-Pop Photocard | Pastel pink-and-ice-blue rim lighting, collectible photocard look |
| `real-kr-cafe-film` | Seoul Cafe Warm Film | Window daylight, creamy latte/beige color grading, gentle film grain |
| `real-kr-drama` | K-Drama Golden Backlight | Cinematic shallow depth-of-field and warm golden-hour rim light |
| `real-kr-variety` | K-Variety Show Reaction | Running Man style expressive reaction with colorful outlined variety pop text |
| `real-purikura` | Korean Life4Cuts (`인생네컷`) | Clean pastel photobooth studio lighting with soft pink-white sticker outline |

### Japanese Series (`日系` · 6)
![Japanese Series 6 Styles](docs/gallery/images/series-jp.jpg)

| Style ID | Name | Highlights |
|---|---|---|
| `real-jp-airy` | Japanese Airy Transparent | Slightly overexposed, low-contrast cyan-pink airy daylight |
| `real-jp-fuji-film` | Japanese Fujifilm Portra | Nostalgic teal-green shadows, warm skin tones, fine 35mm grain |
| `real-jp-purikura` | Tokyo Purikura (`プリクラ`) | Bright beauty flash & kawaii pastel frame (without distorting real eye size) |
| `real-jp-summer` | Kamakura Summer Backlight | Crisp sunlit hair highlights and refreshing coastal summer breeze |
| `real-jp-harajuku` | Harajuku Street Snap | Punchy on-camera flash with bold street-fashion color contrast |
| `real-jp-showa` | 80s Showa Retro Film | Warm faded amber halation and vintage 1980s film softness |

### Chinese Series (`中式` · 7)
![Chinese Series 7 Styles](docs/gallery/images/series-cn.jpg)

| Style ID | Name | Highlights |
|---|---|---|
| `real-cn-new-chinese` | Neo-Chinese Guofeng Portrait | Warm lantern-lit elegance with subtle vermilion and gold accents |
| `real-cn-hk-retro` | 90s Hong Kong Cinema Neon | Wong Kar-wai inspired neon red & teal rim light with rich film grain |
| `real-cn-xhs-vibe` | Xiaohongshu Creamy Aesthetic | Creamy diffused daylight and refined low-saturation tones |
| `real-cn-douyin` | Douyin Studio Beauty Light | Crisp ring-light catchlights and energetic expressions (true face shape preserved) |
| `real-cn-studio-retro` | 90s Retro Photo Studio | Nostalgic 1990s soft-focus portrait studio aesthetic for ironic humor |
| `real-cn-tw-youth` | Taiwan Youth Indie Film | Warm afternoon sunlight with nostalgic green-gold film grading |
| `real-variety-meme` | Chinese Variety Show Meme | Expressive reaction paired with bold yellow-and-black variety show captions |

---

## Codex AI Multi-Frame Animated GIFs (4-Frame Keyframe Storyboards)

![Real-Person Animated GIF Showcase](docs/gallery/images/animated-showcase.gif)

---

## 14 Real-Person Expression Categories

![Real-Person Expressions 1/2](docs/gallery/images/expressions-01.jpg)
![Real-Person Expressions 2/2](docs/gallery/images/expressions-02.jpg)

---

## 38 Real-Person Meme & Abstract Templates (6 Categories)

![Real-Person Memes Overview](docs/gallery/images/memes-overview.jpg)

---

## 7 Speech Bubble Shapes & 5 Strict Single-Language Packs

![7 Speech Bubble Shapes](docs/gallery/images/bubbles.jpg)
![5 Single-Language Packs](docs/gallery/images/languages.jpg)

---

## 23-Platform Export & Social Media Covers

![Social Media Publishing Assets](docs/gallery/images/platforms.jpg)

---

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# Inspect environment & real-person style catalog
wechat-sticker-maker doctor
wechat-sticker-maker styles
wechat-sticker-maker styles --region kr

# Plan and generate a real-person sticker pack
wechat-sticker-maker plan \
  --input photo.jpg \
  --output output/my-portrait-pack \
  --mode both \
  --count 16 \
  --style real-cutout \
  --language en \
  --platforms wechat,xiaohongshu,instagram,telegram

wechat-sticker-maker generate --job output/my-portrait-pack/job.json

# Quick single real-person meme generation
wechat-sticker-maker meme -t claude -i photo.jpg --language en -o output/thinking.gif
wechat-sticker-maker meme -t m02_china_ip_blocked -i photo.jpg --language en -o output/ip_blocked.gif
wechat-sticker-maker meme -t m03_ban_threat -i photo.jpg --language en -o output/ban.gif
```

## Testing

```bash
pytest -v
python scripts/smoke_test.py
```

## License

MIT License. See [`LICENSE`](LICENSE) for details.
