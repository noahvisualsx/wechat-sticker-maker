# WeChat Sticker Maker — ChatGPT / Codex 微信 AI 表情包 Skill 开发文档

> **版本**：v1.0（设计与实施规格）  
> **更新日期**：2026-11-05  
> **目标环境**：ChatGPT、Codex CLI / Desktop、Python 3.11+  
> **项目代号**：`wechat-sticker-maker`  
> **文档状态**：开发设计，不代表代码已实现或平台已审核通过

---

## 0. 文档导读与关键决定

本项目的目标是：**用户只上传一张人物、宠物或卡通角色照片，即可制作一套角色统一、情绪丰富、适合微信使用的表情包，同时支持静态 PNG 与动态 GIF。**

核心原则：

1. **一图输入**：默认参数齐全；只在参考图模糊、主体不明或涉及必要权限时才要求补充。
2. **一致性优先**：将角色身份锚点（脸部、发型、毛色、花纹、服装、配饰）固化为可复用的角色规范，独立生成的每张表情必须遵守。
3. **真正逐张输出**：16 张表情必须是 16 个独立文件，不能用四宫格、九宫格或拼图当作交付。可以额外提供预览图，但它不能替代原始文件。
4. **两种生成模式**：静态 PNG 与动态 GIF 同时支持；动态再分原生 GIF 和关键帧合成两条技术路径。
5. **确定性后处理**：文字排版、尺寸、透明度、压缩、文件命名、校验和压缩包由脚本完成，不交给图像模型碰运气。
6. **真实可用**：生成失败即报告失败，不创建空白占位文件冒充完成；合规检查与视觉检查分开进行。
7. **平台规则可配置**：微信表情开放平台的数量、尺寸、格式和体积限制可能调整；提交前须复核官方页面。

### 0.1 2026 年 11 月的能力现状

- ChatGPT Images 2.6 已在 ChatGPT 中逐步推出 GIF 创建功能，能够根据文本或上传静态图创建循环动画，用户可调整播放速度。该界面能力是否可由某个 Skill 在具体运行环境中直接调用，取决于可用工具与授权。
- GPT Image 2.6 **Sunburst** 与 **Flare** 在 **Image API 的生成端点**支持 `output_format: "gif"`；可设 `frame_count`（2–64）及 `frame_duration_ms`（20–2000，按 10ms 取整）。
- **图像编辑端点不支持直接输出 GIF**。因此，需要精确继承用户上传角色照片时，推荐先编辑生成稳定的静态锚点，再采用逐帧编辑 + Pillow 合成；原生 GIF 是可选的速度优化路径，不应假定一定能保持原照片身份。
- 目前官方文档对部分 SDK/参考页面的格式枚举更新节奏可能不同。本项目应对 API 能力做运行时探测，并准备降级，而不是只信 SDK 的静态类型枚举。

官方依据：

- ChatGPT Images 产品说明：https://help.openai.com/en/articles/11084440-images-in-chatgpt
- ChatGPT 更新日志：https://help.openai.com/en/articles/6825453-chatgpt-release-notes
- Image API 指南（含原生 GIF）：https://developers.openai.com/api/docs/guides/image-generation
- Skill 标准：https://developers.openai.com/plugins/build/skills

---

## 1. 产品范围

### 1.1 使用方式

**ChatGPT 用户示例：**

> 用这张猫咪照片做 16 张可爱微信表情包，既要静态版也要动态版。文字用中文，背景透明，角色始终是同一只猫。

**Codex 用户示例：**

```text
$wechat-sticker-maker
用 input/cat.jpg 生成 16 张 Q 版表情，静态和动态都要，导出到 out/cat-pack。
```

### 1.2 功能等级

| 优先级 | 功能 | 验收口径 |
|---|---|---|
| P0 | 单张参考图、自动角色规范 | `character.json` 形成稳定身份锚点 |
| P0 | 8 / 16 / 24 张静态 PNG | 每张独立文件；PNG 可打开、尺寸正确 |
| P0 | 透明背景 + 中文文字 | 没有乱码，角色主体清晰，文字位置合理 |
| P0 | 规范化导出 + ZIP + manifest | 自动生成并校验 |
| P0 | 16 张预设动作与文案 | 表情语义互不混淆 |
| P1 | 动态 GIF（关键帧合成） | 真正有可见动作且无跳帧、鬼影 |
| P1 | 动态 GIF（原生生成） | 支持能力检测、生成、校验与回退 |
| P1 | 失败重试 / 只重做某一张 | 不重跑整个表情包 |
| P1 | 自动和人工视觉质检 | 输出逐项质检报告 |
| P2 | 多种风格与模板商店 | 样式可插拔 |
| P2 | 分发为 ChatGPT Plugin / MCP 工具 | 单独设计权限及发布流程 |
| 暂不实现 | 自动登录、自动代发微信表情开放平台 | 避免账号操作和平台流程不稳定 |

### 1.3 非目标

- 不承诺生成图与上传照片像素级一致（特别是夸张 Q 版风格）。
- 不承诺一键自动通过微信平台审核。
- 不承诺原生 GIF 模型直接引用上传照片的身份信息；该能力必须通过已支持的具体接口验证。
- 不在未授权情况下保存上传照片或将其公开展示。

---

## 2. 使用场景、默认配置与交互

### 2.1 默认参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `mode` | `both` | `static`、`animated`、`both` |
| `count` | `16` | 常用 8/16/24；最终以平台实际要求为准 |
| `style` | `kawaii-flat` | Q版扁平、圆润描边、柔和马卡龙色 |
| `background` | `transparent` | 每张独立透明画布 |
| `language` | `zh-CN` | 中文简体文字 |
| `canvas_px` | `240` | 导出边长；生成时优先大图再缩小 |
| `animation_backend` | `auto` | 优先高一致性；可设置 `native-gif` 或 `keyframes` |
| `gif_frames` | `8` | 每张 GIF 的目标帧数，可由动作配置覆盖 |
| `gif_frame_duration_ms` | `180` | 动画约 1.44 秒/圈；实际可按动作调整 |
| `loop` | `0` | GIF 无限循环 |
| `text_placement` | `bottom` | 底部留文字安全区 |
| `delivery` | `zip+files+report` | ZIP、独立素材、质检报告 |

