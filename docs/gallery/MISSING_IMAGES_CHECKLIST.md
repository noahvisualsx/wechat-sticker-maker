# 待继续生成的真人表情包底图清单（ChatGPT / Codex 续跑任务单）

## 1. 当前已完成 vs 待补充总览

- **已完成底图（无需重跑）**：
  - 前 26 款真人风格的静态无字透明底图（每款 2 张，共 **52 张**，位于 `output/real-gallery-20261106/raw/`）
  - 10 款真人 4 帧动作 GIF 原画（位于 `output/real-gallery-20261106/sheets/` 与 `output/real-actions-v2-20261106/`）
  - 38 款真人梗图模板（位于 `docs/gallery/memes/`）
  - **多语言独立成套合成（已完成）**：已将韩系自动配全韩语（`ko`）、日系自动配全日语（`ja`）、通用自动配全英语（`en`）、中式自动配全中文（`zh-CN`），并生成了 `pack-zh-CN.jpg`、`pack-en.jpg`、`pack-ja.jpg`、`pack-ko.jpg` 四套 12 张完整单语种表情组。

- **待 ChatGPT 继续生成的底图（新增 82 款风格 + 8 张动作连拍图）**：
  - 任务文件已生成在：`output/real-gallery-20261106/plan_missing.json`（共 **172 个生图任务**，已写好完整 Prompt 与保存路径）
  - **优先级 P1（核心必跑 · 82 张不同表情代表作）**：为新增的 82 款真人风格各生成 1 张独立表情动作底图（同时覆盖另外 82 种不同表情姿态）。
  - **优先级 P1（真动图扩充 · 8 张 `2×2` 四格动作连拍图）**：为四大系列新增代表风格各生成 2 张 `2×2` 四格关键帧原画（共 8 张）。
  - **优先级 P2（可选对比图 · 82 张统一问候动作）**：为新增的 82 款风格各生成 1 张统一挥手问候（`01_hello`）底图，用于 108 款同动作光影横评。

---

## 2. 给 ChatGPT 的直接执行指令（复制即可）

```text
请读取 output/real-gallery-20261106/plan_missing.json：
1. 先按顺序生成 priority 为 'P1-representative' 的 82 张真人静态透明底图，以及 'P1-animated-sheet' 的 8 张 2x2 动作连拍图（保存到每项的 target_file 路径）。
2. 如果配额充足，继续生成 'P2-hello-comparison' 的 82 张 01_hello 对比底图。
3. 全部使用同一真人参考照，严格保持真实五官、骨相、肤质、黑色微卷长发与白衬衫黑马甲领带穿搭，绝不卡通化，不画文字和气泡（文字气泡由 build_gallery.py 按韩语/日语/英语/中文自动单语种合成）。
```

---

## 3. 待生成的 82 款新增真人风格明细（P1 + P2）

### 通用系列新增（12 款 · 合成语种：`en (全英语)`）

