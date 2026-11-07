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
[![Styles](https://img.shields.io/badge/Photographic%20Styles-108%20Presets%20(General%20%7C%20KR%20%7C%20JP%20%7C%20CN)-blue.svg)](#108-built-in-real-person-photographic-styles-referencesstyle-presetsjson)
[![Duo Interactions](https://img.shields.io/badge/Two--Person%20Duo-168%20Presets%20(6%20Categories)-ff2d55.svg)](#168-two-person-real-portrait-duo-interaction-presets-referencesduo-presetsjson)
[![Expressions & Memes](https://img.shields.io/badge/Catalog-220%20Expressions%20%7C%2060%20Memes%20%7C%2015%20Themes-success.svg)](#22-real-person-expression-categories)
[![Languages](https://img.shields.io/badge/Single--Language%20Bubbles-zh--CN%20%7C%20zh--TW%20%7C%20en%20%7C%20ja%20%7C%20ko-orange.svg)](#7-speech-bubble-shapes--5-strict-single-language-packs)
[![Platforms](https://img.shields.io/badge/Export-23%20Social%20Platforms-purple.svg)](#23-platform-export--social-media-covers)

</div>

![Real-Person Sticker Showcase](docs/gallery/images/hero.jpg)

> **[Explore the Full Real-Person Visual Gallery (108 Styles / 168 Duo Presets / 60 Memes / 22 Categories · 220 Expressions) → `docs/gallery/README.md`](docs/gallery/README.md)**

Exports simultaneously to **WeChat and 23 major social & messaging platforms**: WeChat, QQ, Douyin/Kuaishou, Xiaohongshu (RED), Soul, Weibo, DingTalk, Feishu/Lark, Telegram, WhatsApp, LINE, KakaoTalk, Discord, Slack, iMessage, Signal, Viber, GIPHY (Instagram / TikTok / Snapchat sticker source), Instagram, TikTok, X (Twitter), Facebook, and Universal packs.

---

## Core Highlights

- **108 Real-Person Photographic Styles across 4 Series (General / Korean / Japanese / Chinese)**: Defaults to `real-cutout` with classic 4px die-cut white sticker borders. Changes lighting, color grading, and photographic mood while keeping your real face 100% authentic.
- **168 Two-Person Duo Interaction Presets across 6 Categories (`references/duo-presets.json`)**: Besties (`36`), Couple (`36`), Yuri / GL (`36`), Yaoi / Bromance (`20`), Playful Rivals (`20`), and Family / Siblings (`20`).
- **220 Single-Person Expressions across 22 Categories (`references/expression-presets.json`)**: Includes 8 new high-frequency chat categories: Gaming/Esports (`gaming`), Fandom/Idol (`fandom`), Wealth/Money (`wealth`), Boba/Foodie (`foodie`), Campus/Exams (`campus`), Sassy/Tea (`sassy`), Chaotic Mental State (`mental`), and Pet Collab (`pet_collab`).
- **60 Real-Person Meme & Abstract Templates (`references/meme-templates.json`)**: Includes AI "Thinking..." spinner, China IP Warning, Ban Hammer, MBTI ENFP/INTJ badges, Cyber Wooden Fish Karma +1, Social Battery 1%, WeChat ¥520 Transfer, 60s Voice Note Barrage, Behaving Stamp, Sanity 999%, Zundu Jiadu, Left on Read, Slacking Permit, and AI Confident Hallucination.
- **15 One-Click Theme Packs + Zero-Cost Text Remix (`remix-text`) + Social Poster Generator (`collage`)**: Build themed packs via `--theme`, swap captions/bubbles in <2 seconds with 0 AI tokens via `remix-text`, and generate 3:4 Xiaohongshu / 9:16 Story posters + 4-language store submission copy via `collage`.

See [`references/text-bubbles-and-languages.md`](references/text-bubbles-and-languages.md), [`references/memes.md`](references/memes.md), and [`references/platform-export.md`](references/platform-export.md) for full details.

---

## 108 Built-In Real-Person Photographic Styles (`references/style-presets.json`)

Grouped into **General (18) / Korean (30) / Japanese (30) / Chinese (30)** series. Filter by region via CLI: `wechat-sticker-maker styles --region kr` (supports `general` / `kr` / `jp` / `cn`).

![Four Photographic Style Series Comparison](docs/gallery/images/four-series.jpg)

![Real-Person Sticker Styles Overview](docs/gallery/images/styles-overview.jpg)

### General Series (18)
| # | Style ID (`--style`) | Style Name | Lighting & Original Preset |
|---|---|---|---|
| 1 | `real-cutout` | **Real Photo Die-Cut Sticker (Default)** | `studio-portrait` · 真人写真抠图贴纸 |
| 2 | `real-bobblehead` | **Real Caricature Bobblehead** | `bright-studio` · 真人搞怪大头贴 |
| 3 | `real-street-cool` | **Real Editorial Street Flash** | `editorial-flash` · 真人潮酷街拍贴纸 |
| 4 | `real-vintage-ccd` | **Real Y2K CCD Digicam** | `ccd-warm-flash` · 真人复古CCD胶片贴纸 |
| 5 | `real-work-emo` | **Real Office Deadpan Candid** | `natural-candid` · 真人打工人纪实梗图 |
| 6 | `real-high-contrast` | **Real High-Contrast B&W Meme** | `high-contrast-studio` · 真人黑白高反差梗图 |
| 7 | `real-polaroid-instant` | **Polaroid SX-70 Instant Film** | `polaroid-instant` · 真人拍立得即时相纸 |
| 8 | `real-fisheye-y2k` | **Y2K 16mm Fisheye Close-Up** | `fisheye-y2k-flash` · 真人千禧鱼眼大头贴 |
| 9 | `real-paparazzi-flash` | **Night Paparazzi Direct Flash** | `paparazzi-direct-flash` · 真人狗仔直闪抓拍 |
| 10 | `real-golden-hour` | **Golden Hour Sunset Backlight** | `golden-hour-sunset` · 真人落日夕阳逆光 |
| 11 | `real-blue-hour` | **Blue Hour Twilight Cinema** | `blue-hour-cinematic` · 真人蓝调时刻电影感 |
| 12 | `real-cyber-neon` | **Cyberpunk Dual-Neon Night** | `cyber-dual-neon` · 真人赛博霓虹夜景 |
| 13 | `real-film-kodak-gold` | **Kodak Gold 200 Warm Film** | `kodak-gold-200` · 真人柯达Gold200胶片 |
| 14 | `real-film-cinestill-800t` | **CineStill 800T Tungsten Film** | `cinestill-800t` · 真人CineStill钨丝灯胶片 |
| 15 | `real-vogue-editorial` | **High-Fashion Editorial Studio** | `vogue-rembrandt-studio` · 真人高定时尚杂志封面 |
| 16 | `real-french-effortless` | **Parisian Afternoon Window Light** | `french-afternoon-sun` · 真人法式慵懒午后写真 |
| 17 | `real-american-yearbook` | **90s American Yearbook Studio** | `retro-yearbook-studio` · 真人美式复古毕业年鉴 |
| 18 | `real-thermal-ir` | **Festival UV Duotone Stage Glow** | `uv-festival-duo` · 真人潮流伪彩视觉 |

### Korean Series (`韩系` · 30)
![Korean Series Preview](docs/gallery/images/series-kr.jpg)

| # | Style ID (`--style`) | Style Name | Lighting & Original Preset |
|---|---|---|---|
| 1 | `real-purikura` | **Korean Life4Cuts Photobooth** | `creamy-kbeauty` · 韩系人生四格大头贴 |
| 2 | `real-kr-idol-selfie` | **K-Pop Idol Selfie** | `kpop-ringlight` · 韩系爱豆自拍 |
| 3 | `real-kr-glass-skin` | **Korean Dewy Glass Skin** | `kbeauty-dewy` · 韩系水光肌清透 |
| 4 | `real-kr-photocard` | **K-Pop Collectible Photocard** | `pastel-gradient-studio` · 韩系爱豆小卡 |
| 5 | `real-kr-cafe-film` | **Seoul Cafe Warm Film** | `window-daylight` · 韩系咖啡馆胶片 |
| 6 | `real-kr-drama` | **K-Drama Golden Backlight** | `kdrama-backlight` · 韩剧主角氛围 |
| 7 | `real-kr-variety` | **K-Variety Show Reaction** | `kvariety-highkey` · 韩综字幕斗图 |
| 8 | `real-kr-music-bank` | **K-Pop Music Show Ending Fairy** | `kpop-stage-ending` · 韩系打歌舞台Ending妖精 |
| 9 | `real-kr-fansign-soft` | **Idol Fansign Creamy Soft Light** | `kr-fansign-telephoto` · 韩系签售会奶油柔光 |
| 10 | `real-kr-airport-snap` | **Incheon Airport Off-Duty Snap** | `kr-airport-daylight` · 韩系仁川机场路透街拍 |
| 11 | `real-kr-hongdae-street` | **Hongdae Indie Street Snap** | `kr-hongdae-overcast` · 韩系弘大街头潮拍 |
| 12 | `real-kr-seongsu-industrial` | **Seongsu-dong Loft Minimalist** | `kr-seongsu-concrete` · 韩系圣水洞工业风写真 |
| 13 | `real-kr-hannam-oldmoney` | **Hannam-dong Old-Money Cashmere** | `kr-hannam-cashmere` · 韩系汉南洞千金氛围 |
| 14 | `real-kr-apgujeong-glam` | **Apgujeong Night Flash Glam** | `kr-apgujeong-flash` · 韩系狎鸥亭闪光夜拍 |
| 15 | `real-kr-jeju-breeze` | **Jeju Island Coastal Breeze Film** | `kr-jeju-coastal-sun` · 韩系济州岛海风胶片 |
| 16 | `real-kr-hanok-sunlight` | **Bukchon Hanok Warm Courtyard** | `kr-hanok-warm-wood` · 韩系北村韩屋暖阳 |
| 17 | `real-kr-winter-snow` | **First Snow Winter Sonata Glow** | `kr-first-snow-soft` · 韩系初雪围巾恋歌 |
| 18 | `real-kr-cherry-blossom` | **Yeouido Cherry Blossom Sunlight** | `kr-yeouido-blossom` · 韩系汝矣岛樱花柔光 |
| 19 | `real-kr-rainy-pocha` | **Seoul Night Pojangmacha Glow** | `kr-pocha-warm-amber` · 韩系雨夜布帐马车 |
| 20 | `real-kr-high-teen` | **K-Pop High-Teen Campus Pop** | `kr-highteen-pop` · 韩系High-Teen复古校园 |
| 21 | `real-kr-y2k-metallic` | **Y2K Cyber Silver Concept** | `kr-y2k-silver-frost` · 韩系Y2K千禧银光 |
| 22 | `real-kr-balletcore` | **Korean Balletcore Pearl Soft** | `kr-balletcore-pearl` · 韩系芭蕾风柔粉写真 |
| 23 | `real-kr-clean-fit` | **Gangnam Clean-Fit White Studio** | `kr-cleanfit-cyclorama` · 韩系Clean-Fit极简白棚 |
| 24 | `real-kr-id-photo` | **Seoul Signature ID Portrait** | `kr-id-butterfly-light` · 韩系最美证件照精修 |
| 25 | `real-kr-high-angle-booth` | **High-Angle Overhead Photobooth** | `kr-high-angle-booth` · 韩系俯拍高角度四格 |
| 26 | `real-kr-bw-fourcut` | **Monochrome Self-Photo Studio** | `kr-mono-photobooth` · 韩系黑白胶片四格 |
| 27 | `real-kr-practice-mirror` | **Dance Practice Room Mirror Snap** | `kr-practice-room-bright` · 韩系练习室对镜自拍 |
| 28 | `real-kr-convenience-night` | **Late-Night Convenience Store** | `kr-convenience-fluorescent` · 韩系深夜便利店霓虹 |
| 29 | `real-kr-magazine-dazed` | **Seoul Avant-Garde Editorial** | `kr-avant-garde-gel` · 韩系先锋画报冷冽光 |
| 30 | `real-kr-webtoon-real` | **K-Webtoon Live-Action Hero Glow** | `kr-webtoon-hero-glow` · 韩系漫改主角神颜光 |

### Japanese Series (`日系` · 30)
![Japanese Series Preview](docs/gallery/images/series-jp.jpg)

| # | Style ID (`--style`) | Style Name | Lighting & Original Preset |
|---|---|---|---|
| 1 | `real-jp-airy` | **Japanese Airy Transparent** | `airy-overexposed` · 日系空气感清新 |
| 2 | `real-jp-fuji-film` | **Japanese Fujifilm Portra** | `fuji-film` · 日系富士胶片 |
| 3 | `real-jp-purikura` | **Tokyo Purikura Pastel** | `purikura-booth` · 日系大头贴プリクラ |
| 4 | `real-jp-summer` | **Kamakura Summer Backlight** | `summer-backlight` · 日系夏日逆光 |
| 5 | `real-jp-harajuku` | **Harajuku Street Snap** | `street-flash` · 日系原宿街头 |
| 6 | `real-jp-showa` | **80s Showa Retro Film** | `showa-retro` · 日系昭和复古 |
| 7 | `real-jp-rinko-pastel` | **Rinko Kawauchi Airy Pastel** | `jp-rinko-highkey-pastel` · 日系川内伦子风淡彩 |
| 8 | `real-jp-hideaki-clean` | **Hideaki Hamada Medium-Format** | `jp-hideaki-medium-format` · 日系滨田英明风清透 |
| 9 | `real-jp-moriyama-bw` | **Daido Moriyama Gritty B&W** | `jp-moriyama-gritty-bw` · 日系森山大道粗颗粒黑白 |
| 10 | `real-jp-ninagawa-vivid` | **Mika Ninagawa Jewel-Toned** | `jp-ninagawa-saturated` · 日系蜷川实花浓郁花影 |
| 11 | `real-jp-shibuya-neon` | **Shibuya Crossing Night Neon** | `jp-shibuya-night-neon` · 日系涩谷十字路口霓虹 |
| 12 | `real-jp-shimokita-vintage` | **Shimokitazawa Vintage Shop** | `jp-shimokita-warm-film` · 日系下北泽古着胶片 |
| 13 | `real-jp-daikanyama-morning` | **Daikanyama Morning Bookstore** | `jp-daikanyama-morning` · 日系代官山晨光书店 |
| 14 | `real-jp-ginza-luxury` | **Ginza Evening Champagne Bokeh** | `jp-ginza-champagne-glow` · 日系银座夜色流光 |
| 15 | `real-jp-kyoto-komorebi` | **Kyoto Garden Komorebi Sunlight** | `jp-kyoto-komorebi` · 日系京都木漏日和风 |
| 16 | `real-jp-hokkaido-snow` | **Hokkaido Love Letter Snow** | `jp-hokkaido-snow-bounce` · 日系北海道情书雪景 |
| 17 | `real-jp-okinawa-sun` | **Okinawa Sea-Salt Tropical Sun** | `jp-okinawa-sea-salt` · 日系冲绳盛夏海盐 |
| 18 | `real-jp-sakura-film` | **Meguro River Sakura Film** | `jp-sakura-spring-film` · 日系樱花季春光胶片 |
| 19 | `real-jp-autumn-icho` | **Meiji Jingu Golden Ginkgo** | `jp-autumn-ginkgo-gold` · 日系银杏大道秋日暖光 |
| 20 | `real-jp-rainy-hydrangea` | **Kamakura Rainy Hydrangea Blue** | `jp-kamakura-rainy-blue` · 日系镰仓梅雨紫阳花 |
| 21 | `real-jp-onsen-steam` | **Hakone Ryokan Warm Steam** | `jp-onsen-warm-mist` · 日系温泉旅馆暖雾 |
| 22 | `real-jp-izakaya-warm` | **Late-Night Tokyo Izakaya Lantern** | `jp-izakaya-lantern` · 日系深夜食堂居酒屋 |
| 23 | `real-jp-kissaten-retro` | **Showa Kissaten Amber Coffee** | `jp-kissaten-amber` · 日系纯喫茶昭和咖啡 |
| 24 | `real-jp-school-rooftop` | **High-School Rooftop Clear Sky** | `jp-rooftop-clear-sky` · 日系青春天台晴空 |
| 25 | `real-jp-matsuri-fireworks` | **Summer Matsuri Handheld Sparkler** | `jp-sparkler-warm-glow` · 日系夏日祭花火微光 |
| 26 | `real-jp-nonno-magazine` | **Japanese Sweet Fashion Magazine** | `jp-sweet-magazine-studio` · 日系甜美日杂画报 |
| 27 | `real-jp-popeye-cityboy` | **Tokyo City-Boy Editorial Sun** | `jp-popeye-cityboy-sun` · 日系CityBoy街头画报 |
| 28 | `real-jp-utsurundesu` | **Fujifilm QuickSnap Disposable** | `jp-quicksnap-disposable` · 日系写ルンです一次性胶片 |
| 29 | `real-jp-drama-subtitle` | **J-Drama Prime-Time Still** | `jp-prime-drama-cinematic` · 日剧黄金档电影感剧照 |
| 30 | `real-jp-variety-telop` | **J-Variety Show Bold Telop** | `jp-variety-tv-bright` · 日综夸张大字报斗图 |

### Chinese Series (`中式` · 30)
![Chinese Series Preview](docs/gallery/images/series-cn.jpg)

| # | Style ID (`--style`) | Style Name | Lighting & Original Preset |
|---|---|---|---|
| 1 | `real-variety-meme` | **Chinese Variety Show Meme** | `high-key-tv` · 真人综艺花字斗图 |
| 2 | `real-cn-new-chinese` | **Neo-Chinese Guofeng Portrait** | `oriental-warm` · 新中式国风写真 |
| 3 | `real-cn-hk-retro` | **90s Hong Kong Cinema Neon** | `hk-neon-film` · 港风复古胶片 |
| 4 | `real-cn-xhs-vibe` | **Xiaohongshu Creamy Aesthetic** | `creamy-soft` · 小红书氛围感 |
| 5 | `real-cn-douyin` | **Douyin Studio Beauty Light** | `ringlight-bright` · 抖音网红美颜 |
| 6 | `real-cn-studio-retro` | **90s Retro Photo Studio** | `retro-studio-softfocus` · 复古影楼风 |
| 7 | `real-cn-tw-youth` | **Taiwan Youth Indie Film** | `afternoon-sun` · 台式青春胶片 |
| 8 | `real-cn-jiangnan-mist` | **Jiangnan Celadon Misty Rain** | `cn-jiangnan-celadon-mist` · 中式江南烟雨清冷 |
| 9 | `real-cn-palace-redwall` | **Imperial Vermilion Wall Sunlight** | `cn-crimson-wall-sun` · 中式红墙琉璃暖阳 |
| 10 | `real-cn-song-minimal` | **Song-Dynasty Minimalist Ivory** | `cn-song-ruyao-minimal` · 中式宋韵极简留白 |
| 11 | `real-cn-tang-splendor` | **Tang-Style Gilded Lantern Glow** | `cn-tang-gilded-lantern` · 中式盛唐鎏金夜宴 |
| 12 | `real-cn-dunhuang-sunset` | **Dunhuang Desert Amber Sunset** | `cn-dunhuang-amber-dusk` · 中式敦煌大漠流沙 |
| 13 | `real-cn-ink-wash-light` | **Monochrome Ink-Tonal Portrait** | `cn-ink-studio-monochrome` · 中式水墨光影写真 |
| 14 | `real-cn-republican-velvet` | **1930s Shanghai Velvet Tungsten** | `cn-vintage-shanghai-tungsten` · 中式民国复古画报 |
| 15 | `real-cn-shanghai-bund` | **Shanghai Bund Blossoms Amber** | `cn-bund-amber-cinema` · 中式外滩流光夜色 |
| 16 | `real-cn-hk-tvb-90s` | **90s Hong Kong TVB Drama Still** | `cn-hk-tvb-90s-warm` · 港风90年代TVB剧照 |
| 17 | `real-cn-hk-cyber-rain` | **Mong Kok Rainy Neon Street** | `cn-mongkok-rain-neon` · 港风旺角雨夜霓虹 |
| 18 | `real-cn-tw-nightmarket` | **Taipei Night Market Warm Bokeh** | `cn-taipei-nightmarket` · 台式夜市烟火霓虹 |
| 19 | `real-cn-chengdu-teahouse` | **Chengdu Bamboo Teahouse Sun** | `cn-chengdu-bamboo-sun` · 中式成都竹椅茶馆 |
| 20 | `real-cn-chongqing-cyber` | **Chongqing Mountain-City Mist** | `cn-chongqing-fog-neon` · 中式重庆山城迷雾夜 |
| 21 | `real-cn-dali-sunshine` | **Dali Erhai Highland Sunshine** | `cn-dali-highland-sun` · 中式大理洱海慢生活 |
| 22 | `real-cn-hulunbuir-wind` | **Hulunbuir Grassland Breeze** | `cn-grassland-open-sky` · 中式草原旷野清风 |
| 23 | `real-cn-80s-factory` | **80s Vintage Seagull Film** | `cn-80s-seagull-film` · 中式80年代怀旧胶片 |
| 24 | `real-cn-90s-calendar` | **90s Retro Wall-Calendar Studio** | `cn-90s-calendar-bright` · 中式90年代挂历画报 |
| 25 | `real-cn-cny-festive` | **Lunar New Year Red & Gold** | `cn-lunar-new-year-gold` · 中式新春贺岁红金 |
| 26 | `real-cn-wuxia-breeze` | **Cinematic Wuxia Slate Breeze** | `cn-wuxia-cinematic-cool` · 中式武侠清风江湖 |
| 27 | `real-cn-tea-zen` | **Hearth Tea-Brewing Zen Glow** | `cn-tea-hearth-zen` · 中式围炉煮茶禅意 |
| 28 | `real-cn-guochao-street` | **Guochao Vermilion & Teal Flash** | `cn-guochao-crimson-teal` · 中式国潮街头撞色 |
| 29 | `real-cn-work-survival` | **Modern Tech-Office Monitor Glow** | `cn-office-monitor-glow` · 中式大厂打工人图鉴 |
| 30 | `real-cn-bazi-lucky` | **Auspicious Koi Golden Halo** | `cn-auspicious-golden-halo` · 中式锦鲤好运玄学风 |

---

## 108 Two-Person Real-Portrait Duo Interaction Presets (`references/duo-presets.json`)

Pass two real portrait photos (`-i personA.jpg -p personB.jpg`) to generate two-person real-portrait stickers while preserving BOTH people's authentic facial identity (`wechat-sticker-maker duo --category besties|couple|yuri --language en`).

| Category (`--duo-category`) | Count | IDs | Signature Real-Person Interactions |
|---|---|---|---|
| **👯‍♀️ Besties (`besties` / `闺蜜`)** | **36** | `d01` – `d36` | Cheek-to-cheek selfie (`Besties`), Twin heart hands, Boba cheers (`Boba time`), Whispering gossip (`Hot tea!`), Protective hug (`Who bullied you?`), High-five (`Got me`) |
| **👩‍❤️‍👨 Couple (`couple` / `情侣`)** | **36** | `d37` – `d72` | Affectionate head pat (`Good girl`), Back hug (`Recharging`), Cheek pinch (`Adore you`), Forehead touch (`Only you`), Sleeve tug (`Stay with me`), Shared winter scarf |
| **🌸 Yuri / GL (`yuri` / `百合`)** | **36** | `d73` – `d108` | Fingertip chin-lift gaze (`Look at me, Unnie`), Cinematic cheek touch (`Meant to be`), Cool unnie kabedon (`Heart racing`), Sleeping on shoulder (`Yours only`), Red thread of fate, Eternal vow hands |

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

### Complete Single-Language Sticker Packs (100% English / 100% Korean / 100% Japanese / 100% Chinese)

![All-English Sticker Pack](docs/gallery/images/pack-en.jpg)
![All-Korean Sticker Pack](docs/gallery/images/pack-ko.jpg)
![All-Japanese Sticker Pack](docs/gallery/images/pack-ja.jpg)
![All-Chinese Sticker Pack](docs/gallery/images/pack-zh-CN.jpg)

---

## 23-Platform Export & Social Media Covers

![Social Media Publishing Assets](docs/gallery/images/platforms.jpg)

---

## Quick Start

```bash
# One-click installer (creates .venv and links Skill to ~/.claude/skills & ~/.codex/skills)
./install.sh
source .venv/bin/activate

# Inspect environment, 108 styles & 108 two-person duo presets
wechat-sticker-maker doctor
wechat-sticker-maker styles --region kr
wechat-sticker-maker duo --category yuri --language en

# Single-person pack (Generate AI cutouts ONCE -> output 4 single-language packs: zh-CN, en, ja, ko)
wechat-sticker-maker plan \
  --input photo.jpg \
  --output output/my-portrait-pack \
  --mode both \
  --count 16 \
  --style real-cutout \
  --language auto \
  --languages zh-CN,en,ja,ko \
  --platforms wechat,xiaohongshu,instagram,telegram

wechat-sticker-maker generate --job output/my-portrait-pack/job.json

# Two-person Duo pack (Besties / Couple / Yuri)
wechat-sticker-maker plan \
  --input personA.jpg \
  --partner personB.jpg \
  --duo-category yuri \
  --count 16 \
  --style real-kr-drama \
  --language en \
  --languages zh-CN,en,ja,ko \
  --output output/yuri-duo-pack

wechat-sticker-maker generate --job output/yuri-duo-pack/job.json
```

## Testing

```bash
pytest -v
python scripts/smoke_test.py
```

## License

MIT License. See [`LICENSE`](LICENSE) for details.
