# Character Consistency Reference & Bible

## 1. 核心目标
将用户单张参考图提炼为不可漂移的身份特征（Identity Lock），在生成静态和动态表情包时保持一致：
- **身份一致性**：用户一眼认出是同一个角色/宠物/人像。
- **视觉系统一致性**：统一的描边、调色板（马卡龙/柔和色系）、光影、居中构图。
- **时序一致性**：动态 GIF 中五官与身体特征稳定无抖动或换脸。

## 2. 身份锚点（`character.json`）字段规范
- `character_id`: 规范化 ID（如 `cat-001`）。
- `source_sha256`: 源图像真实 SHA256 校验和。
- `subject_type`: 主体类型（`pet-cat`, `pet-dog`, `human-portrait`, `cartoon-character` 等）。
- `identity_facts`: 基于可见事实提取的关键特征（如“奶白色短毛猫”、“杏仁形大眼”、“粉色小鼻子”、“右耳尖浅灰毛”）。不臆造敏感属性。
- `locked_attributes`: 绝对禁止改变的属性列表（毛色、五官比例、耳朵形状等）。
- `allowed_variation`: 允许的变化（表情、手部动作、头部轻度倾斜）。
- `render_style`:
  - `outline`: 统一圆润描边（`round-uniform`）
  - `palette`: 主色系 Hex 列表
  - `lighting`: 柔和平光（`soft-flat`）
  - `composition`: 单主体居中（`single-character-centered`）
- `master_anchor`: 生成的正面、中性表情标准锚点图路径。

## 3. 锚点出图流水线
1. 对源图做 EXIF 旋转纠正与主体安全边距计算。
2. 提取 `identity_facts` 与风格锁定。
3. 调用图像模型生成一张中性正面锚点图（Master Anchor）。
4. 将 Master Anchor 和原照片同时作为后续表情编辑的参考底图。