### 2.2 交互规则

- 若用户仅给一张清晰照片，默认直接启动，不要额外询问风格、数量或动作。
- 对多人物照片，优先使用照片中最显著的主体；如果主体不可判断，询问一次。
- 如果用户明确要求“4 张不同服装”，只变更对应造型，其他特征保持一致。
- 重做某个表情时，复用同一个 `character.json`、固定参考图和风格参数。
- 如果系统没有本地文件写入能力，先输出能做到的独立图片或 GIF，并说明无法自动完成 ZIP / 校验；绝不假装已打包。

---

## 3. 技术架构

```text
                      ┌──────────────────────────┐
                      │ ChatGPT / Codex 用户输入  │
                      │ 参考照片 + 可选偏好        │
                      └────────────┬─────────────┘
                                   │
                     ┌─────────────▼──────────────┐
                     │ Orchestrator（Skill）       │
                     │ 参数规范化 / 任务状态       │
                     └─────────────┬──────────────┘
                                   │
               ┌───────────────────▼───────────────────┐
               │ Character Analyzer / Identity Bible    │
               │ 角色特征、色板、禁止漂移属性、锚点图     │
               └───────────────────┬───────────────────┘
                                   │
                       ┌───────────▼───────────┐
                       │ Expression Planner     │
                       │ 16 组情绪、动作、文案   │
                       └───────────┬───────────┘
                                   │
                  ┌────────────────┴────────────────┐
                  ▼                                 ▼
          Static Renderer                     GIF Renderer
          图像编辑 / 生图                     ├─ Native GIF（快）
          reference → PNG                    └─ Keyframes（稳）
                  │                                 │
                  └────────────────┬────────────────┘
                                   ▼
                         Post-processor
                  透明背景、文字、尺寸、压缩、循环
                                   │
                                   ▼
                        QA / Validation
                  文件检查 + 图像一致性 + 人工复核
                                   │
                                   ▼
                        Package / Manifest
                 静态包、动态包、预览、报告、ZIP
```

### 3.1 设计边界

**Skill：** 负责判断何时触发、读取支持文件、调用可用工具/脚本、处理失败和交付总结。  
**图像提供者（Provider）：** 负责静态图编辑、图像生成或原生 GIF。  
**本地管线：** 负责文件读写、裁剪缩放、加字、GIF 编码、量化、压缩和校验。  
**可选 MCP：** 仅当需要给受限 ChatGPT 客户端提供专用云端文件处理能力时增加，不是 MVP 前提。

### 3.2 两端能力矩阵

| 能力 | ChatGPT 原生会话 | Codex 本地脚本 |
|---|---|---|
| 通过自然语言规划动作 | 是 | 是 |
| 参考照片生成静态图 | 取决于当前可用图像工具 | 可用 Images API |
| 请求 ChatGPT 原生 GIF | 功能正在推出，视账号与客户端而定 | 不直接调用 ChatGPT UI |
| 原生 GIF API | 仅在提供相应接口/工具时 | GPT Image 2.6 生成端点 |
| 参考图逐帧编辑 | 视工具而定 | 可由 Images API 实现 |
| 批量写文件、自动处理透明像素 | 需代码/文件执行环境 | Python 脚本 |
| ZIP / 质量检测 | 需文件工具 | 完整支持 |

---

## 4. 推荐项目目录

```text
wechat-sticker-maker/
├── SKILL.md                          # 必需：简短工作流和触发规则
├── agents/
│   └── openai.yaml                   # 可选：界面元数据/可用依赖
├── references/
│   ├── character-consistency.md      # 锚点生成与身份一致性
│   ├── animation-policy.md            # 动作/循环/关键帧策略
│   ├── wechat-export.md               # 微信素材规格配置说明
│   ├── prompting.md                   # 提示词模板、负面约束
│   └── expression-presets.json        # 8/16/24 动作库
├── assets/
│   └── fonts/README.md                # 字体授权和配置，不打包无授权字体
├── src/sticker_maker/
│   ├── __init__.py
│   ├── cli.py                         # 唯一入口：plan/generate/validate/package
│   ├── config.py                      # Pydantic/Dataclass 配置
│   ├── schemas.py                     # 输入、角色、任务、产物协议
│   ├── orchestrator.py                # 状态机与编排
│   ├── analyzer.py                    # 角色识别与规范
│   ├── planner.py                     # 动作库和文案选择
│   ├── prompts.py                     # 稳定提示词拼装
│   ├── providers/
│   │   ├── base.py                    # 抽象接口
│   │   ├── openai_images.py           # 静态图片/图片编辑
│   │   └── openai_native_gif.py       # 2.6 原生 GIF 生成
│   ├── processing/
│   │   ├── alpha.py                   # 透明背景与边缘
│   │   ├── typography.py              # 中文加字
│   │   ├── resize.py                  # 高质量缩放
│   │   ├── gif_encoder.py             # 关键帧合成
│   │   └── optimizer.py               # 体积优化
│   ├── quality/
│   │   ├── structural.py              # 格式 / 尺寸 / 帧 / 大小
│   │   ├── visual.py                  # 身份/内容一致性辅助检测
│   │   └── report.py
│   └── package.py
├── scripts/
│   ├── smoke_test.py
│   └── make_test_fixture.py
├── tests/
│   ├── fixtures/
│   ├── test_config.py
│   ├── test_planner.py
│   ├── test_typography.py
│   ├── test_gif_encoder.py
│   ├── test_validator.py
│   ├── test_package.py
│   └── test_provider_contract.py
├── pyproject.toml
├── .env.example
└── README.md
```

说明：面向**安装的 Skill**可以只保留 `SKILL.md`、`agents/`、`references/`、`assets/` 与实际运行所需脚本。面向**开发的代码仓库**则应保留 `src/`、`tests/`、`README.md` 等工程文件。不要把开发仓库所有临时产物塞进技能发现目录。

---

## 5. 核心数据契约

### 5.1 `job.json`（输入任务）

