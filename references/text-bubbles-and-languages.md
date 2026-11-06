# 文案、文字气泡与多语言规范（Text, Speech Bubbles & Languages）

## 1. 三种文字版式（`text_layout`）
| 版式 | 效果 | 适用 |
|---|---|---|
| `caption` | 底部描边大字（经典表情包字幕） | 情绪类、状态类、梗图 |
| `bubble` | 角色旁的漫画对话气泡，尾巴指向角色头部 | 问候、回复、提问、喊话等“说出口”的台词 |
| `both` | 气泡里是台词 + 底部是标签字幕（如气泡“不干了！”+ 字幕“掀桌”） | 强戏剧性表情 |
| `none` | 无文字，纯表情 | 纯反应脸（偷看、斜眼、星星眼…） |

- 每个表情在 `references/expression-presets.json` 里自带推荐版式；`JobConfig.text_layout`/`--text-layout` 可全局覆盖（`auto` = 用每个表情自己的）。
- **文字一律由 Python 确定性叠加**，绝不让图像模型画字（AI 画字会错字/乱码，且无法多语言）。生图 Prompt 会自动要求模型为气泡/字幕**留白**（`prompts.composition_hint`）。
- 静态与动态都支持气泡；动态气泡可选动画 `bubble_animation`：`none`（默认，稳定）/ `pop`（弹出）/ `typewriter`（打字机逐字出现）/ `bob`（轻微浮动，仅气泡）。角色本身的动作永远由 AI 关键帧绘制。

## 2. 气泡形状（`bubble.shape`）
`round` 圆角对话框 · `oval` 椭圆 · `thought` 云朵思考泡（尾巴是小圆点）· `shout` 爆炸喊叫框（愤怒/震惊/兴奋）· `rect` 方形旁白框 · `heart` 爱心框（表白）· `whisper` 虚线悄悄话框（害羞/秘密）。
- 位置 `auto` 会放在角色**抬手/伸展方向的另一侧**上角，角色自动向反方向让位并缩放，尾巴指向头部。
- 颜色来自风格预设 `bubble`（缺省时：白底 + 风格字色描边；`shout` 淡黄、`heart` 淡粉、`whisper` 淡紫）。

## 3. 支持的语言
- **内置手写文案（132 个表情 × 5 种语言）**：`zh-CN` 简体中文、`zh-TW` 繁體中文、`en` English、`ja` 日本語、`ko` 한국어。文案是各地聊天习惯的口语（LINE スタンプ / 카톡 이모티콘 风格），不是机翻。
- **任意其他语言**（es/fr/de/it/pt/nl/pl/tr/vi/id/ms/fil/ru/uk/el/th/he/ar/fa/hi …）：
  1. `wechat-sticker-maker captions-template --language es -o captions_es.json`
  2. 由 Codex/ChatGPT 按每个表情的 `_source`（五语原文）与 `_mood` 写**地道、简短、口语化**的翻译填入 `caption`/`bubble`
  3. `plan --language es --captions-file captions_es.json`
  - 没有翻译时自动回退英文，并在 manifest 标记 `needs_translation: true`。
- **单一语言规则（强制）**：每张表情上的字幕、气泡、梗图元素文字**只能是同一种语言**（`--language`），绝不出现“你好 / Hi there!”这种中英混排。生成前会做预检（`planner.language_issues`）：
  - 缺少该语言文案（会导致回退成别的语言）→ 直接报错并提示用 `captions-template` 补翻译；
  - 文案里混入其他文字体系或外语单词 → 直接报错；
  - 聊天常用的短缩写（IP、CPU、OK、AI、BAN、404）不算混用。
  - 梗图元素文字也可在 captions 文件里翻译：`{"m02_china_ip_blocked": {"elements": {"1": {"text": {"es": "..."}}}}}`。
- **字体**：按字符所属文字体系逐段选字体（汉字按语言选简/繁/日/韩字形；平假名→日文字体；한글→韩文字体；泰文/西里尔/希腊/希伯来/天城文各自字体；Emoji 用彩色 Emoji 字体），同一行可混排 `OK啦👌`。`wechat-sticker-maker languages` 查看本机每种语言命中的字体。
- **换行规则**：中日文按字断行并遵守禁则（`。、！？」ー` 不出现在行首），句中英文单词不拆；英/韩/欧语按空格断词；泰文按字形簇；多行自动均衡长度并自动缩小字号。
- ⚠️ 阿拉伯语/波斯语/印地语需要 Pillow 带 libraqm 才能正确连写整形（`brew install libraqm` 后重装 Pillow）；`languages` 命令会提示。希伯来语与泰语在无 raqm 时已做兼容处理。

## 4. 文案长度建议
- 中/日/韩：≤ 6 字最佳，最多 10 字；英文等：≤ 14 字符最佳，最多 20。气泡可放 2–3 行，字幕最多 2 行（长英文 3 行）。
- 自定义文案文件格式（三种都可）：
```json
{"01_hello": "Hola"}
{"01_hello": {"es": "¡Hola!", "fr": "Coucou"}}
{"41_table_flip": {"caption": {"es": "¡Volcar mesa!"}, "bubble": {"es": "¡Renuncio!"}}}
```