| # | 风格 ID (`style`) | 风格名称 | P1 独立表情底图 (`target_file`) | P2 统一问候底图 (`target_file`) |
|---|---|---|---|---|
| 1 | `real-polaroid-instant` | **真人拍立得即时相纸** | `raw/real-polaroid-instant__02_morning.png` (早安) | `raw/real-polaroid-instant__01_hello.png` (你好) |
| 2 | `real-fisheye-y2k` | **真人千禧鱼眼大头贴** | `raw/real-fisheye-y2k__03_goodnight.png` (晚安) | `raw/real-fisheye-y2k__01_hello.png` (你好) |
| 3 | `real-paparazzi-flash` | **真人狗仔直闪抓拍** | `raw/real-paparazzi-flash__08_speechless.png` (无语) | `raw/real-paparazzi-flash__01_hello.png` (你好) |
| 4 | `real-golden-hour` | **真人落日夕阳逆光** | `raw/real-golden-hour__12_hug.png` (抱抱) | `raw/real-golden-hour__01_hello.png` (你好) |
| 5 | `real-blue-hour` | **真人蓝调时刻电影感** | `raw/real-blue-hour__15_bye.png` (拜拜) | `raw/real-blue-hour__01_hello.png` (你好) |
| 6 | `real-cyber-neon` | **真人赛博霓虹夜景** | `raw/real-cyber-neon__17_are_you_there.png` (在吗) | `raw/real-cyber-neon__01_hello.png` (你好) |
| 7 | `real-film-kodak-gold` | **真人柯达Gold200胶片** | `raw/real-film-kodak-gold__19_ok.png` (OK) | `raw/real-film-kodak-gold__01_hello.png` (你好) |
| 8 | `real-film-cinestill-800t` | **真人CineStill钨丝灯胶片** | `raw/real-film-cinestill-800t__20_please.png` (求求) | `raw/real-film-cinestill-800t__01_hello.png` (你好) |
| 9 | `real-vogue-editorial` | **真人高定时尚杂志封面** | `raw/real-vogue-editorial__23_aggrieved.png` (委屈) | `raw/real-vogue-editorial__01_hello.png` (你好) |
| 10 | `real-french-effortless` | **真人法式慵懒午后写真** | `raw/real-french-effortless__25_long_time_no_see.png` (好久不见) | `raw/real-french-effortless__01_hello.png` (你好) |
| 11 | `real-american-yearbook` | **真人美式复古毕业年鉴** | `raw/real-american-yearbook__26_welcome.png` (欢迎欢迎) | `raw/real-american-yearbook__01_hello.png` (你好) |
| 12 | `real-thermal-ir` | **真人潮流伪彩视觉** | `raw/real-thermal-ir__27_see_you_tomorrow.png` (明天见) | `raw/real-thermal-ir__01_hello.png` (你好) |

### 韩系系列新增（23 款 · 合成语种：`ko (全韩语)`）

