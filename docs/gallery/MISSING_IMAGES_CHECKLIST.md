# 待继续生成的真人表情包底图清单（额度重置后续跑）

## 1. 最新进度汇总

- **已完成并入库合成（共 46 款风格 / 72 张真人静态贴纸 + 10 款真动图 + 38 款梗图）**：
  - **通用系列（18 / 18 款，100% 已全部完成！）**：已全部合成为 **100% 全英语** 贴纸并发布至 [`images/series-general.jpg`](images/series-general.jpg)。
  - **韩系系列（15 / 30 款，已完成一半！）**：前 7 款 + 本轮新增 8 款（打歌舞台 Ending 妖精、签售会柔光、仁川机场街拍、弘大潮拍、圣水洞工业风、汉南洞千金风、狎鸥亭闪光夜拍、济州岛海风）已全部合成为 **100% 全韩语** 贴纸并发布至 [`images/series-kr.jpg`](images/series-kr.jpg)。
  - **日系系列（6 / 30 款已完成）**：已合成为 **100% 全日语** 贴纸并发布至 [`images/series-jp.jpg`](images/series-jp.jpg)。
  - **中式系列（7 / 30 款已完成）**：已合成为 **100% 全中文** 贴纸并发布至 [`images/series-cn.jpg`](images/series-cn.jpg)。

- **剩余待生成任务（保存在 `output/real-gallery-20261106/plan_remaining_after_limit.json`）**：
  - **P1 必跑静态底图**：剩余 **62 张**（韩系剩余 15 张 + 日系 24 张 + 中式 23 张）
  - **P1 真动图 `2×2` 连拍图**：剩余 **8 张**
  - **P2 可选统一问候对比图（`01_hello`）**：剩余 **82 张**

---

## 2. 额度重置后给 ChatGPT 的续跑指令（直接复制）

```text
请读取 output/real-gallery-20261106/plan_remaining_after_limit.json：
1. 按顺序继续生成 priority 为 'P1-representative' 的剩余 62 张真人静态透明底图，以及 'P1-animated-sheet' 的 8 张 2x2 动作连拍图，直接保存到每项的 target_file 路径。
2. 全部使用同一真人参考照，严格保留真实五官、骨相、肤质、黑色微卷长发与白衬衫黑马甲领带穿搭，绝不卡通化，不画文字和气泡。
```

---

## 3. 剩余 62 款 P1 静态底图明细

### 韩系系列剩余（15 款 · 合成语种：`ko (全韩语)`）

| # | 风格 ID (`style`) | 风格名称 | P1 独立表情底图 (`target_file`) |
|---|---|---|---|
| 1 | `real-kr-hanok-sunlight` | **韩系北村韩屋暖阳** | `raw/real-kr-hanok-sunlight__36_happy.png` (开心) |
| 2 | `real-kr-winter-snow` | **韩系初雪围巾恋歌** | `raw/real-kr-winter-snow__37_heartbroken.png` (心碎) |
| 3 | `real-kr-cherry-blossom` | **韩系汝矣岛樱花柔光** | `raw/real-kr-cherry-blossom__38_emo.png` (emo了) |
| 4 | `real-kr-rainy-pocha` | **韩系雨夜布帐马车** | `raw/real-kr-rainy-pocha__39_jealous.png` (酸了) |
| 5 | `real-kr-high-teen` | **韩系High-Teen复古校园** | `raw/real-kr-high-teen__40_hmph.png` (哼) |
| 6 | `real-kr-y2k-metallic` | **韩系Y2K千禧银光** | `raw/real-kr-y2k-metallic__41_table_flip.png` (掀桌) |
| 7 | `real-kr-balletcore` | **韩系芭蕾风柔粉写真** | `raw/real-kr-balletcore__42_wail.png` (哇哇大哭) |
| 8 | `real-kr-clean-fit` | **韩系Clean-Fit极简白棚** | `raw/real-kr-clean-fit__43_so_sad.png` (好难过) |
| 9 | `real-kr-id-photo` | **韩系最美证件照精修** | `raw/real-kr-id-photo__44_omg.png` (我的天) |
| 10 | `real-kr-high-angle-booth` | **韩系俯拍高角度四格** | `raw/real-kr-high-angle-booth__45_question_marks.png` (问号脸) |
| 11 | `real-kr-bw-fourcut` | **韩系黑白胶片四格** | `raw/real-kr-bw-fourcut__46_cant_believe.png` (不敢相信) |
| 12 | `real-kr-practice-mirror` | **韩系练习室对镜自拍** | `raw/real-kr-practice-mirror__47_scared.png` (好怕怕) |
| 13 | `real-kr-convenience-night` | **韩系深夜便利店霓虹** | `raw/real-kr-convenience-night__48_faint.png` (晕倒) |
| 14 | `real-kr-magazine-dazed` | **韩系先锋画报冷冽光** | `raw/real-kr-magazine-dazed__49_no.png` (不要) |
| 15 | `real-kr-webtoon-real` | **韩系漫改主角神颜光** | `raw/real-kr-webtoon-real__50_on_my_way.png` (马上到) |

