# 全平台导出规范（Platform Export）

所有平台共享**同一套母版**：每个表情只用 AI 画一次（静态 + 动作关键帧），在 `master_size`（默认 720px）上合成字幕/气泡，存到 `work/master/`；然后按 `references/platform-profiles.json` 为每个平台各自缩放、留边、转码、压缩体积、校验、打包。新增平台只需在 JSON 里加一个 profile。

## 1. 平台一览（`wechat-sticker-maker platforms` 查看完整规格）
| 平台 id | 名称 | 类型 | 主要产物 |
|---|---|---|---|
| `wechat` | 微信表情开放平台 | 表情商店 | 240 PNG/GIF ≤500KB、120 缩略图、封面/图标/横幅（根目录 static/ animated/ thumbnails/ platform/） |
| `qq` | QQ 表情 | 表情商店 | 240 PNG/GIF + 120 缩略图 |
| `douyin` | 抖音 / 快手 | 内容 + 聊天 | 300 GIF/PNG 聊天表情、3:4 封面与九宫格、9:16 MP4 展示视频 |
| `xiaohongshu` | 小红书 | 内容 | 3:4 封面、九宫格合集页、单张展示页、透明原图、MP4 视频笔记 |
| `soul` | Soul | 聊天 | 300 PNG/GIF 自定义表情、瞬间 1:1 九宫格 |
| `weibo` | 微博 | 内容 | 480 GIF、九宫格 9 张方图 |
| `dingtalk` / `feishu` | 钉钉 / 飞书 | 聊天 | 240 PNG/GIF（飞书另含 128 企业表情） |
| `telegram` | Telegram | 表情商店 | 512 WEBP 静态、512 WEBM(VP9) 视频贴纸 ≤256KB ≤3s、100 Emoji、包图标 |
| `whatsapp` | WhatsApp | 表情商店 | 512 WEBP（静态 ≤100KB / 动态 ≤500KB）、96 托盘图标、3–30 张 |
| `line` | LINE | 表情商店 | 370×320 PNG、320×270 APNG（≤4s、循环、≤300KB）、main/tab |
| `kakaotalk` | KakaoTalk | 表情商店 | 360 PNG（32 张）/ 360 GIF（24 张） |
| `discord` | Discord | 聊天 | 320 贴纸 PNG/APNG ≤512KB + 128 Emoji |
| `slack` | Slack | 聊天 | 128 Emoji PNG/GIF ≤128KB |
| `imessage` | iMessage | 表情商店 | 408 PNG/APNG ≤500KB |
| `signal` / `viber` | Signal / Viber | 表情商店 | 512 WEBP/APNG / 490 PNG |
| `giphy` | GIPHY | GIF 库 | 480 透明 GIF —— **Instagram Story、TikTok、Snapchat、Messenger 里的 GIF 贴纸都来自 GIPHY** |
| `instagram` | Instagram | 内容 | 4:5 轮播合集、9:16 Story、Reels MP4 + GIPHY 套装 |
| `tiktok` | TikTok | 内容 | 9:16 照片轮播、竖版 MP4 + GIPHY 套装 |
| `x` / `facebook` | X / Facebook | 内容 | GIF 动图 + 合集图 |
| `generic` | 通用包 | 通用 | 512 PNG/GIF/动态 WEBP |

- 别名：`ins`/`ig`→instagram、`xhs`/`小红书`/`rednote`→xiaohongshu、`抖音`/`快手`→douyin、`tg`→telegram、`wa`→whatsapp、`kakao`→kakaotalk、`twitter`→x、`snapchat`→giphy。
- 分组：`china`、`global-chat`、`social`、`sticker-stores`，或 `all`。

## 2. 目录结构
```
<output>/
  static/ animated/ thumbnails/ platform/        # 微信（保持原有结构）+ static-pack.zip / animated-pack.zip
  work/master/{id}_static.png | {id}_anim.webp   # 母版（不打包）
  exports/<platform>/<set>/static|animated/...   # 各平台贴纸文件
  exports/<platform>/assets/                     # 托盘图标 / tab / main / 包图标
  exports/<platform>/showcase/                   # 小红书/ins/抖音/TikTok/微博 发布用封面、九宫格、Story、MP4
  exports/<platform>/README.md                   # 中文上传说明
  exports/<platform>/qa-report.md|json           # 平台校验（尺寸/体积/格式/帧数/时长/透明）
  exports/<platform>-pack.zip
```

## 3. 规则
- 数量：微信只允许 8/16/24；不导出微信时 `count` 可为 1–120，并按各平台 `pack_counts`/`min_count`/`max_count` 给出警告（如 WhatsApp 3–30、LINE 8–40、Kakao 24/32）。
- 体积超限时自动逐级压缩：PNG→调色板量化；WEBP→降质量；GIF→减色→抽帧；APNG→量化→抽帧；WEBM→提高 CRF。
- 时长超限（Telegram 3s、LINE 4s、Signal 3s）自动加快帧速；LINE 自动计算循环次数使总播放 ≤4s。
- WEBM/MP4 需要本机 `ffmpeg`（含 libvpx-vp9 / libx264）；缺失时跳过并写入 README/QA 报告。
- `wechat-sticker-maker export -j job.json --platforms telegram,line` 可在已生成的母版上**追加导出**新平台，不重新调用 AI 生图。
- ⚠️ 规格为 2026-11 工程基线，平台随时可能调整；所有 profile 均 `requires_manual_recheck`，提交前务必在官方后台复核。