| # | 风格 ID (`style`) | 风格名称 | P1 独立表情底图 (`target_file`) | P2 统一问候底图 (`target_file`) |
|---|---|---|---|---|
| 1 | `real-kr-music-bank` | **韩系打歌舞台Ending妖精** | `raw/real-kr-music-bank__28_im_back.png` (我回来了) | `raw/real-kr-music-bank__01_hello.png` (你好) |
| 2 | `real-kr-fansign-soft` | **韩系签售会奶油柔光** | `raw/real-kr-fansign-soft__29_good_afternoon.png` (午安) | `raw/real-kr-fansign-soft__01_hello.png` (你好) |
| 3 | `real-kr-airport-snap` | **韩系仁川机场路透街拍** | `raw/real-kr-airport-snap__30_excited.png` (激动) | `raw/real-kr-airport-snap__01_hello.png` (你好) |
| 4 | `real-kr-hongdae-street` | **韩系弘大街头潮拍** | `raw/real-kr-hongdae-street__31_proud.png` (骄傲) | `raw/real-kr-hongdae-street__01_hello.png` (你好) |
| 5 | `real-kr-seongsu-industrial` | **韩系圣水洞工业风写真** | `raw/real-kr-seongsu-industrial__32_relieved.png` (松了口气) | `raw/real-kr-seongsu-industrial__01_hello.png` (你好) |
| 6 | `real-kr-hannam-oldmoney` | **韩系汉南洞千金氛围** | `raw/real-kr-hannam-oldmoney__33_cool.png` (酷) | `raw/real-kr-hannam-oldmoney__01_hello.png` (你好) |
| 7 | `real-kr-apgujeong-glam` | **韩系狎鸥亭闪光夜拍** | `raw/real-kr-apgujeong-glam__34_dance.png` (嗨起来) | `raw/real-kr-apgujeong-glam__01_hello.png` (你好) |
| 8 | `real-kr-jeju-breeze` | **韩系济州岛海风胶片** | `raw/real-kr-jeju-breeze__35_giggle.png` (嘿嘿) | `raw/real-kr-jeju-breeze__01_hello.png` (你好) |
| 9 | `real-kr-hanok-sunlight` | **韩系北村韩屋暖阳** | `raw/real-kr-hanok-sunlight__36_happy.png` (开心) | `raw/real-kr-hanok-sunlight__01_hello.png` (你好) |
| 10 | `real-kr-winter-snow` | **韩系初雪围巾恋歌** | `raw/real-kr-winter-snow__37_heartbroken.png` (心碎) | `raw/real-kr-winter-snow__01_hello.png` (你好) |
| 11 | `real-kr-cherry-blossom` | **韩系汝矣岛樱花柔光** | `raw/real-kr-cherry-blossom__38_emo.png` (emo了) | `raw/real-kr-cherry-blossom__01_hello.png` (你好) |
| 12 | `real-kr-rainy-pocha` | **韩系雨夜布帐马车** | `raw/real-kr-rainy-pocha__39_jealous.png` (酸了) | `raw/real-kr-rainy-pocha__01_hello.png` (你好) |
| 13 | `real-kr-high-teen` | **韩系High-Teen复古校园** | `raw/real-kr-high-teen__40_hmph.png` (哼) | `raw/real-kr-high-teen__01_hello.png` (你好) |
| 14 | `real-kr-y2k-metallic` | **韩系Y2K千禧银光** | `raw/real-kr-y2k-metallic__41_table_flip.png` (掀桌) | `raw/real-kr-y2k-metallic__01_hello.png` (你好) |
| 15 | `real-kr-balletcore` | **韩系芭蕾风柔粉写真** | `raw/real-kr-balletcore__42_wail.png` (哇哇大哭) | `raw/real-kr-balletcore__01_hello.png` (你好) |
| 16 | `real-kr-clean-fit` | **韩系Clean-Fit极简白棚** | `raw/real-kr-clean-fit__43_so_sad.png` (好难过) | `raw/real-kr-clean-fit__01_hello.png` (你好) |
| 17 | `real-kr-id-photo` | **韩系最美证件照精修** | `raw/real-kr-id-photo__44_omg.png` (我的天) | `raw/real-kr-id-photo__01_hello.png` (你好) |
| 18 | `real-kr-high-angle-booth` | **韩系俯拍高角度四格** | `raw/real-kr-high-angle-booth__45_question_marks.png` (问号脸) | `raw/real-kr-high-angle-booth__01_hello.png` (你好) |
| 19 | `real-kr-bw-fourcut` | **韩系黑白胶片四格** | `raw/real-kr-bw-fourcut__46_cant_believe.png` (不敢相信) | `raw/real-kr-bw-fourcut__01_hello.png` (你好) |
| 20 | `real-kr-practice-mirror` | **韩系练习室对镜自拍** | `raw/real-kr-practice-mirror__47_scared.png` (好怕怕) | `raw/real-kr-practice-mirror__01_hello.png` (你好) |
| 21 | `real-kr-convenience-night` | **韩系深夜便利店霓虹** | `raw/real-kr-convenience-night__48_faint.png` (晕倒) | `raw/real-kr-convenience-night__01_hello.png` (你好) |
| 22 | `real-kr-magazine-dazed` | **韩系先锋画报冷冽光** | `raw/real-kr-magazine-dazed__49_no.png` (不要) | `raw/real-kr-magazine-dazed__01_hello.png` (你好) |
| 23 | `real-kr-webtoon-real` | **韩系漫改主角神颜光** | `raw/real-kr-webtoon-real__50_on_my_way.png` (马上到) | `raw/real-kr-webtoon-real__01_hello.png` (你好) |

### 日系系列新增（24 款 · 合成语种：`ja (全日语)`）