```json
{
  "job_id": "20261105-cat-001",
  "source_image": "input/cat.png",
  "output_dir": "output/20261105-cat-001",
  "mode": "both",
  "count": 16,
  "style": "kawaii-flat",
  "language": "zh-CN",
  "background": "transparent",
  "animation": {
    "backend": "auto",
    "frames": 8,
    "frame_duration_ms": 180,
    "loop": 0
  },
  "export_profile": "wechat-conservative-2026-11",
  "allow_cloud_upload": true,
  "keep_source": false
}
```

约束：

- `source_image` 必须是实际存在、可解码的文件；处理前纠正 EXIF 方向。
- `job_id` 必须经过安全规范化（字母、数字、`-`、`_`）；不得按用户提供字符串直接拼接任意路径。
- `allow_cloud_upload=false` 时，不可调用将原照片传到云端的 Provider。
- `count` 需与对应表情预设长度相同，或通过可复现的规则选择前 N 个动作。

### 5.2 `character.json`（身份锚点）

```json
{
  "character_id": "cat-001",
  "source_sha256": "<actual_sha256>",
  "subject_type": "pet-cat",
  "identity_facts": [
    "奶白色短毛猫，圆脸",
    "杏仁形大眼，粉色小鼻子",
    "右耳尖有一小块浅灰色毛",
    "短小圆润四肢"
  ],
  "locked_attributes": [
    "毛色和斑纹位置",
    "五官间距",
    "耳朵形状",
    "眼睛主色",
    "身体比例"
  ],
  "allowed_variation": [
    "表情变化",
    "头部小角度转动",
    "手部动作",
    "少量装饰元素"
  ],
  "render_style": {
    "outline": "round-uniform",
    "palette": ["#FFF6EA", "#F7BDC9", "#987C7B"],
    "lighting": "soft-flat",
    "composition": "single-character-centered"
  },
  "master_anchor": "work/character-anchor.png",
  "reference_image": "input/cat.png"
}
```

`source_sha256` 应从真实文件计算，不能填示例值。身份事实必须基于可见信息，不能凭空添加耳环、纹身、独特胎记或衣服图案。对于人像，不要擅自推断身份、民族、健康或其他敏感属性。

### 5.3 `manifest.json`（输出交付）

```json
{
  "schema_version": "1.0",
  "job_id": "20261105-cat-001",
  "mode": "both",
  "character_id": "cat-001",
  "generated_count": {"static": 16, "animated": 16},
  "items": [
    {
      "id": "01_hello",
      "caption": "你好",
      "static_path": "static/01_hello.png",
      "animated_path": "animated/01_hello.gif",
      "thumbnail_path": "thumbnails/01_hello.png",
      "checks": {"structural": "pass", "visual": "reviewed"}
    }
  ],
  "validation_report": "qa/report.json",
  "created_at": "<real_utc_iso8601>"
}
```

**每个文件路径必须指向真实存在的文件**；`generated_count` 从实际产物统计，不从预期数量硬填。

---

## 6. 角色一致性设计（最关键）

### 6.1 必须区分三种一致性

1. **身份一致性**：用户是否能一眼认出这是上传照片中的同一个角色。
2. **视觉系统一致性**：描边粗细、色板、贴纸边缘、阴影、风格是否统一。
3. **时序一致性**：GIF 连续帧的脸、服装、位置和背景不应随机漂移。

### 6.2 建立“角色圣经”流程

```text
source photo
  → 自动纠正旋转、裁剪主体、清理背景
  → 角色可见特征分析
  → 固定 identity_facts / locked_attributes
  → 生成 1 张无字、正面、中性表情角色锚点（master anchor）
  → 人工或视觉评估检查身份
  → 使用同一锚点生成所有静态表情
```

推荐把**原照片**和**角色锚点**同时交给支持多图输入的图像编辑后端。原图约束“是谁”，锚点约束“画风长什么样”。如果图片编辑请求的多图输入或参数被当前模型拒绝，降级为单参考图编辑，并在报告中记录。

### 6.3 提示词结构：禁止把动作直接覆盖身份锚点

每次出图时构建以下固定块：

```text
[IDENTITY LOCK]
Use the supplied photo and canonical character anchor.
Preserve the same subject identity, face structure, hairstyle/fur pattern,
clothing and unique non-sensitive visible details. Do not redesign the character.

[STYLE LOCK]
Consistent kawaii sticker illustration, clean rounded linework,
soft pastel palette, expressive yet recognizable features.
One single character only, transparent background, centered composition.

[ACTION]
Expression: shy / blushing.
Action: shoulders slightly raised, hands near cheeks, eyes briefly glance away.

[COMPOSITION]
Square canvas. Keep subject inside a safe central area.
Reserve lower space for separate typography; do not draw text into image.

[NEGATIVE]
No extra subjects, no collages, no grid layout, no watermark,
no random outfit changes, no extra limbs, no background scene,
no letters or words in the raster illustration.
```

### 6.4 一致性校验建议

| 维度 | 自动检查 | 人工检查 |
|---|---|---|
| 角色数量 | 简单目标检测 / VLM 辅助 | 必须为单角色 |
| 配色 | 主颜色分布差异 | 同套视觉系统 |
| 独有特征 | VLM 对照锚点问答 | 耳朵花纹、发型等不漂移 |
| 构图 | bbox / 安全边距 | 不裁手脚或尾巴 |
| 文案 | 与 preset 文案严格比对 | 语义和画面一致 |
| 动画 | 差分、抖动、循环检测 | 无换脸、无鬼影 |

视觉评分不能仅用“一个相似度数字”替代人工审核。可设置 `pass`、`warn`、`fail`，对明显异常的单张重生最多 2–3 次；超过预算停止并报告。

---

## 7. 表情动作库设计

### 7.1 默认 16 张预设

