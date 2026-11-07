# 真人表情包图库 · 质量复检重做与待补生图清单

本文件记录 `docs/gallery/` 的实拍图库进度、**9 张质量复检未达标需重做的 P1 图片清单**，以及可选的 P2 双图对比清单。

---

## 1. 当前图库完成度总览

| 模块 | 预设总数 | 已实拍合成入库 | 状态 |
|---|---:|---:|---|
| **真人摄影风格 (`references/style-presets.json`)** | **108 款**（通用 18 / 韩系 30 / 日系 30 / 中式 30） | **108 款**（100% 覆盖） | 已全部合成入库（其中 4 张代表图待重做替换） |
| **真人双人互动 (`references/duo-presets.json`)** | **168 套**（闺蜜 36 / 情侣 36 / 百合 36 / 双男主 20 / 欢喜冤家 20 / 亲子 20） | **16 款**精选实拍样图（6 大分类全覆盖） | 已合成 `duo-showcase.jpg`（其中 3 张待重做替换） |
| **单人高频表情 (`references/expression-presets.json`)** | **22 类 · 220 款** | **22 类全覆盖**（`expressions-01..03.jpg`） | 已全部合成入库（其中 2 张待重做替换） |
| **真宠主角预设 (`references/pet-presets.json`)** | **4 类 · 40 款**（猫主子 10 / 快乐修勾 10 / 萌宠梗图 10 / 萌宠祝福 10） | 支持用户传入真宠照片生成 | 预设与 CLI (`pets`) 已就绪 |
| **真人动作 GIF (`docs/gallery/animations/`)** | — | **18 款**（12 张 2×2 关键帧精灵表 + 6 款基础动作） | 全部通过质检并入库 |
| **真人热梗模板 (`references/meme-templates.json`)** | **6 类 · 60 款** | **60 款**（100% 覆盖） | 全部通过质检并入库 |

---

## 2. 质量复检未达标 · 需重新生成的 9 张 P1 图片（最高优先级）

> 复检清单 JSON：`output/real-gallery-20261106/plan_redo_quality_fixes.json`  
> 缺陷对比看板：`output/real-gallery-20261106/qa_audit/defective_9_to_redo.jpg`

在刚生成的 102 张 P1 图片中，**93 张通过质检**，以下 **9 张**存在角色性别错误、眼部被画成 2D 卡通符号或构图截断问题，已修正 Prompt 并写入 `output/real-gallery-20261106/plan_redo_quality_fixes.json`：

| # | Key (`target_file`) | 所属模块 | 风格与表情 | 不达标原因（缺陷详情） | 修复方案（已写入 JSON Prompt） |
|---:|---|---|---|---|---|
| 1 | `real-blue-hour__d109_yaoi_tie_pull_gaze` | 双人互动 (`yaoi`) | 真人蓝调时刻 · 指尖拽领带对视 (`哥哥别躲`) | 分类为**双男主 (BL)**，原图误套用女性角色卡画成了一男一女且女生系领带 | 改为**两位高颜值真实现代青年男性（双男主）**半身同框，一人指尖轻拽另一人领带低眸对视 |
| 2 | `real-film-cinestill-800t__d110_yaoi_back_to_back_suit` | 双人互动 (`yaoi`) | CineStill 800T · 双男主西装背靠背 (`并肩作战`) | 分类为**双男主 (BL)**，原图误画成一男一女背靠背 | 改为**两位高颜值真实现代青年男性**身穿剪裁西装背靠背抱臂半身同框 |
| 3 | `real-vogue-editorial__d75_yuri_cool_unnie_kabedon` | 双人互动 (`yuri`) | 高定时尚杂志 · 清冷姐姐壁咚甜妹 (`心跳超标`) | 贴纸为透明背景无墙壁，高个姐姐左手高举撑着不存在的“空气墙”姿态怪异 | 改为高冷姐姐单手轻扶对方肩膀、两指轻托下巴近距离俯身对视，取消悬空撑墙手势 |
| 4 | `real-high-contrast__200_ment_behaving_now` | 新增单人分类 (`mental`) | 黑白高反差梗图 · 已老实求放过 (`已老实`) | 1) 应为黑白高反差影棚风但画成了彩色；2) 画成全身跪姿导致人脸过小 | 强制纯正黑白灰阶高反差影棚光 + **半身近景**双手合十乖巧低头认错 |
| 5 | `real-kr-convenience-night__48_faint` | 韩系代表图 (`kr`) | 韩系深夜便利店 · 晕倒 (`기절`) | 眼睛被画成 **2D 卡通蚊香圈 (`@_@`)** 且头顶有橙色涂鸦圈，违反 100% 真实人类五官规则 | 严禁卡通蚊香眼与涂鸦符号，保留 100% 真实人类眼睛（半闭微翻白眼/扶额眩晕神态） |
| 6 | `real-kr-high-angle-booth__45_question_marks` | 韩系代表图 (`kr`) | 韩系俯拍高角度四格 · 满头问号 (`???`) | AI 在背景自绘了 3 个大彩色问号，且左问号白边与袖子粘连无法通过连通域滤除 | 严禁 AI 在画面中绘制任何 `?` 问号符号（统一由 Python 叠加气泡） |
| 7 | `real-cn-tw-nightmarket__87_payday` | 中式代表图 (`cn`) | 台式夜市烟火霓虹 · 发工资啦 (`发工资啦!`) | 双眼眼球被**两枚黄色金币贴纸**覆盖，显得惊悚且违反真人五官锁 | 严禁金币挡眼，保留真实笑眼弯弯的眼睛，双手拿一沓红包扇面开心欢呼 |
| 8 | `real-cn-guochao-street__101_broken` | 中式代表图 (`cn`) | 中式国潮街头撞色 · 我裂开了 (`破防了`) | AI 把“裂开”具象化为脸颊和手背飞溅的棕色泥块/碎石，破坏干净人像肤质 | 保持面部与手部皮肤干净自然，用双手抱头崩溃震惊表情传达“我裂开了” |
| 9 | `real-jp-drama-subtitle__75_awesome` | 日系代表图 (`jp`) | 日剧黄金档剧照 · 太强了 (`すごすぎる`) | 画成趴在地上仰视且下半身在肩膀后方被生硬截断 | 改为标准正面半身人像，双手竖起大拇指 + 星星眼赞叹微笑 |

---

## 3. 一键重做这 9 张图片的指令

把下面这段话发给带有内置 `image_gen` 的 ChatGPT / Codex，即可直接覆盖原文件并完成修复：

```text
请读取 /Users/yoonseulah/weChatSticker/output/real-gallery-20261106/plan_redo_quality_fixes.json（共 9 项质量复检未达标图片）。
- 对于前 2 项双男主（d109、d110），不要使用女性参考照，直接按项内 prompt 生成两位高颜值真实现代青年男性（双男主）半身透明背景贴纸；
- 对于其余 7 项，使用 /Users/yoonseulah/weChatSticker/output/real-gallery-20261106/anchor.png 作为真人面部参考锚点，严格按项内修正后的 prompt 重新生成透明背景 PNG，并直接覆盖保存到每项的 target_file 路径。
生成完这 9 张后运行：
.venv/bin/python output/real-gallery-20261106/build_all_108.py && .venv/bin/python output/real-gallery-20261106/finish.py
```
