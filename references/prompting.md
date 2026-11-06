# Prompting Reference（真人表情包提示词规范）

## 结构化提示词分块设计

本项目**仅制作真人表情包与真人梗图**。为确保每一张静态贴纸与每一个动图关键帧都严格保持本人真实面孔且不变成二次元/卡通画风，提示词由 5 个结构块拼装而成：

1. `[IDENTITY LOCK]` & `[REAL_PERSON_HARD_LOCK]`
   - 强制锁定为**真人实拍写真级抠图（Photorealistic Real-Person Portrait Cutout）**。
   - 描述本人真实骨相、五官、肤质、发型与穿搭，严禁换脸或改动年龄。
2. `[STYLE LOCK]`
   - 根据所选真人 `StylePreset`（定义于 `references/style-presets.json`）注入真人摄影光影与贴纸白边规范。
   - 内置 26 种真人专属风格，分为通用 / 韩系 / 日系 / 中式四个系列（`StylePreset.region`），完整列表见 `README.md` 或 `wechat-sticker-maker styles --region <系列>`。风格只改变光影、色调与氛围，五官、脸型、眼睛大小、发型和穿搭始终与照片一致。
   - 单一真人主体居中，透明或纯白乾淨背景（由 Python 抠图并生成模切白边）。
3. `[ACTION]`
   - 对应预设中的特定真人神态与手势微动作（以及 `[MEME LOOK]` 梗图神态提示）。
4. `[COMPOSITION]`
   - 正方形画布，按 `text_layout` 预留底部字幕或顶部角落对话气泡/梗图弹窗空间，模型严禁在画面中自行画字或气泡。
5. `[NEGATIVE]`
   - 严格负面词约束：**严禁 2D 动漫、严禁二次元、严禁扁平插画、严禁 3D 玩偶化、严禁把人脸替换成熊猫头或动物头**、无水印、无拼贴网格线、无背景杂物、无模型自绘文本。
