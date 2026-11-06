# WeChat Sticker Maker (ChatGPT / Codex 全平台真人 AI 表情包与梗图 Skill)

![真人表情包展示](docs/gallery/images/hero.jpg)

> **[查看完整真人图库（26 款风格 / 10 款真动图 / 38 款梗图 / 14 类表情） → `docs/gallery/README.md`](docs/gallery/README.md)**

专注于**真人照片（`human-portrait`）**的一键成套表情包与梗图生成（静态 + 动图），严格保留本人真实五官、骨相、肤质、发型与穿搭，**绝不二次元化或变成卡通假脸**，并同时导出到**微信及全部 23 个主流社交 / 聊天平台**：微信、QQ、抖音/快手、小红书、Soul、微博、钉钉、飞书、Telegram、WhatsApp、LINE、KakaoTalk、Discord、Slack、iMessage、Signal、Viber、GIPHY（Instagram / TikTok / Snapchat 贴纸来源）、Instagram、TikTok、X、Facebook 以及通用格式包。

---

## 核心能力与视觉预览

- **纯正真人专属风格（26 款，通用 / 韩系 / 日系 / 中式四大系列）**：默认 `real-cutout`，自动生成微信经典纯白立体模切白边，严禁把真人画成 2D 动漫或扁平卡通。
- **Codex 自带作图能力驱动真动图**：所有挥手、眨眼、歪头、表情变化均由 Codex 自带 AI 生图工具通过 `2×2` 四连拍动作图（`build_sprite_sheet_prompt`）或多帧参考关键帧绘制，Python 仅做非破坏性抠图、躯干基线对齐、加白边、叠字与编码。
- **全类型表情与动作**：132 个表情 × 14 大类，129 种动作库（`references/motion-library.json`），每个表情均配 4 帧 AI 动作分镜。
- **真人梗图 / 抽象图模式**：内置 38 个梗图模板（`references/meme-templates.json`），涵盖 AI 正在思考旋转星芒、检测到中国IP禁止靠近、再说话封你号、已深度思考 999 秒、请求过于频繁、CPU 干烧了、真人黑白高反差梗图等。
- **文字气泡 + 严格单语种**：支持 `caption` 底部字幕 / `bubble` 对话气泡 / `both` / `none` 及 7 种气泡形状；内置 `zh-CN` / `zh-TW` / `en` / `ja` / `ko` 五语口语化文案；**每张表情只用单一语言，绝不双语混排**。
- **全平台母版一键分发**：每个表情生成一次 720px 母版，自动导出 23 个平台的专属尺寸、格式、体积与社交展示图（小红书 3:4 封面、INS Story/Reels、抖音/TikTok 竖版视频、微博九宫格）。

详见 [`references/text-bubbles-and-languages.md`](references/text-bubbles-and-languages.md)、[`references/memes.md`](references/memes.md) 与 [`references/platform-export.md`](references/platform-export.md)。

---

## 内置 26 款真人专属风格（`references/style-presets.json`）

分 **通用 / 韩系 / 日系 / 中式** 四个系列，全部只改变光影、色调和氛围，**本人五官、脸型、发型、穿搭一律不变**，也绝不画成卡通。按系列查看：`wechat-sticker-maker styles --region 韩系`（也可用 `kr` / `jp` / `cn` / `国风`）。

![四大真人摄影风格系列对比](docs/gallery/images/four-series.jpg)

![26 款真人摄影贴纸风格总览](docs/gallery/images/styles-overview.jpg)

### 通用（6）
| 风格 ID (`--style`) | 名称 | 特色 |
|---|---|---|
| `real-cutout` | **真人写真抠图贴纸（默认）** | 保留真实五官肤质、4px 微信经典模切白边 |
| `real-bobblehead` | 真人搞怪大头贴 | 真人五官 + 夸张大头比例、5px 剪纸白边 |
| `real-street-cool` | 真人潮酷街拍 | 杂志直闪街拍质感、高反差光影 |
| `real-vintage-ccd` | 真人复古 CCD | 千禧年 CCD 暖调闪光灯 |
| `real-work-emo` | 真人打工人纪实 | 生无可恋 / 发疯神态抓拍 |
| `real-high-contrast` | 真人黑白高反差 | 黑白高对比，经典梗图首选 |

### 韩系（7）
![韩系 7 款风格](docs/gallery/images/series-kr.jpg)