### 日系系列剩余（24 款 · 合成语种：`ja (全日语)`）

| # | 风格 ID (`style`) | 风格名称 | P1 独立表情底图 (`target_file`) |
|---|---|---|---|
| 1 | `real-jp-rinko-pastel` | **日系川内伦子风淡彩** | `raw/real-jp-rinko-pastel__51_sure.png` (好的呀) |
| 2 | `real-jp-hideaki-clean` | **日系滨田英明风清透** | `raw/real-jp-hideaki-clean__52_let_me_think.png` (让我想想) |
| 3 | `real-jp-moriyama-bw` | **日系森山大道粗颗粒黑白** | `raw/real-jp-moriyama-bw__53_got_it.png` (懂了) |
| 4 | `real-jp-ninagawa-vivid` | **日系蜷川实花浓郁花影** | `raw/real-jp-ninagawa-vivid__54_really.png` (真的吗) |
| 5 | `real-jp-shibuya-neon` | **日系涩谷十字路口霓虹** | `raw/real-jp-shibuya-neon__55_whatever.png` (随便) |
| 6 | `real-jp-shimokita-vintage` | **日系下北泽古着胶片** | `raw/real-jp-shimokita-vintage__56_call_me.png` (打给我) |
| 7 | `real-jp-daikanyama-morning` | **日系代官山晨光书店** | `raw/real-jp-daikanyama-morning__58_youre_welcome.png` (不客气) |
| 8 | `real-jp-ginza-luxury` | **日系银座夜色流光** | `raw/real-jp-ginza-luxury__59_excuse_me.png` (打扰了) |
| 9 | `real-jp-kyoto-komorebi` | **日系京都木漏日和风** | `raw/real-jp-kyoto-komorebi__60_thanks_boss.png` (谢谢老板) |
| 10 | `real-jp-hokkaido-snow` | **日系北海道情书雪景** | `raw/real-jp-hokkaido-snow__61_good_work.png` (辛苦了) |
| 11 | `real-jp-okinawa-sun` | **日系冲绳盛夏海盐** | `raw/real-jp-okinawa-sun__62_miss_you.png` (想你了) |
| 12 | `real-jp-sakura-film` | **日系樱花季春光胶片** | `raw/real-jp-sakura-film__63_kiss.png` (亲亲) |
| 13 | `real-jp-autumn-icho` | **日系银杏大道秋日暖光** | `raw/real-jp-autumn-icho__64_finger_heart.png` (比心) |
| 14 | `real-jp-rainy-hydrangea` | **日系镰仓梅雨紫阳花** | `raw/real-jp-rainy-hydrangea__65_mwah.png` (么么哒) |
| 15 | `real-jp-onsen-steam` | **日系温泉旅馆暖雾** | `raw/real-jp-onsen-steam__66_snuggle.png` (贴贴) |
| 16 | `real-jp-izakaya-warm` | **日系深夜食堂居酒屋** | `raw/real-jp-izakaya-warm__67_sending_love.png` (送你爱心) |
| 17 | `real-jp-kissaten-retro` | **日系纯喫茶昭和咖啡** | `raw/real-jp-kissaten-retro__68_heart_flutter.png` (心动) |
| 18 | `real-jp-school-rooftop` | **日系青春天台晴空** | `raw/real-jp-school-rooftop__69_six_six_six.png` (666) |
| 19 | `real-jp-matsuri-fireworks` | **日系夏日祭花火微光** | `raw/real-jp-matsuri-fireworks__71_like.png` (点赞) |
| 20 | `real-jp-nonno-magazine` | **日系甜美日杂画报** | `raw/real-jp-nonno-magazine__72_genius.png` (天才) |
| 21 | `real-jp-popeye-cityboy` | **日系CityBoy街头画报** | `raw/real-jp-popeye-cityboy__73_you_can_do_it.png` (你可以的) |
| 22 | `real-jp-utsurundesu` | **日系写ルンです一次性胶片** | `raw/real-jp-utsurundesu__74_respect.png` (敬礼) |
| 23 | `real-jp-drama-subtitle` | **日剧黄金档电影感剧照** | `raw/real-jp-drama-subtitle__75_awesome.png` (太强了) |
| 24 | `real-jp-variety-telop` | **日综夸张大字报斗图** | `raw/real-jp-variety-telop__76_chow_time.png` (干饭人) |