| ID | 文字 | 情绪 | 静态姿势 | 动态动作 |
|---|---|---|---|---|
| 01 | 你好 | 友好 | 面向前方抬手 | 挥手 2 次 |
| 02 | 早安 | 元气 | 双手伸懒腰 | 伸懒腰、眨眼 |
| 03 | 晚安 | 困倦 | 抱枕闭眼 | 点头困倦 |
| 04 | 哈哈哈 | 开心 | 张口大笑 | 身体轻轻弹跳 |
| 05 | 害羞 | 腼腆 | 双手捂脸 | 脸红、眼神躲闪 |
| 06 | 哭哭 | 伤心 | 眼泪汪汪 | 眼泪滑落 |
| 07 | 生气 | 愤怒 | 双手叉腰 | 轻轻跺脚 |
| 08 | 无语 | 无奈 | 眯眼 | 眼皮慢慢下垂 |
| 09 | 收到 | 肯定 | 竖大拇指 | 点头 1 次 |
| 10 | 加油 | 鼓励 | 举拳 | 小幅挥拳 |
| 11 | 谢谢 | 感谢 | 合掌鞠躬 | 轻轻鞠躬 |
| 12 | 抱抱 | 安慰 | 双臂张开 | 双臂靠近镜头 |
| 13 | 好耶 | 兴奋 | 双手举起 | 小幅跳起 |
| 14 | 疑问 | 困惑 | 头歪向一边 | 左右歪头 |
| 15 | 拜拜 | 告别 | 侧身挥手 | 挥手和眨眼 |
| 16 | 爱你 | 喜爱 | 手捧小爱心 | 爱心轻微跳动 |

扩展至 24 张时建议新增：`在吗`、`等等`、`OK`、`求求`、`吃饭啦`、`睡觉啦`、`委屈`、`震惊`。8 张版从默认 16 中选择高频动作，不仅截取前 8 张。

### 7.2 数据化动作预设

```json
{
  "id": "05_shy",
  "caption": "害羞",
  "mood": "shy",
  "static_pose": "hands near cheeks, blushing, glance aside",
  "motion": {
    "type": "blink_and_blush",
    "duration_ms": 1440,
    "frames": 8,
    "loop": "seamless",
    "amplitude": "small",
    "stationary_parts": ["hair_or_fur_pattern", "outfit", "body_silhouette"]
  }
}
```

---

## 8. 图像/动画生成后端

### 8.1 Provider 能力接口

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

@dataclass
class ProviderCapabilities:
    edit_with_reference: bool
    transparent_png: bool
    native_gif: bool
    gif_max_frames: int | None = None

class StickerProvider(Protocol):
    def capabilities(self) -> ProviderCapabilities: ...
    def render_static(
        self, reference_paths: list[Path], prompt: str, output: Path
    ) -> Path: ...
    def render_native_gif(
        self, prompt: str, output: Path,
        frames: int, frame_duration_ms: int
    ) -> Path: ...
```

调用者不得在 Provider 不支持相应能力时硬调用；应切换 `keyframes` 或返回明确错误。

### 8.2 推荐 Provider 策略

**A. 静态图片和关键帧编辑：** 优先选择图像编辑能力稳定、角色还原效果最好的 GPT Image 模型。可将 `gpt-image-2.6-sunburst` 设为候选，但以实际 API 授权、SDK 和响应测试为准；必要时退回 `gpt-image-2.5-sunburst`。

**B. 原生 GIF：** 使用 `gpt-image-2.6-sunburst`（重精度）或 `gpt-image-2.6-flare`（重速度）的 `/v1/images/generations`。**该接口通过文本生成动画，不能把“编辑照片并直接导出 GIF”当作其已保证具备的能力。**

**C. ChatGPT 原生生成：** 在具备 GIF 工具的 ChatGPT 运行环境中，Skill 负责分配动作并逐张调用工具；如果没有文件系统支持，交付形式可能受限。ChatGPT 订阅与 API 使用量计费是两套不同的能力/配额。

### 8.3 原生 GIF API 示例（HTTP，作为实现参考）

```python
import base64
import os
import requests
from pathlib import Path

payload = {
    "model": "gpt-image-2.6-sunburst",
    "prompt": (
        "Create a seamless looping kawaii sticker animation of a cute "
        "cream-colored cat waving. One centered character, stable identity, "
        "clean empty background, no text, gentle continuous motion."
    ),
    "output_format": "gif",
    "frame_count": 8,
    "frame_duration_ms": 180,
    "size": "512x512"
}
response = requests.post(
    "https://api.openai.com/v1/images/generations",
    headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
    json=payload,
    timeout=240,
)
response.raise_for_status()
result = response.json()
Path("hello.gif").write_bytes(base64.b64decode(result["data"][0]["b64_json"]))
```

注意：这是说明调用形态的示例，必须在目标账号用真实 API 请求做兼容测试；不要将它描述成已在本项目环境中成功运行。若返回模型未授权、格式不支持或请求过大，遵守错误分类并降级。

### 8.4 参考图编辑 API 示例（静态 PNG）

```python
import base64
import os
import requests
from pathlib import Path

image_path = Path("input/cat.png")
with image_path.open("rb") as fp:
    response = requests.post(
        "https://api.openai.com/v1/images/edits",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        data={
            "model": "gpt-image-2.5-sunburst",
            "prompt": "<拼接后的角色身份锁定+风格+动作提示词>",
            "output_format": "png",
            "background": "transparent",
            "size": "1024x1024",
        },
        files={"image": (image_path.name, fp, "image/png")},
        timeout=240,
    )
