# 梗图 / 抽象图模式（Meme & Abstract）

## 1. 用法
- 整套梗图包：`plan --pack-type memes [--meme-categories ai-meme,ban-warning] [--meme-templates claude,中国ip,封号]`
- 表情 + 梗图混合：`--pack-type mixed`（默认 1/4 为梗图，或按 `--meme-templates` 数量）
- 改梗图主文字：`--meme-text 封号=再BB一句试试`（可重复）
- 单张快速出图（用户照片 / Codex 生成的角色图）：
```bash
wechat-sticker-maker meme -t claude -i char.png -o out/thinking.gif            # 正在思考 + 头顶旋转思考图标
wechat-sticker-maker meme -t 中国ip -i char.png -o out/ip.gif                   # 检测到中国IP 禁止靠近
wechat-sticker-maker meme -t 封号 --sprite-sheet sheet_2x2.png -o out/ban.gif   # 再说话封你号 + 封号印章（角色有真实动作）
wechat-sticker-maker meme -t claude -i char.png -o out/a.gif --color "#D97757" --language ja
wechat-sticker-maker memes                                                     # 列出全部模板
```
- 单张图：输出 PNG；模板带动画叠加层（旋转图标、思考省略号、故障闪烁、印章砸下）时同时输出 GIF（仅叠加层动、角色不动）。要角色本身动起来，用 2×2 动作图或 2–8 张关键帧。

## 2. 模板（`references/meme-templates.json`，60 个，6 类）
`ai-meme` AI 梗（正在思考、已深度思考 999 秒、请求过于频繁、CPU 干烧了、我无法回答、大脑加载中、一本正经胡说八道、额度用完了、Token 余额不足、Prompt 写崩了、算力告急、系统升级中）·
`ban-warning` 封号/警告（中国IP禁止靠近、再说话封你号、账号已被封禁、已截图已举报、退退退、黄牌警告、防诈中心提醒、撤回也没用）·
`chat-ui` 聊天界面梗（禁言、对方正在输入、已读不回、老板拍了拍你、转账 ¥520.00、60 秒语音轰炸、你已被移出群聊、仅三天可见）·
`abstract` 抽象/发疯（震惊电子油炸、我悟了、我裂开了、精神状态良好、祖传包浆、404 脑子不在服务区、绷不住了、尊嘟假嘟、赛博木鱼功德+1、ENFP 快乐小狗、INTJ 冷漠脸、汗流浃背了、包的、CPU 给我干哪来了…）·
`classic-meme` 经典梗图（真人黑白高反差梗图、Impact 上下大字、顶部白条梗、专业团队、安全出口、纯爱战神）·
`work-life` 打工人（电量 1%、又改需求、禁止下班 403、续命中、社交电量 1%、带薪摸鱼许可证、精神赔偿账单、发薪日倒计时、周一综合症、已开启勿扰模式）。
别名：`claude`/`正在思考` → m01，`中国ip`/`禁止靠近` → m02，`封号`/`再说话封你号` → m03，`黑白梗图`/`真人黑白`/`熊猫头` → m19。

## 3. 规则
- **只做真人梗图**：所有梗图主角均保持用户参考照片的**真实真人五官与实拍皮肤质感**，绝不画成二次元动漫或卡通形象。
- 角色的真人表情与动作由 AI（Codex 自带作图）绘制；生图 Prompt 自动带 `[MEME LOOK]` 风格提示，并**禁止 AI 画字、图标、UI、印章、标志**——这些全部由 Python 叠加（22 种元素：思考图标、禁止标志、警戒胶带、印章、系统弹窗、聊天气泡、群通知、标签、进度条、故障大字、Impact 字、顶部白条、速度线、光芒、裂痕、冒烟、电量、正在输入、已读、星光、问号、静音）+ 8 种滤镜（电子油炸、故障、电子包浆、黑白、色相循环、暗角、高对比、色调分离）。
- 思考图标是通用的星芒图形，不复刻任何公司的官方 Logo；颜色可用 `--color` 自定义。
- 单一语言规则同样适用于梗图：所有元素文字都使用 `--language` 指定的语言。
- 梗图同样会导出到所有已选平台（见 `platform-export.md`）。
