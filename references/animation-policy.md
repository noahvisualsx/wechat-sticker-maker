# Animation Policy Reference（Codex 自带作图能力动图规范）

## 0. 核心禁令（严禁单图浮动与 PIL 像素涂改）
- **严禁单图整体浮动/轻摇**：绝对禁止只用 AI 生成 1 张静态人物图，然后在 Python 里对整张图做上下浮动、左右摇晃、缩放字幕来冒充 GIF（即严禁出现“人物轻摇、浮动，字幕轻微缩放，没有独立挥手、眨眼等动作”）。
- **严禁 Python PIL 强行画眼皮或拉伸五官**：Python 只负责切图、抠图、对齐躯干基线、加白边、压字幕和编码 GIF，**绝不允许**用 PIL 在人物脸上画椭圆眼皮或做网格拉伸变形。
- **所有动作帧必须由 Codex 自带作图能力（AI 图像生成工具）直接绘制**：挥手角度变化、自然眨眼/笑眼闭合、歪头点头、嘴部开合等动作，必须由 AI 生图工具画出真实的多帧画面。

---

## 1. 使用 Codex 自带作图能力生成真动图的两种标准方案

### 方案 A（首选推荐）：AI 2×2 四连拍动作序列图（`2×2 Action Sprite Sheet`）
单次调用 Codex 自带作图工具（引用用户原图 / Master Anchor），生成一张 `1024×1024` 的 **2×2 四宫格连续动作分解图**（纯白或透明背景，无网格分割线、无文字），4 个象限由 AI 直接画出同一角色的 4 个连续动作关键帧（具体分镜见 `references/expression-presets.json` 中每个表情的 `keyframe_poses`）：

- **Top-Left（第 1 帧 - 基准帧）**：人物半身正对镜头，睁眼微笑，手部处于挥手/手势起始位置（如手掌偏左），下半身躯干稳定。
- **Top-Right（第 2 帧 - 眨眼+动作中段）**：同一人物、同一服装与下半身位置，**双眼自然闭合眨眼（或弯月笑眼）**，手掌摆动到中间位置。
- **Bottom-Left（第 3 帧 - 动作幅度峰值）**：同一人物、同一服装与下半身位置，双眼睁开有神、笑容放大（或张嘴欢呼/嘟嘴），手掌摆动到右侧位置。
- **Bottom-Right（第 4 帧 - 回位过渡帧）**：同一人物、同一服装与下半身位置，单眼俏皮眨眼（Wink）或头部轻微歪斜，手掌向中间回摆。

#### 配套 Prompt 生成与 Python 一键切帧合成代码：
```python
from pathlib import Path
from sticker_maker.prompts import build_sprite_sheet_prompt
from sticker_maker.processing.gif_encoder import assemble_gif_from_sprite_sheet

# 1. 生成供 Codex 自带作图工具使用的 2x2 四连拍动作 Prompt：
# sheet_prompt = build_sprite_sheet_prompt(bible, expression_item, style="real-cutout")
# （调用 Codex 自带作图工具生成 1024x1024 四连拍图并保存为 work/raw_gif/01_hello_sheet_raw.png）

# 2. 使用内置非破坏性切帧与躯干基线对齐器，一键输出静态 PNG（取第 1 帧）和 8 帧循环 GIF：
assemble_gif_from_sprite_sheet(
    sheet_path=Path("work/raw_gif/01_hello_sheet_raw.png"),
    gif_output_path=Path("animated/01_hello.gif"),
    static_output_path=Path("static/01_hello.png"),
    caption="你好",
    style="real-cutout",
    frame_duration_ms=150,
    target_frames=8,
)
```
或直接通过 CLI 调用：
```bash
wechat-sticker-maker assemble-gif \
  --sprite-sheet work/raw_gif/01_hello_sheet_raw.png \
  --output animated/01_hello.gif \
  --static-output static/01_hello.png \
  --caption "你好" \
  --style real-cutout
```

---

### 方案 B（高精逐帧模式）：AI 多帧参考连续重绘（`Multi-Pass AI Keyframes`）
对每个表情，使用 Codex 自带作图工具依次生成 2～4 张独立关键帧图片：
1. **生成第 1 帧（`f1.png`）**：以原图/Anchor 为参考，生成睁眼微笑、手在左侧的基准姿势。
2. **生成第 2 帧（`f2.png`）**：以 `f1.png` 为参考图（Image Edit / Reference），Prompt 要求：*“严格保持与第 1 帧完全相同的人物身份、发型、衣服与下半身位置，仅将抬起的手掌向右摆动，并将双眼改为自然眨眼闭合状态”*。
3. **生成第 3 帧（`f3.png`）**：以 `f1.png` 为参考图，Prompt 要求：*“严格保持与第 1 帧相同的人物与下半身位置，手掌摆至最右侧，睁眼露齿笑”*。
4. 调用 `assemble_gif_from_keyframe_files([f1, f2, f3], ...)` 自动对齐下半身躯干中心与底边基线、加白色模切描边与静止字幕，按 `0-1-2-1` 乒乓循环编码为 `240×240` 透明 GIF。

---

## 2. 躯干基线对齐与帧率规范
- **统一缩放与下半身锚定（`align_ai_keyframes`）**：
  - 自动以第 1 帧人物高度为基准统一缩放比例，彻底消除多宫格或多帧之间忽大忽小的“呼吸抖动”。
  - 自动计算人物底部 35%（腰部/胸口躯干区，不受单侧挥手宽度影响）的水平质心与底边 `anchor_bottom_y`，确保挥手时人物身体稳如磐石、绝不左右横移。
- **底部字幕静止清晰**：所有风格的 `caption_animation` 默认设为 `"none"`，底部中文大字固定不缩放、不晃动。
- **帧率与循环**：默认 8 帧（4 个 AI 关键帧按 `0-1-2-3-2-1-0-1` 乒乓循环），单帧时长 `150ms`（总周期 `1.2s`），`loop=0` 无限循环，1-bit 透明索引 `transparency=0` + `disposal=2`。

## 3. 动图里的文字气泡与多平台
- 气泡/字幕属于**文字叠加层**，与角色动作无关：角色动作永远来自 AI 关键帧；气泡可设 `bubble_animation`（`none` 默认静止 / `pop` 弹出 / `typewriter` 逐字 / `bob` 仅气泡轻浮），字幕始终静止。
- 生成关键帧时 Prompt 会要求为气泡预留角落空白（`composition_hint`），所有关键帧共用同一气泡位置，尾巴指向第 1 帧角色头部。
- 动图母版（720px、无损 WEBP）会按平台转成 GIF / APNG（LINE、Discord、iMessage、Signal）/ 动态 WEBP（WhatsApp）/ WEBM VP9（Telegram ≤3s）/ MP4（Reels、TikTok、抖音、小红书视频），时长超限会自动加速，详见 `references/platform-export.md`。