response.raise_for_status()
Path("static_hello_raw.png").write_bytes(
    base64.b64decode(response.json()["data"][0]["b64_json"])
)
```

实施时应根据图片实际类型设置 MIME；编辑多图应按 API 支持的文件/表单结构传入。在此基础上增加 requests session、错误分级、日志、速率限制、超时配置与模型能力探测。

---

## 9. 静态 PNG 流程

### 9.1 流水线

```text
原照片 → 验证与预处理 → 角色锚点 → 动作规划
→ 逐张参考图编辑（不加字）→ 身份/构图初检
→ 自动去背景或透明度精修 → 中文文字层
→ 240×240 输出 → 文件大小优化 → QA → manifest
```

### 9.2 为什么先生成大图再缩小

- 大图便于检视五官、线条和边缘；最终用 Lanczos 缩小到 240 × 240。
- 字体应在最终分辨率或矢量层上单独渲染，避免被模型画错。
- 保留 `work/raw` 与 `work/processed`，交付时只打包需要的最终文件。

### 9.3 文字布局

- 采用有合法授权的中文字体；作为配置路径传入，如 `--font /path/to/font.ttf`。
- 文案区域建议靠下，保留 12–18px 底部安全间距（具体随模板）；字号按短语字数自动调整。
- 文字描边 2–4px，高对比度，避免与白色角色融为一体。
- 使用 Pillow 精确测量字体 bbox 再居中。若文案超过最大宽度，缩字号或换行。
- 中文加字应从配置读取 Unicode 文案，禁止以乱码或英文占位代替。

---

## 10. 动态 GIF：两条正式实现路线

### 10.1 路线 A：原生 GIF 生成（速度优先）

```text
character profile（文本） + action prompt
→ GPT Image 2.6 原生 GIF 生成
→ 解码并检查时长 / 帧数 / 角色一致性
→ 背景/文字后处理（逐帧）
→ 压缩 / 优化 / QA
```

优点：动作可能更流畅、接口调用相对简单。  
不足：当前生成 GIF 接口不等于参考图 GIF 编辑；从文本还原特定真人或宠物更易漂移。主要用于无严格身份要求的原创角色，或经人工验收后启用。

### 10.2 路线 B：参考图关键帧合成（默认推荐）

```text
master anchor
→ 动画分镜（8 帧）
→ 以同一参考图/锚点逐帧编辑
→ 帧一致性对齐、稳定锚点、去除明显漂移
→ 中文文字叠加到每一帧相同位置
→ GIF 编码、透明色处理、帧差异压缩
→ 检测循环接缝 / 质量 / 文件体积
```

为避免 8 张独立编辑引起角色抖动，先从一张确定的 `base pose` 出发，进行**局部动作渐变**；条件许可时使用分层素材（眼睛、手、嘴、脸颊）在本地做运动，而不是每帧完全重绘。优先级：

1. 分层角色 / 固定底图 + 局部层动画（最稳）；
2. 相同锚点 + 帧间约束编辑 + 对齐（较灵活）；
3. 逐帧无关联文生图（不推荐）。

### 10.3 动作时间设计

**害羞**示例：8 帧 × 180ms = 1440ms，每帧动作：

| 帧 | 变化 | 说明 |
|---|---|---|
| 0 | 基准姿态 | 双手贴脸，浅粉腮红 |
| 1 | 眼皮略下垂 | 身体不动 |
| 2 | 视线转开 | 腮红加深 |
| 3 | 闭眼 | 头轻微下倾 |
| 4 | 最害羞 | 腮红最明显 |
| 5 | 眼睛半睁 | 头回正 |
| 6 | 视线回来 | 腮红减弱 |
| 7 | 接近帧 0 | 形成无明显跳变的循环 |

不要让全角色连续位移超出安全画面，不要出现重复闪烁的大面积背景变化。

### 10.4 GIF 工程约束

- 目标分辨率：240 × 240。
- 默认 8 帧、180ms/帧，实际可 6–12 帧；与原生 API 支持范围分别处理。
- `loop=0` 无限循环。
- 导出时确保 GIF 是完整多帧且实际帧内容不同，禁止单帧假动态。
- GIF 使用索引色，透明度一般是 1-bit，不同于 PNG 的连续 alpha。要避免半透明边缘黑边：先在合适的底色下预混合，再有意识地设置透明色；需要测试微信聊天背景的浅色和深色场景。
- 检查每一帧时长、`disposal` 策略和透明色，避免前一帧留下“鬼影”。
- 符合平台大小要求时优先保持动作质量；超过限制先尝试减色、帧差异优化，再考虑减少帧数或分辨率细节。
- 任何优化后都必须重新验证视觉质量和循环属性。

### 10.5 GIF 编码示意

```python
from PIL import Image

frames = [Image.open(p).convert("RGBA") for p in frame_paths]
# 实际项目应先对齐尺寸、处理透明色和调色板，再编码；此处只示范接口。
frames[0].save(
    "out.gif",
    save_all=True,
    append_images=frames[1:],
    duration=[180] * len(frames),
    loop=0,
    disposal=2,
    optimize=True,
)
```

该段代码**不是最终透明 GIF 优化器**：需增加调色板一致性、透明边缘预处理和不同微信背景下的视觉回归测试。

---

## 11. 微信文件规格和导出策略

> 以下为**常见制作基准**，依据公开资料整理，并非对平台截至今天的实时规则作保证。平台管理后台、提交入口及官方最新规范拥有最终优先级。特别是是否需要逐张缩略图、数量规则以及单张体积上限，必须在提交前复核。

| 产物 | 常见规格 | MVP 目标 |
|---|---|---|
| 静态主表情 | PNG，240 × 240 | ≤500KB/张 |
| 动态主表情 | GIF，240 × 240 | ≤500KB/张，循环播放 |
| 每张缩略图 | PNG，120 × 120（视投稿类别） | 目标 ≤50KB |
| 封面 | PNG，240 × 240 | 目标 ≤500KB |
| 聊天面板图标 | PNG，50 × 50 | 目标 ≤100KB |
| 详情横幅 | PNG / JPG，750 × 400 | 目标 ≤500KB |
| 数量 | 常见为 8 / 16 / 24 张 | 分别生成独立静态/动态套装 |

官方入口：https://sticker.weixin.qq.com/  
公开整理参考（非官方）：https://github.com/limboinf/wechat-sticker-skill/blob/main/docs/微信表情包提交规格.md

配置应位于 `references/wechat-export.md` 或 JSON profile，例：

```json
{
  "name": "wechat-conservative-2026-11",
  "sticker": {"size": [240, 240], "max_bytes": 500000},
  "thumbnail": {"size": [120, 120], "max_bytes": 50000},
  "cover": {"size": [240, 240], "max_bytes": 500000},
  "icon": {"size": [50, 50], "max_bytes": 100000},
  "banner": {"size": [750, 400], "max_bytes": 500000},
  "allowed_counts": [8, 16, 24],
  "requires_manual_platform_recheck": true
}
```

**注意：** `500KB` 有时按 500,000 字节、有时按 512,000 字节解释。为减少误判，采用较保守的 500,000 字节内部上限，并把实际文件体积写进报告。

### 11.1 导出文件结构

```text
output/job-001/
├── static/
│   ├── 01_hello.png
│   ├── 02_morning.png
│   └── ...（共 16 个 PNG）
├── animated/
│   ├── 01_hello.gif
│   ├── 02_morning.gif
│   └── ...（共 16 个 GIF）
├── thumbnails/
│   ├── 01_hello.png
│   └── ...
├── platform/
│   ├── cover.png
│   ├── icon.png
│   └── banner.png
├── qa/
│   ├── report.json
│   ├── report.md
│   └── preview-sheet.png        # 仅内部预览，不能代替独立文件
├── manifest.json
├── static-pack.zip
└── animated-pack.zip
```

静态和动态**分开 ZIP**，避免将混合格式误提交为同一套专辑；打包时不应把临时文件、用户原始照片或 API 密钥带进去。

---

## 12. CLI 接口与退出码

统一入口：

```bash
python -m sticker_maker.cli plan \
  --input input/cat.png \
  --mode both --count 16 --style kawaii-flat \
  --output output/cat-pack

