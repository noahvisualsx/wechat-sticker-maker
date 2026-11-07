# 待 Codex 继续生成的真人表情包底图总清单（含新扩展分类与双人互动）

## 1. 整体完成度与待跑汇总

- **✅ 已完成入库（无需重复生成）**：
  - **单人风格底图**：已完成 **46 款风格 / 72 张真人静态贴纸**（通用 18/18 款 100% 完成、韩系 15/30 款、日系 6/30 款、中式 7/30 款）
  - **真动作 GIF**：已完成 **10 款**（4 张 `2×2` 风格动作表 + 6 张通用动作 GIF）
  - **真人梗图模板（60 / 60 款，100% 已全部完成！）**：刚刚已由本地 Python 复用现有真人四格底图将全部 **60 款梗图（含新增 `m39`–`m60` 22 款）** 100% 渲染入库至 `docs/gallery/memes/`，**0 Token 消耗，无需 Codex 生图**！

- **⏳ 待 Codex 继续生成的图片（已按优先级写入 JSON 队列）**：
  - **核心队列文件**：[`output/real-gallery-20261106/plan_remaining_after_limit.json`](plan_remaining_after_limit.json)（共 **184 张**：P1 必跑 **102 张** + P2 对比图 **82 张**）
  - **全量队列文件**：[`output/real-gallery-20261106/plan_codex_all_missing.json`](plan_codex_all_missing.json)（含 P3 全曲库扩展共 **408 张**）

| 优先级 (`priority`) | 类型说明 | 数量 | 目标目录 | 是否必跑 |
|---|---|---:|---|---|
| **`P1-representative`** | 108 款摄影风格中剩余未生成的独立表情底图（韩 15 + 日 24 + 中 23） | **62 张** | `output/real-gallery-20261106/raw/` | ⭐ **必跑 (P1)** |
| **`P1-animated-sheet`** | 4 大系列新增代表真动图 `2×2` 四格动作连拍图 | **8 张** | `output/real-gallery-20261106/sheets/` | ⭐ **必跑 (P1)** |
| **`P1-new-single-category`** | 新增 8 大单人分类代表图（电竞/追星/搞钱/干饭/考研/茶艺/发疯/萌宠，每类 2 张） | **16 张** | `output/real-gallery-20261106/raw/` | ⭐ **必跑 (P1)** |
| **`P1-duo-showcase`** | 6 大双人互动关系代表图（闺蜜 3 / 情侣 3 / 百合 4 / 双男主 2 / 冤家 2 / 亲子 2） | **16 张** | `output/real-gallery-20261106/raw/` | ⭐ **必跑 (P1)** |
| **`P2-hello-comparison`** | 82 款新增风格的统一 `01_hello`（你好）同动作光影对比图 | **82 张** | `output/real-gallery-20261106/raw/` | 选跑 (P2) |
| **`P3-single-remaining`** | 新增 8 大单人分类其余 72 款动作全量底图 (`133`–`220`) | **72 张** | `output/real-gallery-20261106/raw/` | 选跑 (P3) |
| **`P3-duo-remaining`** | 168 套双人互动其余 152 款动作全量底图 (`d01`–`d168`) | **152 张** | `output/real-gallery-20261106/raw/` | 选跑 (P3) |
| **合计（P1 核心必跑）** | **补齐全部 108 风格 + 22 单人分类展板 + 6 双人分类展板 + 18 真动图** | **102 张** | — | — |

---

## 2. 直接复制给 Codex 的续跑指令

```text
请读取 output/real-gallery-20261106/plan_remaining_after_limit.json：
1. 按顺序优先生成以下 P1 核心必跑任务（共 102 张），每张直接保存到该项的 target_file 路径（已存在的文件自动跳过）：
   - priority == 'P1-representative'（62 张：韩系 15 + 日系 24 + 中式 23 剩余风格静态底图）
   - priority == 'P1-animated-sheet'（8 张：2x2 四格真动作连拍底图）
   - priority == 'P1-new-single-category'（16 张：电竞/追星/搞钱/干饭/考研/茶艺/发疯/萌宠 8 大新分类代表图）
   - priority == 'P1-duo-showcase'（16 张：闺蜜/情侣/百合/双男主/欢喜冤家/亲子 6 大双人关系代表图）
2. 若额度充足，再继续生成 priority == 'P2-hello-comparison' 的 82 张统一问候对比图（或读取 plan_codex_all_missing.json 继续生成 P3）。
3. 铁律：全部使用同一真人参考照（白衬衫+黑V领针织马甲+酒红藏蓝斜纹领带+黑长卷发），100% 保留真实五官骨相与自然肤质，绝不卡通化，不在图片内画任何文字或气泡。
```

---

## 3. P1 必跑清单明细（共 102 张）

### 3.1 `P1-representative`：108 款风格剩余静态底图（62 张）