| # | 风格 ID (`style`) | 风格名称 | P1 独立表情底图 (`target_file`) | P2 统一问候底图 (`target_file`) |
|---|---|---|---|---|
| 1 | `real-jp-rinko-pastel` | **日系川内伦子风淡彩** | `raw/real-jp-rinko-pastel__51_sure.png` (好的呀) | `raw/real-jp-rinko-pastel__01_hello.png` (你好) |
| 2 | `real-jp-hideaki-clean` | **日系滨田英明风清透** | `raw/real-jp-hideaki-clean__52_let_me_think.png` (让我想想) | `raw/real-jp-hideaki-clean__01_hello.png` (你好) |
| 3 | `real-jp-moriyama-bw` | **日系森山大道粗颗粒黑白** | `raw/real-jp-moriyama-bw__53_got_it.png` (懂了) | `raw/real-jp-moriyama-bw__01_hello.png` (你好) |
| 4 | `real-jp-ninagawa-vivid` | **日系蜷川实花浓郁花影** | `raw/real-jp-ninagawa-vivid__54_really.png` (真的吗) | `raw/real-jp-ninagawa-vivid__01_hello.png` (你好) |
| 5 | `real-jp-shibuya-neon` | **日系涩谷十字路口霓虹** | `raw/real-jp-shibuya-neon__55_whatever.png` (随便) | `raw/real-jp-shibuya-neon__01_hello.png` (你好) |
| 6 | `real-jp-shimokita-vintage` | **日系下北泽古着胶片** | `raw/real-jp-shimokita-vintage__56_call_me.png` (打给我) | `raw/real-jp-shimokita-vintage__01_hello.png` (你好) |
| 7 | `real-jp-daikanyama-morning` | **日系代官山晨光书店** | `raw/real-jp-daikanyama-morning__58_youre_welcome.png` (不客气) | `raw/real-jp-daikanyama-morning__01_hello.png` (你好) |
| 8 | `real-jp-ginza-luxury` | **日系银座夜色流光** | `raw/real-jp-ginza-luxury__59_excuse_me.png` (打扰了) | `raw/real-jp-ginza-luxury__01_hello.png` (你好) |
| 9 | `real-jp-kyoto-komorebi` | **日系京都木漏日和风** | `raw/real-jp-kyoto-komorebi__60_thanks_boss.png` (谢谢老板) | `raw/real-jp-kyoto-komorebi__01_hello.png` (你好) |
| 10 | `real-jp-hokkaido-snow` | **日系北海道情书雪景** | `raw/real-jp-hokkaido-snow__61_good_work.png` (辛苦了) | `raw/real-jp-hokkaido-snow__01_hello.png` (你好) |
| 11 | `real-jp-okinawa-sun` | **日系冲绳盛夏海盐** | `raw/real-jp-okinawa-sun__62_miss_you.png` (想你了) | `raw/real-jp-okinawa-sun__01_hello.png` (你好) |
| 12 | `real-jp-sakura-film` | **日系樱花季春光胶片** | `raw/real-jp-sakura-film__63_kiss.png` (亲亲) | `raw/real-jp-sakura-film__01_hello.png` (你好) |
| 13 | `real-jp-autumn-icho` | **日系银杏大道秋日暖光** | `raw/real-jp-autumn-icho__64_finger_heart.png` (比心) | `raw/real-jp-autumn-icho__01_hello.png` (你好) |
| 14 | `real-jp-rainy-hydrangea` | **日系镰仓梅雨紫阳花** | `raw/real-jp-rainy-hydrangea__65_mwah.png` (么么哒) | `raw/real-jp-rainy-hydrangea__01_hello.png` (你好) |
| 15 | `real-jp-onsen-steam` | **日系温泉旅馆暖雾** | `raw/real-jp-onsen-steam__66_snuggle.png` (贴贴) | `raw/real-jp-onsen-steam__01_hello.png` (你好) |
| 16 | `real-jp-izakaya-warm` | **日系深夜食堂居酒屋** | `raw/real-jp-izakaya-warm__67_sending_love.png` (送你爱心) | `raw/real-jp-izakaya-warm__01_hello.png` (你好) |
| 17 | `real-jp-kissaten-retro` | **日系纯喫茶昭和咖啡** | `raw/real-jp-kissaten-retro__68_heart_flutter.png` (心动) | `raw/real-jp-kissaten-retro__01_hello.png` (你好) |
| 18 | `real-jp-school-rooftop` | **日系青春天台晴空** | `raw/real-jp-school-rooftop__69_six_six_six.png` (666) | `raw/real-jp-school-rooftop__01_hello.png` (你好) |
| 19 | `real-jp-matsuri-fireworks` | **日系夏日祭花火微光** | `raw/real-jp-matsuri-fireworks__71_like.png` (点赞) | `raw/real-jp-matsuri-fireworks__01_hello.png` (你好) |
| 20 | `real-jp-nonno-magazine` | **日系甜美日杂画报** | `raw/real-jp-nonno-magazine__72_genius.png` (天才) | `raw/real-jp-nonno-magazine__01_hello.png` (你好) |
| 21 | `real-jp-popeye-cityboy` | **日系CityBoy街头画报** | `raw/real-jp-popeye-cityboy__73_you_can_do_it.png` (你可以的) | `raw/real-jp-popeye-cityboy__01_hello.png` (你好) |
| 22 | `real-jp-utsurundesu` | **日系写ルンです一次性胶片** | `raw/real-jp-utsurundesu__74_respect.png` (敬礼) | `raw/real-jp-utsurundesu__01_hello.png` (你好) |
| 23 | `real-jp-drama-subtitle` | **日剧黄金档电影感剧照** | `raw/real-jp-drama-subtitle__75_awesome.png` (太强了) | `raw/real-jp-drama-subtitle__01_hello.png` (你好) |
| 24 | `real-jp-variety-telop` | **日综夸张大字报斗图** | `raw/real-jp-variety-telop__76_chow_time.png` (干饭人) | `raw/real-jp-variety-telop__01_hello.png` (你好) |