python -m sticker_maker.cli generate \
  --job output/cat-pack/job.json \
  --provider openai --animation-backend auto

python -m sticker_maker.cli validate \
  --output output/cat-pack --profile wechat-conservative-2026-11

python -m sticker_maker.cli package \
  --output output/cat-pack --strict
```

| 命令 | 输入 | 输出 | 说明 |
|---|---|---|---|
| `plan` | 源图、模式、风格、数量 | `job.json`、初始动作计划 | 不应发起大量付费生图 |
| `generate` | Job、模型配置 | 静态/动态素材、任务日志 | 支持断点续跑 |
| `regenerate --item 05_shy` | 指定表情 | 覆盖该项中间和最终素材 | 不影响其他项 |
| `validate` | 输出目录、规格 | `report.json/.md` | 可独立执行 |
| `package` | 通过校验的素材 | 2 个 ZIP / manifest | `--strict` 对 fail 拒绝打包 |
| `doctor` | 本地环境 | 依赖、字体、API 能力状态 | 不生成付费素材 |

退出码建议：`0` 成功；`2` 用户输入错误；`3` 环境/依赖缺失；`4` Provider/网络错误；`5` 校验失败；`6` 部分成功；`7` 安全/权限阻止。

### 12.1 配置优先级

`CLI 参数 > job.json > 项目配置 > 默认值`。对模型名称、尺寸、允许输出路径进行白名单或类型约束，避免错误环境变量导致混乱。

### 12.2 环境变量

```dotenv
OPENAI_API_KEY=                 # 从系统环境或密钥管理器读取，不提交到 Git
STICKER_IMAGE_MODEL=gpt-image-2.5-sunburst
STICKER_GIF_MODEL=gpt-image-2.6-sunburst
STICKER_MAX_RETRIES=2
STICKER_MAX_PARALLEL=2
STICKER_FONT_PATH=/absolute/path/to/licensed-chinese-font.ttf
STICKER_LOG_LEVEL=INFO
```

不要默认用 `eval`、动态 shell 拼接或开放用户字符串作为命令路径；最好直接调用 Python API。

---

## 13. `SKILL.md` 建议正文（可作为实际文件初稿）

> 下面为 Skill 的简版核心文案。正式安装时将此段单独保存为 `SKILL.md`，详细规则放入 `references/`。保持 frontmatter 仅包含标准字段，避免把整份开发文档塞进发现元数据。

```markdown
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
```

---

## 14. Codex / ChatGPT 安装和执行

### 14.1 Codex 项目级使用

将 Skill 目录安装到：

```text
<your-project>/.agents/skills/wechat-sticker-maker/
```

用户级目录：

```text
~/.agents/skills/wechat-sticker-maker/
```

创建流程可通过 Codex 的 `$skill-creator` 启动；在项目中启动新的 Codex 会话之后调用 `$wechat-sticker-maker`。需要具备相应 Python 运行环境与 API 密钥。若用户电脑缺少 Node/npm/brew，也可以直接用已安装的 Python 建立环境，不强制依赖这些工具。

### 14.2 Python 环境

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate         # macOS/Linux
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m sticker_maker.cli doctor
```

Windows 激活命令请换成 `.venv\Scripts\activate`。最小依赖建议：`openai` 或 `requests`、`Pillow`、`pydantic`、`PyYAML`、`pytest`、`python-dotenv`。需要更高级视频/GIF 编码时再增加 `imageio`、FFmpeg 或 Pillow 外部工具，而非一开始安装过大的依赖。

### 14.3 ChatGPT 使用

ChatGPT 可理解同一份 `SKILL.md` 的流程规则，但**能否自动执行 Python、创建 ZIP、批量调用 API**，由当前 ChatGPT 产品运行环境、权限与插件工具决定。可以选择：

1. 在 ChatGPT 已具备的图片/GIF 工具中直接按动作逐张生成；
2. 将 Skill 配合可执行脚本/工具使用；
3. 如需跨平台稳定交付，开发一个提供 `plan`、`render`、`validate`、`package` 操作的 MCP 服务，让 ChatGPT 通过授权接口调用。

不要把“粘贴 SKILL.md 到聊天里”误当成已安装了运行工具。

---

## 15. 稳定性与状态机

### 15.1 任务状态

```text
CREATED → SOURCE_VALIDATED → CHARACTER_READY → PLANNED
→ RENDERING_STATIC → RENDERING_ANIMATED → POSTPROCESSING
→ VALIDATING → PACKAGING → COMPLETED
                          ↘ PARTIAL / FAILED
```

每个表情额外记录 `PENDING / RUNNING / SUCCESS / WARNING / FAILED`。使用稳定的输出路径、原子写入（临时文件生成成功后 rename）和逐项 manifest，以支持断点续跑。

### 15.2 错误与恢复策略

