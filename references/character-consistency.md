# Character Consistency Reference & Bible（真人专属身份锁定规范）

## 1. 核心目标
将用户单张真人参考照片提炼为不可漂移的真人身份特征（Real-Person Identity Lock），在生成静态和动态真人表情包及真人梗图时保持高度一致：
- **100% 真人写真还原**：用户一眼认出是本人真实照片级面孔，**绝不二次元化、绝不变成 2D 动漫/Q版插画/3D 玩偶/熊猫头**。
- **视觉系统一致性**：统一的微信经典模切白边（`die-cut-white-border`）、真实肤色与影棚光影、单人居中构图。
- **时序一致性**：动态 GIF 中真人五官、骨相、发型与服装稳定无抖动或换脸，下半身躯干锚定不动，仅手部动作、眨眼与表情自然变化。

## 2. 身份锚点（`character.json`）字段规范
- `character_id`: 规范化 ID（如 `human-portrait-a1b2c3d4`）。
- `source_sha256`: 源图像真实 SHA256 校验和。
- `subject_type`: 固定为 `"human-portrait"`（真人人像）。
- `identity_facts`: 基于可见事实提取的 4 项真人特征（如发型与发色、脸型骨相与眉眼鼻唇特征、真实肤色、眼镜/配饰与服装）。不臆造敏感属性。
- `locked_attributes`: 绝对禁止改变的属性列表（真人面部骨相与五官身份、真实摄影皮肤质感、发型与发际线、服装与配饰）。
- `allowed_variation`: 允许的变化（真人面部微表情与嘴型、自然眨眼/Wink 与视线方向、头部轻度歪斜、手势与手臂动作）。
- `render_style`:
  - `style_id`: 默认 `real-cutout`
  - `outline`: 模切白边（`die-cut-white-border`）
  - `palette`: 主色系 Hex 列表
  - `lighting`: 影棚人像光（`studio-portrait`）
  - `composition`: 单主体居中（`single-character-centered`）
- `master_anchor`: 生成的正面、自然表情真人标准锚点图路径。