| # | 系列 | 风格 ID (`style`) | 风格名称 | 表情 ID | 台词 (`language`) | 保存路径 (`target_file`) |
|---:|---|---|---|---|---|---|
| 1 | 韩系 | `real-kr-hanok-sunlight` | **韩系北村韩屋暖阳** | `36_happy` | 开心 (`ko`) | `output/real-gallery-20261106/raw/real-kr-hanok-sunlight__36_happy.png` |
| 2 | 韩系 | `real-kr-winter-snow` | **韩系初雪围巾恋歌** | `37_heartbroken` | 心碎 (`ko`) | `output/real-gallery-20261106/raw/real-kr-winter-snow__37_heartbroken.png` |
| 3 | 韩系 | `real-kr-cherry-blossom` | **韩系汝矣岛樱花柔光** | `38_emo` | emo了 (`ko`) | `output/real-gallery-20261106/raw/real-kr-cherry-blossom__38_emo.png` |
| 4 | 韩系 | `real-kr-rainy-pocha` | **韩系雨夜布帐马车** | `39_jealous` | 酸了 (`ko`) | `output/real-gallery-20261106/raw/real-kr-rainy-pocha__39_jealous.png` |
| 5 | 韩系 | `real-kr-high-teen` | **韩系High-Teen复古校园** | `40_hmph` | 哼 (`ko`) | `output/real-gallery-20261106/raw/real-kr-high-teen__40_hmph.png` |
| 6 | 韩系 | `real-kr-y2k-metallic` | **韩系Y2K千禧银光** | `41_table_flip` | 掀桌 (`ko`) | `output/real-gallery-20261106/raw/real-kr-y2k-metallic__41_table_flip.png` |
| 7 | 韩系 | `real-kr-balletcore` | **韩系芭蕾风柔粉写真** | `42_wail` | 哇哇大哭 (`ko`) | `output/real-gallery-20261106/raw/real-kr-balletcore__42_wail.png` |
| 8 | 韩系 | `real-kr-clean-fit` | **韩系Clean-Fit极简白棚** | `43_so_sad` | 好难过 (`ko`) | `output/real-gallery-20261106/raw/real-kr-clean-fit__43_so_sad.png` |
| 9 | 韩系 | `real-kr-id-photo` | **韩系最美证件照精修** | `44_omg` | 我的天 (`ko`) | `output/real-gallery-20261106/raw/real-kr-id-photo__44_omg.png` |
| 10 | 韩系 | `real-kr-high-angle-booth` | **韩系俯拍高角度四格** | `45_question_marks` | 问号脸 (`ko`) | `output/real-gallery-20261106/raw/real-kr-high-angle-booth__45_question_marks.png` |
| 11 | 韩系 | `real-kr-bw-fourcut` | **韩系黑白胶片四格** | `46_cant_believe` | 不敢相信 (`ko`) | `output/real-gallery-20261106/raw/real-kr-bw-fourcut__46_cant_believe.png` |
| 12 | 韩系 | `real-kr-practice-mirror` | **韩系练习室对镜自拍** | `47_scared` | 好怕怕 (`ko`) | `output/real-gallery-20261106/raw/real-kr-practice-mirror__47_scared.png` |
| 13 | 韩系 | `real-kr-convenience-night` | **韩系深夜便利店霓虹** | `48_faint` | 晕倒 (`ko`) | `output/real-gallery-20261106/raw/real-kr-convenience-night__48_faint.png` |
| 14 | 韩系 | `real-kr-magazine-dazed` | **韩系先锋画报冷冽光** | `49_no` | 不要 (`ko`) | `output/real-gallery-20261106/raw/real-kr-magazine-dazed__49_no.png` |
| 15 | 韩系 | `real-kr-webtoon-real` | **韩系漫改主角神颜光** | `50_on_my_way` | 马上到 (`ko`) | `output/real-gallery-20261106/raw/real-kr-webtoon-real__50_on_my_way.png` |
| 16 | 日系 | `real-jp-rinko-pastel` | **日系川内伦子风淡彩** | `51_sure` | 好的呀 (`ja`) | `output/real-gallery-20261106/raw/real-jp-rinko-pastel__51_sure.png` |
| 17 | 日系 | `real-jp-hideaki-clean` | **日系滨田英明风清透** | `52_let_me_think` | 让我想想 (`ja`) | `output/real-gallery-20261106/raw/real-jp-hideaki-clean__52_let_me_think.png` |
| 18 | 日系 | `real-jp-moriyama-bw` | **日系森山大道粗颗粒黑白** | `53_got_it` | 懂了 (`ja`) | `output/real-gallery-20261106/raw/real-jp-moriyama-bw__53_got_it.png` |
| 19 | 日系 | `real-jp-ninagawa-vivid` | **日系蜷川实花浓郁花影** | `54_really` | 真的吗 (`ja`) | `output/real-gallery-20261106/raw/real-jp-ninagawa-vivid__54_really.png` |
| 20 | 日系 | `real-jp-shibuya-neon` | **日系涩谷十字路口霓虹** | `55_whatever` | 随便 (`ja`) | `output/real-gallery-20261106/raw/real-jp-shibuya-neon__55_whatever.png` |
| 21 | 日系 | `real-jp-shimokita-vintage` | **日系下北泽古着胶片** | `56_call_me` | 打给我 (`ja`) | `output/real-gallery-20261106/raw/real-jp-shimokita-vintage__56_call_me.png` |
| 22 | 日系 | `real-jp-daikanyama-morning` | **日系代官山晨光书店** | `58_youre_welcome` | 不客气 (`ja`) | `output/real-gallery-20261106/raw/real-jp-daikanyama-morning__58_youre_welcome.png` |
| 23 | 日系 | `real-jp-ginza-luxury` | **日系银座夜色流光** | `59_excuse_me` | 打扰了 (`ja`) | `output/real-gallery-20261106/raw/real-jp-ginza-luxury__59_excuse_me.png` |
| 24 | 日系 | `real-jp-kyoto-komorebi` | **日系京都木漏日和风** | `60_thanks_boss` | 谢谢老板 (`ja`) | `output/real-gallery-20261106/raw/real-jp-kyoto-komorebi__60_thanks_boss.png` |
| 25 | 日系 | `real-jp-hokkaido-snow` | **日系北海道情书雪景** | `61_good_work` | 辛苦了 (`ja`) | `output/real-gallery-20261106/raw/real-jp-hokkaido-snow__61_good_work.png` |
| 26 | 日系 | `real-jp-okinawa-sun` | **日系冲绳盛夏海盐** | `62_miss_you` | 想你了 (`ja`) | `output/real-gallery-20261106/raw/real-jp-okinawa-sun__62_miss_you.png` |
| 27 | 日系 | `real-jp-sakura-film` | **日系樱花季春光胶片** | `63_kiss` | 亲亲 (`ja`) | `output/real-gallery-20261106/raw/real-jp-sakura-film__63_kiss.png` |
| 28 | 日系 | `real-jp-autumn-icho` | **日系银杏大道秋日暖光** | `64_finger_heart` | 比心 (`ja`) | `output/real-gallery-20261106/raw/real-jp-autumn-icho__64_finger_heart.png` |
| 29 | 日系 | `real-jp-rainy-hydrangea` | **日系镰仓梅雨紫阳花** | `65_mwah` | 么么哒 (`ja`) | `output/real-gallery-20261106/raw/real-jp-rainy-hydrangea__65_mwah.png` |
| 30 | 日系 | `real-jp-onsen-steam` | **日系温泉旅馆暖雾** | `66_snuggle` | 贴贴 (`ja`) | `output/real-gallery-20261106/raw/real-jp-onsen-steam__66_snuggle.png` |
| 31 | 日系 | `real-jp-izakaya-warm` | **日系深夜食堂居酒屋** | `67_sending_love` | 送你爱心 (`ja`) | `output/real-gallery-20261106/raw/real-jp-izakaya-warm__67_sending_love.png` |
| 32 | 日系 | `real-jp-kissaten-retro` | **日系纯喫茶昭和咖啡** | `68_heart_flutter` | 心动 (`ja`) | `output/real-gallery-20261106/raw/real-jp-kissaten-retro__68_heart_flutter.png` |
| 33 | 日系 | `real-jp-school-rooftop` | **日系青春天台晴空** | `69_six_six_six` | 666 (`ja`) | `output/real-gallery-20261106/raw/real-jp-school-rooftop__69_six_six_six.png` |
| 34 | 日系 | `real-jp-matsuri-fireworks` | **日系夏日祭花火微光** | `71_like` | 点赞 (`ja`) | `output/real-gallery-20261106/raw/real-jp-matsuri-fireworks__71_like.png` |
| 35 | 日系 | `real-jp-nonno-magazine` | **日系甜美日杂画报** | `72_genius` | 天才 (`ja`) | `output/real-gallery-20261106/raw/real-jp-nonno-magazine__72_genius.png` |
| 36 | 日系 | `real-jp-popeye-cityboy` | **日系CityBoy街头画报** | `73_you_can_do_it` | 你可以的 (`ja`) | `output/real-gallery-20261106/raw/real-jp-popeye-cityboy__73_you_can_do_it.png` |
| 37 | 日系 | `real-jp-utsurundesu` | **日系写ルンです一次性胶片** | `74_respect` | 敬礼 (`ja`) | `output/real-gallery-20261106/raw/real-jp-utsurundesu__74_respect.png` |
| 38 | 日系 | `real-jp-drama-subtitle` | **日剧黄金档电影感剧照** | `75_awesome` | 太强了 (`ja`) | `output/real-gallery-20261106/raw/real-jp-drama-subtitle__75_awesome.png` |
| 39 | 日系 | `real-jp-variety-telop` | **日综夸张大字报斗图** | `76_chow_time` | 干饭人 (`ja`) | `output/real-gallery-20261106/raw/real-jp-variety-telop__76_chow_time.png` |
| 40 | 中式 | `real-cn-jiangnan-mist` | **中式江南烟雨清冷** | `77_hungry` | 饿了 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-jiangnan-mist__77_hungry.png` |
| 41 | 中式 | `real-cn-palace-redwall` | **中式红墙琉璃暖阳** | `78_coffee` | 续命咖啡 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-palace-redwall__78_coffee.png` |
| 42 | 中式 | `real-cn-song-minimal` | **中式宋韵极简留白** | `79_bath_time` | 洗澡去 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-song-minimal__79_bath_time.png` |
| 43 | 中式 | `real-cn-tang-splendor` | **中式盛唐鎏金夜宴** | `80_shopping` | 买买买 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-tang-splendor__80_shopping.png` |
| 44 | 中式 | `real-cn-dunhuang-sunset` | **中式敦煌大漠流沙** | `81_gaming` | 打游戏 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-dunhuang-sunset__81_gaming.png` |
| 45 | 中式 | `real-cn-ink-wash-light` | **中式水墨光影写真** | `82_workout` | 健身 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-ink-wash-light__82_workout.png` |
| 46 | 中式 | `real-cn-republican-velvet` | **中式民国复古画报** | `83_five_more_minutes` | 赖床 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-republican-velvet__83_five_more_minutes.png` |
| 47 | 中式 | `real-cn-shanghai-bund` | **中式外滩流光夜色** | `84_commuting` | 通勤中 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-shanghai-bund__84_commuting.png` |
| 48 | 中式 | `real-cn-hk-tvb-90s` | **港风90年代TVB剧照** | `85_meeting` | 开会中 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-hk-tvb-90s__85_meeting.png` |
| 49 | 中式 | `real-cn-hk-cyber-rain` | **港风旺角雨夜霓虹** | `86_overtime` | 加班 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-hk-cyber-rain__86_overtime.png` |
| 50 | 中式 | `real-cn-tw-nightmarket` | **台式夜市烟火霓虹** | `87_payday` | 发工资啦 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-tw-nightmarket__87_payday.png` |
| 51 | 中式 | `real-cn-chengdu-teahouse` | **中式成都竹椅茶馆** | `88_deadline` | 赶DDL (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-chengdu-teahouse__88_deadline.png` |
| 52 | 中式 | `real-cn-chongqing-cyber` | **中式重庆山城迷雾夜** | `90_studying` | 学习中 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-chongqing-cyber__90_studying.png` |
| 53 | 中式 | `real-cn-dali-sunshine` | **中式大理洱海慢生活** | `91_exam_week` | 考试周 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-dali-sunshine__91_exam_week.png` |
| 54 | 中式 | `real-cn-hulunbuir-wind` | **中式草原旷野清风** | `93_off_work` | 下班啦 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-hulunbuir-wind__93_off_work.png` |
| 55 | 中式 | `real-cn-80s-factory` | **中式80年代怀旧胶片** | `94_grind` | 打工人 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-80s-factory__94_grind.png` |
| 56 | 中式 | `real-cn-90s-calendar` | **中式90年代挂历画报** | `96_lie_flat` | 躺平 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-90s-calendar__96_lie_flat.png` |
| 57 | 中式 | `real-cn-cny-festive` | **中式新春贺岁红金** | `97_side_eye` | 斜眼 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-cny-festive__97_side_eye.png` |
| 58 | 中式 | `real-cn-wuxia-breeze` | **中式武侠清风江湖** | `99_thats_it` | 就这？ (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-wuxia-breeze__99_thats_it.png` |
| 59 | 中式 | `real-cn-tea-zen` | **中式围炉煮茶禅意** | `100_im_fine` | 我没事 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-tea-zen__100_im_fine.png` |
| 60 | 中式 | `real-cn-guochao-street` | **中式国潮街头撞色** | `101_broken` | 破防了 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-guochao-street__101_broken.png` |
| 61 | 中式 | `real-cn-work-survival` | **中式大厂打工人图鉴** | `102_popcorn` | 坐等后续 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-work-survival__102_popcorn.png` |
| 62 | 中式 | `real-cn-bazi-lucky` | **中式锦鲤好运玄学风** | `103_mic_drop` | 我说完了 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-bazi-lucky__103_mic_drop.png` |

### 3.2 `P1-animated-sheet`：真动图 `2×2` 四格动作连拍图（8 张）

| # | 系列 | 风格 ID (`style`) | 风格名称 | 动作表情 ID | 台词 (`language`) | 保存路径 (`target_file`) |
|---:|---|---|---|---|---|---|
| 1 | 通用 | `real-polaroid-instant` | **真人拍立得即时相纸** | `13_yay` | 好耶 (`en`) | `output/real-gallery-20261106/sheets/real-polaroid-instant__13_yay.png` |
| 2 | 通用 | `real-golden-hour` | **真人落日夕阳逆光** | `16_love` | 爱你 (`en`) | `output/real-gallery-20261106/sheets/real-golden-hour__16_love.png` |
| 3 | 韩系 | `real-kr-music-bank` | **韩系打歌舞台Ending妖精** | `09_acknowledged` | 收到 (`ko`) | `output/real-gallery-20261106/sheets/real-kr-music-bank__09_acknowledged.png` |
| 4 | 韩系 | `real-kr-high-angle-booth` | **韩系俯拍高角度四格** | `11_thanks` | 谢谢 (`ko`) | `output/real-gallery-20261106/sheets/real-kr-high-angle-booth__11_thanks.png` |
| 5 | 日系 | `real-jp-rinko-pastel` | **日系川内伦子风淡彩** | `70_clap` | 鼓掌 (`ja`) | `output/real-gallery-20261106/sheets/real-jp-rinko-pastel__70_clap.png` |
| 6 | 日系 | `real-jp-matsuri-fireworks` | **日系夏日祭花火微光** | `106_new_year` | 新年快乐 (`ja`) | `output/real-gallery-20261106/sheets/real-jp-matsuri-fireworks__106_new_year.png` |
| 7 | 中式 | `real-cn-jiangnan-mist` | **中式江南烟雨清冷** | `123_pat_pat` | 摸摸头 (`zh-CN`) | `output/real-gallery-20261106/sheets/real-cn-jiangnan-mist__123_pat_pat.png` |
| 8 | 中式 | `real-cn-shanghai-bund` | **中式外滩流光夜色** | `107_red_envelope` | 恭喜发财 (`zh-CN`) | `output/real-gallery-20261106/sheets/real-cn-shanghai-bund__107_red_envelope.png` |

### 3.3 `P1-new-single-category`：新增 8 大单人分类代表图（16 张，每类 2 张）

| # | 分类 (`category`) | 风格 ID (`style`) | 风格名称 | 表情 ID | 台词 (`language`) | 保存路径 (`target_file`) |
|---:|---|---|---|---|---|---|
| 1 | **开黑电竞** (`gaming`) | `real-cyber-neon` | 真人赛博霓虹夜景 | `133_game_log_on` | 上号开黑 (`en`) | `output/real-gallery-20261106/raw/real-cyber-neon__133_game_log_on.png` |
| 2 | **开黑电竞** (`gaming`) | `real-kr-idol-selfie` | 韩系爱豆自拍 | `142_game_loot_gold` | 出金了! (`ko`) | `output/real-gallery-20261106/raw/real-kr-idol-selfie__142_game_loot_gold.png` |
| 3 | **追星打Call** (`fandom`) | `real-kr-photocard` | 韩系爱豆小卡 | `144_fan_lightstick` | 为姐姐打CALL (`ko`) | `output/real-gallery-20261106/raw/real-kr-photocard__144_fan_lightstick.png` |
| 4 | **追星打Call** (`fandom`) | `real-kr-fansign-soft` | 韩系签售会奶油柔光 | `147_fan_ship_otp` | 嗑死我了 (`ko`) | `output/real-gallery-20261106/raw/real-kr-fansign-soft__147_fan_ship_otp.png` |
| 5 | **搞钱暴富** (`wealth`) | `real-cn-bazi-lucky` | 中式锦鲤好运玄学风 | `155_wealth_get_rich` | 接泼天富贵 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-bazi-lucky__155_wealth_get_rich.png` |
| 6 | **搞钱暴富** (`wealth`) | `real-cn-cny-festive` | 中式新春贺岁红金 | `162_wealth_payday_joy` | 发工资啦! (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-cny-festive__162_wealth_payday_joy.png` |
| 7 | **干饭奶茶** (`foodie`) | `real-kr-cafe-film` | 韩系咖啡馆胶片 | `166_food_boba_gulp` | 奶茶续命 (`ko`) | `output/real-gallery-20261106/raw/real-kr-cafe-film__166_food_boba_gulp.png` |
| 8 | **干饭奶茶** (`foodie`) | `real-cn-tw-nightmarket` | 台式夜市烟火霓虹 | `171_food_hotpot_call` | 走，吃火锅! (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-tw-nightmarket__171_food_hotpot_call.png` |
| 9 | **学生考研** (`campus`) | `real-jp-school-rooftop` | 日系青春天台晴空 | `178_camp_pass_exam` | 逢考必过! (`ja`) | `output/real-gallery-20261106/raw/real-jp-school-rooftop__178_camp_pass_exam.png` |
| 10 | **学生考研** (`campus`) | `real-american-yearbook` | 真人美式复古毕业年鉴 | `181_camp_ddl_rush` | 极限赶DDL (`en`) | `output/real-gallery-20261106/raw/real-american-yearbook__181_camp_ddl_rush.png` |
| 11 | **阴阳怪气/茶艺** (`sassy`) | `real-vogue-editorial` | 真人高定时尚杂志封面 | `188_sass_just_this` | 就这? (`en`) | `output/real-gallery-20261106/raw/real-vogue-editorial__188_sass_just_this.png` |
| 12 | **阴阳怪气/茶艺** (`sassy`) | `real-cn-chengdu-teahouse` | 中式成都竹椅茶馆 | `194_sass_sip_tea` | 品一口好茶 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-chengdu-teahouse__194_sass_sip_tea.png` |
| 13 | **发疯精神状态** (`mental`) | `real-work-emo` | 真人打工人纪实梗图 | `199_ment_stable_fine` | 精神状态美丽 (`en`) | `output/real-gallery-20261106/raw/real-work-emo__199_ment_stable_fine.png` |
| 14 | **发疯精神状态** (`mental`) | `real-high-contrast` | 真人黑白高反差梗图 | `200_ment_behaving_now` | 已老实求放过 (`en`) | `output/real-gallery-20261106/raw/real-high-contrast__200_ment_behaving_now.png` |
| 15 | **萌宠同框** (`pet_collab`) | `real-jp-airy` | 日系空气感清新 | `210_pet_hug_cat` | 吸猫续命 (`ja`) | `output/real-gallery-20261106/raw/real-jp-airy__210_pet_hug_cat.png` |
| 16 | **萌宠同框** (`pet_collab`) | `real-film-kodak-gold` | 真人柯达Gold200胶片 | `211_pet_puppy_wave` | 修勾打招呼 (`en`) | `output/real-gallery-20261106/raw/real-film-kodak-gold__211_pet_puppy_wave.png` |

### 3.4 `P1-duo-showcase`：6 大双人互动关系代表图（16 张）

| # | 关系分类 (`category`) | 风格 ID (`style`) | 互动名称 | 预设 ID | 台词 (`language`) | 保存路径 (`target_file`) |
|---:|---|---|---|---|---|---|
| 1 | `besties` | `real-purikura` | **闺蜜贴贴自拍** | `d01_bestie_cheek_selfie` | 贴贴！ (`ko`) | `output/real-gallery-20261106/raw/real-purikura__d01_bestie_cheek_selfie.png` |
| 2 | `besties` | `real-kr-cafe-film` | **干杯奶茶续命** | `d02_bestie_milk_tea_cheers` | 奶茶续命 (`ko`) | `output/real-gallery-20261106/raw/real-kr-cafe-film__d02_bestie_milk_tea_cheers.png` |
| 3 | `besties` | `real-kr-idol-selfie` | **暴风夸夸给跪** | `d03_bestie_hype_queen` | 绝美！ (`ko`) | `output/real-gallery-20261106/raw/real-kr-idol-selfie__d03_bestie_hype_queen.png` |
| 4 | `couple` | `real-kr-drama` | **宠溺摸摸头** | `d37_couple_head_pat` | 乖啦~ (`ko`) | `output/real-gallery-20261106/raw/real-kr-drama__d37_couple_head_pat.png` |
| 5 | `couple` | `real-golden-hour` | **温柔背后拥抱** | `d38_couple_back_hug` | 抱紧你 (`en`) | `output/real-gallery-20261106/raw/real-golden-hour__d38_couple_back_hug.png` |
| 6 | `couple` | `real-kr-winter-snow` | **额头相抵甜笑** | `d41_couple_forehead_touch` | 只看着你 (`ko`) | `output/real-gallery-20261106/raw/real-kr-winter-snow__d41_couple_forehead_touch.png` |
| 7 | `yuri` | `real-kr-drama` | **指尖轻挑下巴对视** | `d73_yuri_chin_lift_gaze` | 姐姐看着我 (`ko`) | `output/real-gallery-20261106/raw/real-kr-drama__d73_yuri_chin_lift_gaze.png` |
| 8 | `yuri` | `real-jp-sakura-film` | **双女主宿命感贴脸** | `d74_yuri_destiny_cheek_touch` | 命中注定 (`ja`) | `output/real-gallery-20261106/raw/real-jp-sakura-film__d74_yuri_destiny_cheek_touch.png` |
| 9 | `yuri` | `real-vogue-editorial` | **清冷姐姐壁咚甜妹** | `d75_yuri_cool_unnie_kabedon` | 心跳好快... (`en`) | `output/real-gallery-20261106/raw/real-vogue-editorial__d75_yuri_cool_unnie_kabedon.png` |
| 10 | `yuri` | `real-golden-hour` | **借肩浅眠发丝交织** | `d76_yuri_hair_intertwine_sleep` | 安静陪着你 (`en`) | `output/real-gallery-20261106/raw/real-golden-hour__d76_yuri_hair_intertwine_sleep.png` |
| 11 | `yaoi` | `real-blue-hour` | **指尖拽领带对视** | `d109_yaoi_tie_pull_gaze` | 哥哥别躲 (`en`) | `output/real-gallery-20261106/raw/real-blue-hour__d109_yaoi_tie_pull_gaze.png` |
| 12 | `yaoi` | `real-film-cinestill-800t` | **双男主西装背靠背** | `d110_yaoi_back_to_back_suit` | 并肩作战 (`en`) | `output/real-gallery-20261106/raw/real-film-cinestill-800t__d110_yaoi_back_to_back_suit.png` |
| 13 | `rivals` | `real-variety-meme` | **互相扯脸颊肉较劲** | `d129_rival_pinch_cheeks` | 互相伤害 (`zh-CN`) | `output/real-gallery-20261106/raw/real-variety-meme__d129_rival_pinch_cheeks.png` |
| 14 | `rivals` | `real-kr-variety` | **偷喝对方最后一口奶茶** | `d131_rival_steal_boba` | 最后一口归我! (`ko`) | `output/real-gallery-20261106/raw/real-kr-variety__d131_rival_steal_boba.png` |
| 15 | `family` | `real-film-kodak-gold` | **大小同款双手托腮歪头** | `d149_fam_copy_paste_pose` | 复制粘贴 (`en`) | `output/real-gallery-20261106/raw/real-film-kodak-gold__d149_fam_copy_paste_pose.png` |
| 16 | `family` | `real-cn-xhs-vibe` | **姐姐霸气把弟妹护在身后** | `d150_fam_sister_shield` | 有姐在别怕 (`zh-CN`) | `output/real-gallery-20261106/raw/real-cn-xhs-vibe__d150_fam_sister_shield.png` |

---

## 4. P2 选跑清单：`P2-hello-comparison` 统一 `01_hello` 问候对比图（82 张）

| # | 系列 | 风格 ID (`style`) | 风格名称 | 表情 ID | 语种 | 保存路径 (`target_file`) |
|---:|---|---|---|---|---|---|
| 1 | 通用 | `real-polaroid-instant` | **真人拍立得即时相纸** | `01_hello` | `en` | `output/real-gallery-20261106/raw/real-polaroid-instant__01_hello.png` |
| 2 | 通用 | `real-fisheye-y2k` | **真人千禧鱼眼大头贴** | `01_hello` | `en` | `output/real-gallery-20261106/raw/real-fisheye-y2k__01_hello.png` |
| 3 | 通用 | `real-paparazzi-flash` | **真人狗仔直闪抓拍** | `01_hello` | `en` | `output/real-gallery-20261106/raw/real-paparazzi-flash__01_hello.png` |
| 4 | 通用 | `real-golden-hour` | **真人落日夕阳逆光** | `01_hello` | `en` | `output/real-gallery-20261106/raw/real-golden-hour__01_hello.png` |
| 5 | 通用 | `real-blue-hour` | **真人蓝调时刻电影感** | `01_hello` | `en` | `output/real-gallery-20261106/raw/real-blue-hour__01_hello.png` |
| 6 | 通用 | `real-cyber-neon` | **真人赛博霓虹夜景** | `01_hello` | `en` | `output/real-gallery-20261106/raw/real-cyber-neon__01_hello.png` |
| 7 | 通用 | `real-film-kodak-gold` | **真人柯达Gold200胶片** | `01_hello` | `en` | `output/real-gallery-20261106/raw/real-film-kodak-gold__01_hello.png` |
| 8 | 通用 | `real-film-cinestill-800t` | **真人CineStill钨丝灯胶片** | `01_hello` | `en` | `output/real-gallery-20261106/raw/real-film-cinestill-800t__01_hello.png` |
| 9 | 通用 | `real-vogue-editorial` | **真人高定时尚杂志封面** | `01_hello` | `en` | `output/real-gallery-20261106/raw/real-vogue-editorial__01_hello.png` |
| 10 | 通用 | `real-french-effortless` | **真人法式慵懒午后写真** | `01_hello` | `en` | `output/real-gallery-20261106/raw/real-french-effortless__01_hello.png` |
| 11 | 通用 | `real-american-yearbook` | **真人美式复古毕业年鉴** | `01_hello` | `en` | `output/real-gallery-20261106/raw/real-american-yearbook__01_hello.png` |
| 12 | 通用 | `real-thermal-ir` | **真人潮流伪彩视觉** | `01_hello` | `en` | `output/real-gallery-20261106/raw/real-thermal-ir__01_hello.png` |
| 13 | 韩系 | `real-kr-music-bank` | **韩系打歌舞台Ending妖精** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-music-bank__01_hello.png` |
| 14 | 韩系 | `real-kr-fansign-soft` | **韩系签售会奶油柔光** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-fansign-soft__01_hello.png` |
| 15 | 韩系 | `real-kr-airport-snap` | **韩系仁川机场路透街拍** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-airport-snap__01_hello.png` |
| 16 | 韩系 | `real-kr-hongdae-street` | **韩系弘大街头潮拍** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-hongdae-street__01_hello.png` |
| 17 | 韩系 | `real-kr-seongsu-industrial` | **韩系圣水洞工业风写真** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-seongsu-industrial__01_hello.png` |
| 18 | 韩系 | `real-kr-hannam-oldmoney` | **韩系汉南洞千金氛围** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-hannam-oldmoney__01_hello.png` |
| 19 | 韩系 | `real-kr-apgujeong-glam` | **韩系狎鸥亭闪光夜拍** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-apgujeong-glam__01_hello.png` |
| 20 | 韩系 | `real-kr-jeju-breeze` | **韩系济州岛海风胶片** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-jeju-breeze__01_hello.png` |
| 21 | 韩系 | `real-kr-hanok-sunlight` | **韩系北村韩屋暖阳** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-hanok-sunlight__01_hello.png` |
| 22 | 韩系 | `real-kr-winter-snow` | **韩系初雪围巾恋歌** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-winter-snow__01_hello.png` |
| 23 | 韩系 | `real-kr-cherry-blossom` | **韩系汝矣岛樱花柔光** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-cherry-blossom__01_hello.png` |
| 24 | 韩系 | `real-kr-rainy-pocha` | **韩系雨夜布帐马车** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-rainy-pocha__01_hello.png` |
| 25 | 韩系 | `real-kr-high-teen` | **韩系High-Teen复古校园** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-high-teen__01_hello.png` |
| 26 | 韩系 | `real-kr-y2k-metallic` | **韩系Y2K千禧银光** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-y2k-metallic__01_hello.png` |
| 27 | 韩系 | `real-kr-balletcore` | **韩系芭蕾风柔粉写真** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-balletcore__01_hello.png` |
| 28 | 韩系 | `real-kr-clean-fit` | **韩系Clean-Fit极简白棚** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-clean-fit__01_hello.png` |
| 29 | 韩系 | `real-kr-id-photo` | **韩系最美证件照精修** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-id-photo__01_hello.png` |
| 30 | 韩系 | `real-kr-high-angle-booth` | **韩系俯拍高角度四格** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-high-angle-booth__01_hello.png` |
| 31 | 韩系 | `real-kr-bw-fourcut` | **韩系黑白胶片四格** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-bw-fourcut__01_hello.png` |
| 32 | 韩系 | `real-kr-practice-mirror` | **韩系练习室对镜自拍** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-practice-mirror__01_hello.png` |
| 33 | 韩系 | `real-kr-convenience-night` | **韩系深夜便利店霓虹** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-convenience-night__01_hello.png` |
| 34 | 韩系 | `real-kr-magazine-dazed` | **韩系先锋画报冷冽光** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-magazine-dazed__01_hello.png` |
| 35 | 韩系 | `real-kr-webtoon-real` | **韩系漫改主角神颜光** | `01_hello` | `ko` | `output/real-gallery-20261106/raw/real-kr-webtoon-real__01_hello.png` |
| 36 | 日系 | `real-jp-rinko-pastel` | **日系川内伦子风淡彩** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-rinko-pastel__01_hello.png` |
| 37 | 日系 | `real-jp-hideaki-clean` | **日系滨田英明风清透** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-hideaki-clean__01_hello.png` |
| 38 | 日系 | `real-jp-moriyama-bw` | **日系森山大道粗颗粒黑白** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-moriyama-bw__01_hello.png` |
| 39 | 日系 | `real-jp-ninagawa-vivid` | **日系蜷川实花浓郁花影** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-ninagawa-vivid__01_hello.png` |
| 40 | 日系 | `real-jp-shibuya-neon` | **日系涩谷十字路口霓虹** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-shibuya-neon__01_hello.png` |
| 41 | 日系 | `real-jp-shimokita-vintage` | **日系下北泽古着胶片** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-shimokita-vintage__01_hello.png` |
| 42 | 日系 | `real-jp-daikanyama-morning` | **日系代官山晨光书店** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-daikanyama-morning__01_hello.png` |
| 43 | 日系 | `real-jp-ginza-luxury` | **日系银座夜色流光** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-ginza-luxury__01_hello.png` |
| 44 | 日系 | `real-jp-kyoto-komorebi` | **日系京都木漏日和风** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-kyoto-komorebi__01_hello.png` |
| 45 | 日系 | `real-jp-hokkaido-snow` | **日系北海道情书雪景** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-hokkaido-snow__01_hello.png` |
| 46 | 日系 | `real-jp-okinawa-sun` | **日系冲绳盛夏海盐** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-okinawa-sun__01_hello.png` |
| 47 | 日系 | `real-jp-sakura-film` | **日系樱花季春光胶片** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-sakura-film__01_hello.png` |
| 48 | 日系 | `real-jp-autumn-icho` | **日系银杏大道秋日暖光** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-autumn-icho__01_hello.png` |
| 49 | 日系 | `real-jp-rainy-hydrangea` | **日系镰仓梅雨紫阳花** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-rainy-hydrangea__01_hello.png` |
| 50 | 日系 | `real-jp-onsen-steam` | **日系温泉旅馆暖雾** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-onsen-steam__01_hello.png` |
| 51 | 日系 | `real-jp-izakaya-warm` | **日系深夜食堂居酒屋** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-izakaya-warm__01_hello.png` |
| 52 | 日系 | `real-jp-kissaten-retro` | **日系纯喫茶昭和咖啡** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-kissaten-retro__01_hello.png` |
| 53 | 日系 | `real-jp-school-rooftop` | **日系青春天台晴空** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-school-rooftop__01_hello.png` |
| 54 | 日系 | `real-jp-matsuri-fireworks` | **日系夏日祭花火微光** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-matsuri-fireworks__01_hello.png` |
| 55 | 日系 | `real-jp-nonno-magazine` | **日系甜美日杂画报** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-nonno-magazine__01_hello.png` |
| 56 | 日系 | `real-jp-popeye-cityboy` | **日系CityBoy街头画报** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-popeye-cityboy__01_hello.png` |
| 57 | 日系 | `real-jp-utsurundesu` | **日系写ルンです一次性胶片** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-utsurundesu__01_hello.png` |
| 58 | 日系 | `real-jp-drama-subtitle` | **日剧黄金档电影感剧照** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-drama-subtitle__01_hello.png` |
| 59 | 日系 | `real-jp-variety-telop` | **日综夸张大字报斗图** | `01_hello` | `ja` | `output/real-gallery-20261106/raw/real-jp-variety-telop__01_hello.png` |
| 60 | 中式 | `real-cn-jiangnan-mist` | **中式江南烟雨清冷** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-jiangnan-mist__01_hello.png` |
| 61 | 中式 | `real-cn-palace-redwall` | **中式红墙琉璃暖阳** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-palace-redwall__01_hello.png` |
| 62 | 中式 | `real-cn-song-minimal` | **中式宋韵极简留白** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-song-minimal__01_hello.png` |
| 63 | 中式 | `real-cn-tang-splendor` | **中式盛唐鎏金夜宴** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-tang-splendor__01_hello.png` |
| 64 | 中式 | `real-cn-dunhuang-sunset` | **中式敦煌大漠流沙** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-dunhuang-sunset__01_hello.png` |
| 65 | 中式 | `real-cn-ink-wash-light` | **中式水墨光影写真** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-ink-wash-light__01_hello.png` |
| 66 | 中式 | `real-cn-republican-velvet` | **中式民国复古画报** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-republican-velvet__01_hello.png` |
| 67 | 中式 | `real-cn-shanghai-bund` | **中式外滩流光夜色** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-shanghai-bund__01_hello.png` |
| 68 | 中式 | `real-cn-hk-tvb-90s` | **港风90年代TVB剧照** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-hk-tvb-90s__01_hello.png` |
| 69 | 中式 | `real-cn-hk-cyber-rain` | **港风旺角雨夜霓虹** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-hk-cyber-rain__01_hello.png` |
| 70 | 中式 | `real-cn-tw-nightmarket` | **台式夜市烟火霓虹** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-tw-nightmarket__01_hello.png` |
| 71 | 中式 | `real-cn-chengdu-teahouse` | **中式成都竹椅茶馆** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-chengdu-teahouse__01_hello.png` |
| 72 | 中式 | `real-cn-chongqing-cyber` | **中式重庆山城迷雾夜** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-chongqing-cyber__01_hello.png` |
| 73 | 中式 | `real-cn-dali-sunshine` | **中式大理洱海慢生活** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-dali-sunshine__01_hello.png` |
| 74 | 中式 | `real-cn-hulunbuir-wind` | **中式草原旷野清风** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-hulunbuir-wind__01_hello.png` |
| 75 | 中式 | `real-cn-80s-factory` | **中式80年代怀旧胶片** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-80s-factory__01_hello.png` |
| 76 | 中式 | `real-cn-90s-calendar` | **中式90年代挂历画报** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-90s-calendar__01_hello.png` |
| 77 | 中式 | `real-cn-cny-festive` | **中式新春贺岁红金** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-cny-festive__01_hello.png` |
| 78 | 中式 | `real-cn-wuxia-breeze` | **中式武侠清风江湖** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-wuxia-breeze__01_hello.png` |
| 79 | 中式 | `real-cn-tea-zen` | **中式围炉煮茶禅意** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-tea-zen__01_hello.png` |
| 80 | 中式 | `real-cn-guochao-street` | **中式国潮街头撞色** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-guochao-street__01_hello.png` |
| 81 | 中式 | `real-cn-work-survival` | **中式大厂打工人图鉴** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-work-survival__01_hello.png` |
| 82 | 中式 | `real-cn-bazi-lucky` | **中式锦鲤好运玄学风** | `01_hello` | `zh-CN` | `output/real-gallery-20261106/raw/real-cn-bazi-lucky__01_hello.png` |