### 中式系列新增（23 款 · 合成语种：`zh-CN (全中文)`）

| # | 风格 ID (`style`) | 风格名称 | P1 独立表情底图 (`target_file`) | P2 统一问候底图 (`target_file`) |
|---|---|---|---|---|
| 1 | `real-cn-jiangnan-mist` | **中式江南烟雨清冷** | `raw/real-cn-jiangnan-mist__77_hungry.png` (饿了) | `raw/real-cn-jiangnan-mist__01_hello.png` (你好) |
| 2 | `real-cn-palace-redwall` | **中式红墙琉璃暖阳** | `raw/real-cn-palace-redwall__78_coffee.png` (续命咖啡) | `raw/real-cn-palace-redwall__01_hello.png` (你好) |
| 3 | `real-cn-song-minimal` | **中式宋韵极简留白** | `raw/real-cn-song-minimal__79_bath_time.png` (洗澡去) | `raw/real-cn-song-minimal__01_hello.png` (你好) |
| 4 | `real-cn-tang-splendor` | **中式盛唐鎏金夜宴** | `raw/real-cn-tang-splendor__80_shopping.png` (买买买) | `raw/real-cn-tang-splendor__01_hello.png` (你好) |
| 5 | `real-cn-dunhuang-sunset` | **中式敦煌大漠流沙** | `raw/real-cn-dunhuang-sunset__81_gaming.png` (打游戏) | `raw/real-cn-dunhuang-sunset__01_hello.png` (你好) |
| 6 | `real-cn-ink-wash-light` | **中式水墨光影写真** | `raw/real-cn-ink-wash-light__82_workout.png` (健身) | `raw/real-cn-ink-wash-light__01_hello.png` (你好) |
| 7 | `real-cn-republican-velvet` | **中式民国复古画报** | `raw/real-cn-republican-velvet__83_five_more_minutes.png` (赖床) | `raw/real-cn-republican-velvet__01_hello.png` (你好) |
| 8 | `real-cn-shanghai-bund` | **中式外滩流光夜色** | `raw/real-cn-shanghai-bund__84_commuting.png` (通勤中) | `raw/real-cn-shanghai-bund__01_hello.png` (你好) |
| 9 | `real-cn-hk-tvb-90s` | **港风90年代TVB剧照** | `raw/real-cn-hk-tvb-90s__85_meeting.png` (开会中) | `raw/real-cn-hk-tvb-90s__01_hello.png` (你好) |
| 10 | `real-cn-hk-cyber-rain` | **港风旺角雨夜霓虹** | `raw/real-cn-hk-cyber-rain__86_overtime.png` (加班) | `raw/real-cn-hk-cyber-rain__01_hello.png` (你好) |
| 11 | `real-cn-tw-nightmarket` | **台式夜市烟火霓虹** | `raw/real-cn-tw-nightmarket__87_payday.png` (发工资啦) | `raw/real-cn-tw-nightmarket__01_hello.png` (你好) |
| 12 | `real-cn-chengdu-teahouse` | **中式成都竹椅茶馆** | `raw/real-cn-chengdu-teahouse__88_deadline.png` (赶DDL) | `raw/real-cn-chengdu-teahouse__01_hello.png` (你好) |
| 13 | `real-cn-chongqing-cyber` | **中式重庆山城迷雾夜** | `raw/real-cn-chongqing-cyber__90_studying.png` (学习中) | `raw/real-cn-chongqing-cyber__01_hello.png` (你好) |
| 14 | `real-cn-dali-sunshine` | **中式大理洱海慢生活** | `raw/real-cn-dali-sunshine__91_exam_week.png` (考试周) | `raw/real-cn-dali-sunshine__01_hello.png` (你好) |
| 15 | `real-cn-hulunbuir-wind` | **中式草原旷野清风** | `raw/real-cn-hulunbuir-wind__93_off_work.png` (下班啦) | `raw/real-cn-hulunbuir-wind__01_hello.png` (你好) |
| 16 | `real-cn-80s-factory` | **中式80年代怀旧胶片** | `raw/real-cn-80s-factory__94_grind.png` (打工人) | `raw/real-cn-80s-factory__01_hello.png` (你好) |
| 17 | `real-cn-90s-calendar` | **中式90年代挂历画报** | `raw/real-cn-90s-calendar__96_lie_flat.png` (躺平) | `raw/real-cn-90s-calendar__01_hello.png` (你好) |
| 18 | `real-cn-cny-festive` | **中式新春贺岁红金** | `raw/real-cn-cny-festive__97_side_eye.png` (斜眼) | `raw/real-cn-cny-festive__01_hello.png` (你好) |
| 19 | `real-cn-wuxia-breeze` | **中式武侠清风江湖** | `raw/real-cn-wuxia-breeze__99_thats_it.png` (就这？) | `raw/real-cn-wuxia-breeze__01_hello.png` (你好) |
| 20 | `real-cn-tea-zen` | **中式围炉煮茶禅意** | `raw/real-cn-tea-zen__100_im_fine.png` (我没事) | `raw/real-cn-tea-zen__01_hello.png` (你好) |
| 21 | `real-cn-guochao-street` | **中式国潮街头撞色** | `raw/real-cn-guochao-street__101_broken.png` (破防了) | `raw/real-cn-guochao-street__01_hello.png` (你好) |
| 22 | `real-cn-work-survival` | **中式大厂打工人图鉴** | `raw/real-cn-work-survival__102_popcorn.png` (坐等后续) | `raw/real-cn-work-survival__01_hello.png` (你好) |
| 23 | `real-cn-bazi-lucky` | **中式锦鲤好运玄学风** | `raw/real-cn-bazi-lucky__103_mic_drop.png` (我说完了) | `raw/real-cn-bazi-lucky__01_hello.png` (你好) |