| 风格 ID | 名称 | 特色 |
|---|---|---|
| `real-kr-idol-selfie` | 韩系爱豆自拍 | 环形灯柔光、水润唇色，比心 / wink |
| `real-kr-glass-skin` | 韩系水光肌清透 | 通透奶油光泽、低饱和裸色调 |
| `real-kr-photocard` | 韩系爱豆小卡 | 粉蓝渐变轮廓光，追星斗图 |
| `real-kr-cafe-film` | 韩系咖啡馆胶片 | 窗边自然光、奶茶米色调 |
| `real-kr-drama` | 韩剧主角氛围 | 电影级柔逆光、浪漫光晕 |
| `real-kr-variety` | 韩综字幕斗图 | Running Man 式夸张反应 + 彩色描边字 |
| `real-purikura` | 韩系人生四格 | 奶油肌拍立得、粉白描边 |

### 日系（6）
![日系 6 款风格](docs/gallery/images/series-jp.jpg)

| 风格 ID | 名称 | 特色 |
|---|---|---|
| `real-jp-airy` | 日系空气感清新 | 微过曝、低对比、淡青淡粉 |
| `real-jp-fuji-film` | 日系富士胶片 | 青绿暗部、细腻颗粒 |
| `real-jp-purikura` | 日系大头贴プリクラ | 高亮美白、粉嫩 kawaii（不放大眼睛） |
| `real-jp-summer` | 日系夏日逆光 | 金色逆光、发丝透光、元气 |
| `real-jp-harajuku` | 日系原宿街头 | 直闪街拍、高饱和撞色 |
| `real-jp-showa` | 日系昭和复古 | 80 年代褪色暖黄、柔焦颗粒 |

### 中式（7）
![中式 7 款风格](docs/gallery/images/series-cn.jpg)

| 风格 ID | 名称 | 特色 |
|---|---|---|
| `real-cn-new-chinese` | 新中式国风写真 | 暖光柔影、朱红与金色点缀 |
| `real-cn-hk-retro` | 港风复古胶片 | 90 年代港片霓虹红绿调 |
| `real-cn-xhs-vibe` | 小红书氛围感 | 奶油柔光、低饱和高级色 |
| `real-cn-douyin` | 抖音网红美颜 | 环形灯高光、元气有梗（不改脸型） |
| `real-cn-studio-retro` | 复古影楼风 | 90 年代老影楼柔焦、土味搞笑 |
| `real-cn-tw-youth` | 台式青春胶片 | 午后暖阳、淡绿怀旧 |
| `real-variety-meme` | 真人综艺花字斗图 | 国综亮黄撞色花字 |

---

## Codex AI 驱动的真动图（4 帧关键帧分镜）

![真人动作 GIF 展示](docs/gallery/images/animated-showcase.gif)

---

## 14 大类真人表情分类

![真人表情分类 1/2](docs/gallery/images/expressions-01.jpg)
![真人表情分类 2/2](docs/gallery/images/expressions-02.jpg)

---

## 38 款真人梗图与抽象图（6 大类）

![真人梗图与抽象图总览](docs/gallery/images/memes-overview.jpg)

---

## 7 种对话气泡与 5 种独立单语种支持

![7 种文字气泡形状](docs/gallery/images/bubbles.jpg)
![单语言严格隔离](docs/gallery/images/languages.jpg)

---

## 全平台自动分发与社交封面导出

![社交平台发布素材](docs/gallery/images/platforms.jpg)

---

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# 查看环境与真人风格库
wechat-sticker-maker doctor
wechat-sticker-maker styles
wechat-sticker-maker styles --region 韩系

# 规划并生成真人表情包
wechat-sticker-maker plan \
  --input photo.jpg \
  --output output/my-portrait-pack \
  --mode both \
  --count 16 \
  --style real-cutout \
  --language zh-CN \
  --platforms wechat,xiaohongshu,instagram,telegram

wechat-sticker-maker generate --job output/my-portrait-pack/job.json

# 单张真人梗图快速生成
wechat-sticker-maker meme -t claude -i photo.jpg -o output/thinking.gif
wechat-sticker-maker meme -t 中国ip -i photo.jpg -o output/china_ip.gif
wechat-sticker-maker meme -t 封号 -i photo.jpg -o output/ban.gif
```

## 测试

```bash
pytest -v
python scripts/smoke_test.py
```

## License

MIT License. See [`LICENSE`](LICENSE) for details.