### 中式系列剩余（23 款 · 合成语种：`zh-CN (全中文)`）

| # | 风格 ID (`style`) | 风格名称 | P1 独立表情底图 (`target_file`) |
|---|---|---|---|
| 1 | `real-cn-jiangnan-mist` | **中式江南烟雨清冷** | `raw/real-cn-jiangnan-mist__77_hungry.png` (饿了) |
| 2 | `real-cn-palace-redwall` | **中式红墙琉璃暖阳** | `raw/real-cn-palace-redwall__78_coffee.png` (续命咖啡) |
| 3 | `real-cn-song-minimal` | **中式宋韵极简留白** | `raw/real-cn-song-minimal__79_bath_time.png` (洗澡去) |
| 4 | `real-cn-tang-splendor` | **中式盛唐鎏金夜宴** | `raw/real-cn-tang-splendor__80_shopping.png` (买买买) |
| 5 | `real-cn-dunhuang-sunset` | **中式敦煌大漠流沙** | `raw/real-cn-dunhuang-sunset__81_gaming.png` (打游戏) |
| 6 | `real-cn-ink-wash-light` | **中式水墨光影写真** | `raw/real-cn-ink-wash-light__82_workout.png` (健身) |
| 7 | `real-cn-republican-velvet` | **中式民国复古画报** | `raw/real-cn-republican-velvet__83_five_more_minutes.png` (赖床) |
| 8 | `real-cn-shanghai-bund` | **中式外滩流光夜色** | `raw/real-cn-shanghai-bund__84_commuting.png` (通勤中) |
| 9 | `real-cn-hk-tvb-90s` | **港风90年代TVB剧照** | `raw/real-cn-hk-tvb-90s__85_meeting.png` (开会中) |
| 10 | `real-cn-hk-cyber-rain` | **港风旺角雨夜霓虹** | `raw/real-cn-hk-cyber-rain__86_overtime.png` (加班) |
| 11 | `real-cn-tw-nightmarket` | **台式夜市烟火霓虹** | `raw/real-cn-tw-nightmarket__87_payday.png` (发工资啦) |
| 12 | `real-cn-chengdu-teahouse` | **中式成都竹椅茶馆** | `raw/real-cn-chengdu-teahouse__88_deadline.png` (赶DDL) |
| 13 | `real-cn-chongqing-cyber` | **中式重庆山城迷雾夜** | `raw/real-cn-chongqing-cyber__90_studying.png` (学习中) |
| 14 | `real-cn-dali-sunshine` | **中式大理洱海慢生活** | `raw/real-cn-dali-sunshine__91_exam_week.png` (考试周) |
| 15 | `real-cn-hulunbuir-wind` | **中式草原旷野清风** | `raw/real-cn-hulunbuir-wind__93_off_work.png` (下班啦) |
| 16 | `real-cn-80s-factory` | **中式80年代怀旧胶片** | `raw/real-cn-80s-factory__94_grind.png` (打工人) |
| 17 | `real-cn-90s-calendar` | **中式90年代挂历画报** | `raw/real-cn-90s-calendar__96_lie_flat.png` (躺平) |
| 18 | `real-cn-cny-festive` | **中式新春贺岁红金** | `raw/real-cn-cny-festive__97_side_eye.png` (斜眼) |
| 19 | `real-cn-wuxia-breeze` | **中式武侠清风江湖** | `raw/real-cn-wuxia-breeze__99_thats_it.png` (就这？) |
| 20 | `real-cn-tea-zen` | **中式围炉煮茶禅意** | `raw/real-cn-tea-zen__100_im_fine.png` (我没事) |
| 21 | `real-cn-guochao-street` | **中式国潮街头撞色** | `raw/real-cn-guochao-street__101_broken.png` (破防了) |
| 22 | `real-cn-work-survival` | **中式大厂打工人图鉴** | `raw/real-cn-work-survival__102_popcorn.png` (坐等后续) |
| 23 | `real-cn-bazi-lucky` | **中式锦鲤好运玄学风** | `raw/real-cn-bazi-lucky__103_mic_drop.png` (我说完了) |