## 4. 待生成的 8 张 `2×2` 真人动作连拍图（`P1-animated-sheet`）

| # | 所属系列 | 合成语种 | 风格 ID | 风格名称 | 动作表情 | 目标路径 (`target_file`) |
|---|---|---|---|---|---|---|
| 1 | 通用 | `en` | `real-polaroid-instant` | **真人拍立得即时相纸** | `13_yay` (好耶) | `output/real-gallery-20261106/sheets/real-polaroid-instant__13_yay.png` |
| 2 | 通用 | `en` | `real-golden-hour` | **真人落日夕阳逆光** | `16_love` (爱你) | `output/real-gallery-20261106/sheets/real-golden-hour__16_love.png` |
| 3 | 韩系 | `ko` | `real-kr-music-bank` | **韩系打歌舞台Ending妖精** | `09_acknowledged` (收到) | `output/real-gallery-20261106/sheets/real-kr-music-bank__09_acknowledged.png` |
| 4 | 韩系 | `ko` | `real-kr-high-angle-booth` | **韩系俯拍高角度四格** | `11_thanks` (谢谢) | `output/real-gallery-20261106/sheets/real-kr-high-angle-booth__11_thanks.png` |
| 5 | 日系 | `ja` | `real-jp-rinko-pastel` | **日系川内伦子风淡彩** | `70_clap` (鼓掌) | `output/real-gallery-20261106/sheets/real-jp-rinko-pastel__70_clap.png` |
| 6 | 日系 | `ja` | `real-jp-matsuri-fireworks` | **日系夏日祭花火微光** | `106_new_year` (新年快乐) | `output/real-gallery-20261106/sheets/real-jp-matsuri-fireworks__106_new_year.png` |
| 7 | 中式 | `zh-CN` | `real-cn-jiangnan-mist` | **中式江南烟雨清冷** | `123_pat_pat` (摸摸头) | `output/real-gallery-20261106/sheets/real-cn-jiangnan-mist__123_pat_pat.png` |
| 8 | 中式 | `zh-CN` | `real-cn-shanghai-bund` | **中式外滩流光夜色** | `107_red_envelope` (恭喜发财) | `output/real-gallery-20261106/sheets/real-cn-shanghai-bund__107_red_envelope.png` |

