# WeChat Sticker Maker (ChatGPT / Codex 微信 AI 表情包 Skill)

基于单张人物、宠物或卡通参考照片，一键自动化制作符合微信表情开放平台标准的成套微信表情包（支持静态 PNG 与动态 GIF）。

## 核心特性

- **单图输入，身份锁定**：自动校正 EXIF、计算真实 SHA256，生成可复用的角色规范（`character.json`）与正面主锚点图（Master Anchor）。
- **真正逐张输出**：支持 8 / 16 / 24 张标准预设表情，每张独立输出，严禁以拼接多宫格替代交付。
- **双模态输出**：
  - **静态 PNG**：240 × 240，透明背景，安全边距保护，中文文字矢量级排版与抗锯齿描边。
  - **动态 GIF**：支持 GPT Image 2.6 原生 GIF 生成与关键帧局部动作插值合成（自动降级与回退机制），无限循环（`loop=0`），无鬼影（`disposal=2`）。
- **确定性后处理与优化**：Lanczos 高精度缩放、中文字体排版与避让、1-bit 透明度调色板优化、500KB 体积约束。
- **严格质量校验与分包**：
  - 自动执行结构性格式、尺寸、多帧检测、透明度检测。
  - 输出 `qa/report.json`、`qa/report.md` 以及用于内部审核的联系表 `qa/preview-sheet.png`。
  - 自动归档 `static-pack.zip` 与 `animated-pack.zip`，隔离凭证与原始素材，具备防路径穿越安全保障。

## 安装与快速开始

### 1. 环境准备

```bash
python3 -m venv .venv
source .venv/bin/activate       # macOS / Linux
pip install -e '.[dev]'
```

### 2. 环境体检

```bash
python -m sticker_maker.cli doctor
```

### 3. 一键工作流

```bash
# 1. 任务规划
python -m sticker_maker.cli plan \
  --input input/my_cat.png \
  --output output/cat-pack \
  --mode both \
  --count 16

# 2. 生成表情（支持 fake 离线模式或 openai 生产模式）
python -m sticker_maker.cli generate \
  --job output/cat-pack/job.json \
  --provider auto

# 3. 规范校验
python -m sticker_maker.cli validate \
  --output output/cat-pack

# 4. 严格打包
python -m sticker_maker.cli package \
  --output output/cat-pack --strict

# 单张不满意时重做特定表情（不重跑整个包）：
python -m sticker_maker.cli regenerate \
  --job output/cat-pack/job.json \
  --item 05_shy
```

## 测试

```bash
# 执行全部单元测试与集成测试
pytest -v

# 执行冒烟测试脚本
python scripts/smoke_test.py
```