| 错误 | 处理 |
|---|---|
| 用户输入文件不存在、无法解码 | 立即停止，报告文件路径 |
| 无法读取授权字体 | 停止加字，提示配置字体；不可用乱码字体顶替 |
| API 401 / 403 | 停止，报告权限问题；不可无限重试 |
| API 429 或临时 5xx | 指数退避、遵循 Retry-After、限制并发 |
| 余额/额度不足 | 停止付费生成，报告已完成数量 |
| 原生 GIF 参数不支持 | 能力降级至关键帧，记录原因 |
| 主体漂移、肢体异常 | 单张重试，保留失败版本供审计 |
| PNG 超过大小上限 | 优化，必要时调整复杂度，不动其他表情 |
| GIF 超过大小上限 | 减色、帧差异优化、缩减非必要帧 |
| ZIP 有遗漏或损坏 | 拒绝标记完成，重新校验打包 |

### 15.3 成本/限流控制

- 生成前计算预估调用数：16 张静态 + 16 个 8 帧 GIF 最多可能超过百次图像生成/编辑请求，成本和耗时不应被低估。
- **先运行 2 张静态 + 1 张动态样品**，确认锚点、画风、透明度和动图质量，然后再批量生成。
- 同一 `job_id` 的中间结果缓存，重试只针对失败项。
- API 并发默认 2，按账号限额调节。
- 记录实际请求数、失败数、模型、用量信息（若返回）和预算上限，但绝不记录 API key。

---

## 16. 质量检测与验收标准

### 16.1 结构性检测（必须自动化）

| 检查项 | 判定标准 |
|---|---|
| 文件存在 | manifest 指向的每个文件真实存在 |
| 独立数量 | 每个模式有恰好 N 个独立主文件 |
| 静态编码 | PNG 可解码，尺寸 240×240 |
| 动态编码 | GIF 可解码，尺寸 240×240，多于 1 个不同帧 |
| 循环 | GIF `loop=0` 或符合指定策略 |
| 帧时间 | 大于 0，符合动作配置，不能长时间冻结 |
| 文件体积 | 不超过当前 profile 的上限 |
| 透明背景 | PNG 有有效 alpha；GIF 透明像素效果正常 |
| 文案 | 与 preset 一致，无空白、乱码、裁切 |
| ZIP | 可以解压、文件数正确、无意外数据 |
| 产物来源 | 原始 source、临时素材和凭据不混入交付包 |

### 16.2 视觉检测（辅助自动 + 人工）

- 同一角色：至少检查正面、侧面、夸张情绪和动图帧的标志性特征。
- 无多余肢体、双头、随机背景、不可解释的服饰替换。
- 表情间动作有差异；不能只有文案不同、动作完全相同。
- 文字无错别字，24/16 张表情里的情绪内容合理。
- GIF 头尾衔接自然、没有明显闪烁或角色瞬间换脸。
- 浅色和深色聊天背景下，贴纸边缘都能正常显示。

### 16.3 质量门槛

- **发布阻断**：缺文件、尺寸错误、GIF 单帧、ZIP 损坏、文案乱码、超出平台规则。
- **单项重做**：主体特征明显漂移、动作不符合文字、严重画面瑕疵。
- **人工提示**：轻微颜色偏差、极小边缘瑕疵或创意程度不足。

不要将未经测量的“角色一致性 98%”作为发布指标。应使用可复核的样品集、清晰判定表和人工标注结果。

---

## 17. 测试计划

### 17.1 单元测试（不调用付费 API）

1. `test_config.py`：默认值，非法数量/路径拒绝，配置优先级。
2. `test_planner.py`：16 张 preset 唯一、文字非空、每个动作有 ID。
3. `test_typography.py`：中英文混排、两行文字、超长文本缩放、字体缺失。
4. `test_gif_encoder.py`：多帧、循环、透明背景、disposal、持续时间、首尾接缝。
5. `test_validator.py`：损坏 PNG、单帧 GIF、过大文件、错误尺寸、错误 manifest。
6. `test_package.py`：ZIP 数量、相对路径、安全、无源文件泄露。
7. `test_provider_contract.py`：模拟 API 返回、401/429/5xx、无 GIF 权限、超时/重试。

### 17.2 集成测试（使用假 Provider）

- 生成 8 张固定位图（单角色）及 8 个不同帧 GIF，完成全流程，断言输出结构和 QA 报告。
- 模拟第 5 张失败，重新执行时仅重做第 5 张。
- 从源图片中读取 EXIF 方向，验证规范化后的尺寸。
- 模拟文字过长，验证自动换行不出界。

### 17.3 实际模型评估（需要 API 额度）

准备 3 类授权测试图：

- `human_portrait.png`：发型与服装有稳定特征的成年人像。
- `pet_cat.png`：有独特毛色花纹的猫。
- `cartoon.png`：原创画风角色。

每张图先生成 **2 张静态 + 1 张 GIF** 样品；通过后再做 16 张套装。对比：

- 2.6 Sunburst 静态编辑 / 2.5 Sunburst 编辑质量；
- 原生 GIF 与关键帧合成的一致性、动作质量、生成成本；
- 图片透明背景和 GIF 在微信实际聊天页面中的显示结果。

### 17.4 推荐测试命令

```bash
python -m pytest -q
python -m sticker_maker.cli doctor
python -m sticker_maker.cli validate --output tests/fixtures/good_pack
python -m sticker_maker.cli validate --output tests/fixtures/broken_pack
```

`good_pack` 必须通过，`broken_pack` 必须按预期失败。测试执行结果应写入 CI 日志，不能只宣称“测试通过”。

### 17.5 验收定义（Definition of Done）

MVP 可以称为完成，当且仅当：

- `SKILL.md` 能在 Codex 被正确发现与调用。
- 一张真实照片可生成 16 张独立静态 PNG，人物/宠物的身份主要特征稳定。
- 每张动图单独输出 GIF，有实际动作、循环可播放、无严重闪烁。
- 文字清楚且正确，严格尺寸和体积检测通过。
- 不成功的单张明确标记，失败重做只处理该项。
- 静态/动态 ZIP 均可解压、文件清单准确。
- 至少有单元测试、模拟集成测试、真实 API 的小规模冒烟测试记录。
- 尚未验证的微信平台要求明确标记“待官方复核”。

---

## 18. 分阶段研发计划（建议的任务拆分）

### Milestone 1：静态 MVP

- M1-01：仓库初始化、Skill 元数据、CLI 和配置 schema。
- M1-02：源图预处理与 `character.json` 生成。
- M1-03：16 张表达式动作库与提示词模板。
- M1-04：静态参考图 Provider、单张失败重试。
- M1-05：中文文字、PNG 缩放与透明背景后处理。
- M1-06：静态 QA、manifest、ZIP。
- M1-07：单测与模拟集成测试。

**M1 验收**：一张图 → 16 张可用静态 PNG + ZIP + 报告。

### Milestone 2：动态 GIF

- M2-01：关键帧调度、角色局部动作模板。
- M2-02：透明 GIF 编码、调色板与帧差异优化。
- M2-03：原生 GIF Provider、能力探测与降级。
- M2-04：动图自动质量检查与样例回归。
- M2-05：动图 ZIP、首尾循环测试、微信环境实测。

**M2 验收**：一张图 → 16 张独立动态 GIF；每个都能循环且角色稳定。

### Milestone 3：完善双端体验

- M3-01：ChatGPT 工具可用性适配、交付说明。
- M3-02：错误定位和某项单独重做。
- M3-03：可选 MCP 服务，以支持受限环境文件处理。
- M3-04：更多画风与动作库，用户级配置模板。
- M3-05：微信平台规格复核与发布辅助材料。

---

## 19. 给 Codex 的执行任务（可复制）

```text
请以当前仓库为目标，实现《WeChat Sticker Maker — ChatGPT / Codex 微信 AI 表情包 Skill 开发文档》所述方案。

重要约束：
1. 先检查仓库现状和 AGENTS.md，不覆盖已有代码。
2. 使用官方 Skill 规范创建 `SKILL.md` 和必要 references。
3. 先实现 Milestone 1：16 张独立 PNG，角色锚点、中文加字、透明背景、文件校验、ZIP、测试。
4. 再实现 Milestone 2：GIF 关键帧合成，并加原生 GIF Provider 和自动降级。
5. 原生 GIF 仅在 GPT Image 2.6 生成端点启用；不得把图片编辑接口虚构为支持 GIF 输出。
6. 图片与动图逐张单独输出，预览拼图只能作为额外文件。
7. 所有模型调用封装为 Provider，配置从环境变量读取，不写死 API 密钥。
8. 先用 Fake Provider 完成测试，再对真实模型做小规模冒烟测试；对需要付费/权限的步骤明示。
9. 以 pyproject.toml、pytest、CLI 和 JSON manifest 构成可维护工程。
10. 逐步执行可运行的测试，最后提供真实生成文件路径、测试结果、未完成事项。

不得在没有生成或验证的情况下报告已完成。若有接口权限或平台规则的未知部分，保留可运行降级路径并明确记录。
```

---

## 20. 风险、安全与版权

- **照片隐私**：默认临时存储，源照片删除或保留由用户选项决定；不得自动将用户照片保存为跨会话参考图。
- **人物授权**：使用真人肖像制作可传播的表情包前，应确认有适当使用授权；禁止冒充或误导性使用。
- **未成年人**：适用额外保护与肖像审慎处理，不进行不适当表现。
- **版权**：不要默认复制第三方知名角色、商标或未经授权的表情包素材；所用字体须有相应授权。
- **凭据**：API key 只存环境变量/密钥管理器；日志中隐藏凭据，不能把 `.env` 打进 ZIP。
- **路径安全**：使用受控输出根目录，拒绝 `../` 路径穿越和不可信扩展名，防止 ZIP Slip。
- **外部操作**：不在未经用户明确授权时自动上传微信平台或公开分享。
- **透明说明**：向用户明确区分“成功生成”“通过自动验证”“在微信平台提交成功”这三种状态。

---

## 21. 需要持续核对的外部文档

| 类别 | 资源 | 核对目的 |
|---|---|---|
| ChatGPT GIF | https://help.openai.com/en/articles/11084440-images-in-chatgpt | 原生生成、编辑与当前限制 |
| ChatGPT 版本 | https://help.openai.com/en/articles/6825453-chatgpt-release-notes | 2.6 GIF rollout 状态 |
| OpenAI Image API | https://developers.openai.com/api/docs/guides/image-generation | GIF 参数、生成模型、编辑能力 |
| GPT Image 2.6 Sunburst | https://developers.openai.com/api/docs/models/gpt-image-2.6-sunburst | 支持能力与额度 |
| Plugin Skill | https://developers.openai.com/plugins/build/skills | SKILL.md、资源、MCP 依赖 |
| Agent Skills API | https://developers.openai.com/api/docs/guides/tools-skills | 安装/上传/执行接口 |
| Codex Skill 目录 | https://developers.openai.com/api/reference/cli | 用户级和项目级 Skill 路径 |
| 微信表情开放平台 | https://sticker.weixin.qq.com/ | 最新平台上传规范与审核规则 |

核对日期：**2026-11-05**。如果未来遇到文档冲突，以当前 API 的运行时响应和最新官方规范为准；所有第三方汇总只作为参考。

---

## 22. 最小落地建议

不要第一天就直接生成 16 张静态 + 16 张动态。推荐：

1. **先用 1 张猫咪照片制作角色锚点。** 验证是否能从照片准确提炼毛色、五官、轮廓和表情风格。
2. **生成“你好”和“害羞”两张独立静态 PNG。** 检验身份锁定、动作差异、透明度与中文文字。
3. **将“害羞”做成一张 8 帧循环 GIF。** 对比原生 GIF 与参考图关键帧合成方案，选择更稳定的后端。
4. **验证体积/尺寸/播放/浅色深色背景。** 失败时只修复这个流程环节。
5. **扩大到 16 张，并建立回归测试。** 发布静态包、动态包、manifest 和 QA 报告。

**最终交付定义：不是“有一张看起来像表情包的图”，而是“同一个角色、16 种不同表达、16 个独立 PNG、16 个独立 GIF、自动验证、可解压 ZIP”。**
