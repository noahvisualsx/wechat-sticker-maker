#!/usr/bin/env python3
"""Expand expression-presets.json (132 -> 220), duo-presets.json (108 -> 168), and meme-templates.json (38 -> 60)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "references"

# 1. 88 NEW SINGLE-PERSON EXPRESSIONS (8 new categories x 11 items = 88 -> total 220)
# Tuple: (id, cat, zh_cn, zh_tw, en, ko, ja, mood, layout, shape, pose)
NEW_EXPRS = [
    # gaming (开黑电竞 · 11)
    ("133_game_log_on", "gaming", "上号开黑", "上號開黑", "Log on!", "접속해!", "ログインして!", "gaming-excited", "bubble", "shout", "putting on gaming headset with one hand and beckoning excitedly toward the camera"),
    ("134_game_carry_me", "gaming", "求大佬带飞", "求大佬帶飛", "Carry me pls", "버스 태워줘", "キャリーして", "gaming-pleading", "bubble", "round", "clasping hands together with sparkling puppy eyes begging to be carried in a game"),
    ("135_game_easy_win", "gaming", "躺赢真爽", "躺贏真爽", "Easy win", "누워서 이김", "楽勝すぎ", "gaming-smug", "caption", "round", "leaning back lazily with hands behind head and a smug relaxed grin"),
    ("136_game_lag_460", "gaming", "网卡460了", "網卡460了", "Lagging!", "렉 걸렸어!", "ラグい!", "gaming-frustrated", "bubble", "thought", "staring blankly at phone held up in hand, tapping screen in frustration"),
    ("137_game_clutch_play", "gaming", "这波天秀", "這波天秀", "Godlike play", "방금 미쳤다", "今の神プレイ", "gaming-proud", "caption", "shout", "blowing imaginary smoke off fingertips with a cool confident smirk"),
    ("138_game_teammates", "gaming", "真带不动", "真帶不動", "Can't carry", "팀운 실화냐", "味方が重い", "gaming-exhausted", "bubble", "oval", "pinching the bridge of the nose with eyes closed in deep gaming despair"),
    ("139_game_one_more", "gaming", "最后亿把", "最後億把", "One last match", "진짜 막판!", "あと1戦だけ!", "gaming-determined", "bubble", "round", "holding up one index finger with dark eye circles and fiery determination"),
    ("140_game_gg_wp", "gaming", "打得不错", "打得不錯", "GGWP!", "수고했어!", "ナイスゲーム!", "gaming-respect", "caption", "round", "giving a clean respectful two-finger salute with a warm smile"),
    ("141_game_rage_quit", "gaming", "心态崩了", "心態崩了", "Tilted", "멘탈 터짐", "メンタル崩壊", "gaming-tilted", "bubble", "shout", "ruffling own hair with both hands and a dramatic meltdown expression"),
    ("142_game_loot_gold", "gaming", "出金了!", "出金了!", "SSR Drop!", "전설 떴다!", "SSR出た!", "gaming-ecstatic", "bubble", "shout", "gasping with both hands covering mouth and eyes wide at a golden phone glow"),
    ("143_game_afk_sleep", "gaming", "挂机睡觉", "掛機睡覺", "Going AFK", "잠수 탄다", "放置寝落ち", "gaming-sleepy", "caption", "thought", "resting chin on desk with headset sliding off one ear and eyelids drooping"),

    # fandom (追星打Call · 11)
    ("144_fan_lightstick", "fandom", "为姐姐打CALL", "為姐姐打CALL", "Stan forever!", "언니 사랑해!", "一生推す!", "fandom-cheering", "bubble", "heart", "waving a glowing concert lightstick with starry-eyed excitement"),
    ("145_fan_visual_shock", "fandom", "神颜暴击", "神顏暴擊", "Visual attack!", "미모 실화냐", "顔面国宝すぎ", "fandom-stunned", "caption", "heart", "clutching chest dramatically as if pierced through the heart by beauty"),
    ("146_fan_got_tickets", "fandom", "抢到票了!", "搶到票了!", "Got tickets!", "티켓팅 성공!", "神席当選!", "fandom-triumph", "bubble", "shout", "pumping both fists in the air with tears of pure joy"),
    ("147_fan_ship_otp", "fandom", "嗑死我了", "嗑死我了", "My OTP!", "이 주식 산다", "尊すぎて無理", "fandom-fangirl", "bubble", "heart", "hiding lower face behind both hands while peeking with a huge giddy grin"),
    ("148_fan_front_row", "fandom", "前排围观", "前排圍觀", "Front row!", "1열 직관 중", "最前列待機", "fandom-eager", "caption", "round", "leaning forward resting chin on palms with binoculars-like finger rings"),
    ("149_fan_screaming", "fandom", "啊啊啊太美了", "啊啊啊太美了", "Screaming!!", "미쳤다 진짜!", "ビジュ爆発!", "fandom-scream", "bubble", "shout", "cupping hands around mouth shouting praises with sparkling eyes"),
    ("150_fan_camera_snap", "fandom", "狂按快门", "狂按快門", "Taking 999 pics", "연사 찍는 중", "連写止まらん", "fandom-focused", "caption", "round", "holding up a camera lens at eye level with intense focused devotion"),
    ("151_fan_crying_beauty", "fandom", "美哭我了", "美哭我了", "So pretty I cry", "예뻐서 눈물나", "美しすぎて泣く", "fandom-moved", "bubble", "heart", "dabbing the corner of one eye with a tissue while smiling lovingly"),
    ("152_fan_banner_up", "fandom", "排面拉满", "排面拉滿", "Full support!", "응원 준비 끝!", "全力応援!", "fandom-proud", "caption", "round", "holding both hands above head as if displaying a cheering slogan banner"),
    ("153_fan_fancall_shy", "fandom", "签售会紧张", "簽售會緊張", "So nervous~", "영통 팬싸 떨려", "ヨントン緊張", "fandom-shy", "bubble", "heart", "fanning blushing cheeks with both hands before a video call"),
    ("154_fan_protect_idol", "fandom", "守护全世界最好的你", "守護全世界最好的你", "Must protect", "절대 지켜", "全力で守る", "fandom-protective", "bubble", "heart", "spreading both arms wide in a warm protective stance"),

    # wealth (搞钱暴富 · 11)
    ("155_wealth_get_rich", "wealth", "接泼天富贵", "接潑天富貴", "Manifesting wealth", "대박 기원!", "金運爆上がり!", "wealth-hopeful", "bubble", "round", "opening both palms upward toward the sky to catch falling fortune"),
    ("156_wealth_make_money", "wealth", "搞钱要紧", "搞錢要緊", "Hustle time", "돈 벌러 간다", "稼ぐぞ!", "wealth-focused", "caption", "round", "adjusting sunglasses with a sharp determined business smile"),
    ("157_wealth_red_packet", "wealth", "红包拿来", "紅包拿來", "Red packet pls", "세뱃돈 주세요", "お年玉ちょうだい", "wealth-playful", "bubble", "heart", "extending both hands palms-up with a cheeky expectant wink"),
    ("158_wealth_boss_generous", "wealth", "老板大气!", "老闆大氣!", "Boss is generous!", "사장님 최고!", "太っ腹!", "wealth-flattering", "bubble", "shout", "giving two enthusiastic thumbs-up with a deep appreciative bow"),
    ("159_wealth_one_cent", "wealth", "才抢一分钱", "才搶一分錢", "Only 1 cent?!", "겨우 10원?!", "たった1円?!", "wealth-shocked", "bubble", "thought", "squinting closely at thumb and index finger pinched tiny bit apart"),
    ("160_wealth_broke_dirt", "wealth", "钱包空空", "錢包空空", "Flat broke", "텅장 됐어...", "金欠すぎる", "wealth-broke", "caption", "thought", "turning empty pockets inside out with a pitiful pout"),
    ("161_wealth_v_me_50", "wealth", "V我50看看实力", "V我50看看實力", "Send $50", "치킨값 쏴봐", "500円送って", "wealth-teasing", "bubble", "round", "making a 5 and 0 gesture with both hands and raising one eyebrow"),
    ("162_wealth_payday_joy", "wealth", "发工资啦!", "發工資啦!", "Payday!!", "월급날이다!", "給料日キター!", "wealth-ecstatic", "bubble", "shout", "throwing arms up in celebration with a radiant carefree laugh"),
    ("163_wealth_sugar_friend", "wealth", "富婆抱抱我", "富婆抱抱我", "Spoil me pls", "부자 언니 안아줘", "貢いでほしい", "wealth-clingy", "bubble", "heart", "reaching arms out for a hug with shameless adorable puppy eyes"),
    ("164_wealth_lottery_pray", "wealth", "一夜暴富", "一夜暴富", "Instant millionaire", "로또 1등 기원", "一攫千金", "wealth-praying", "caption", "round", "pressing palms together in earnest prayer with eyes tightly shut"),
    ("165_wealth_bill_shock", "wealth", "账单刺客", "帳單刺客", "Bill shock!", "카드값 실화냐", "請求書エグい", "wealth-horrified", "bubble", "shout", "recoiling backward holding chest while staring at a long receipt"),

    # foodie (干饭奶茶 · 11)
    ("166_food_boba_gulp", "foodie", "奶茶续命", "奶茶續命", "Boba life", "버블티 수혈", "タピオカ最高", "foodie-bliss", "bubble", "heart", "happily sipping a large boba milk tea with cheeks puffed up"),
    ("167_food_late_snack", "foodie", "吃夜宵吗?", "吃宵夜嗎?", "Late-night snack?", "야식 먹을래?", "夜食いく?", "foodie-tempting", "bubble", "whisper", "leaning in conspiratorially with a mischievous foodie grin"),
    ("168_food_diet_tomorrow", "foodie", "吃饱再减肥", "吃飽再減肥", "Diet starts tmr", "다이어트는 내일부터", "明日から痩せる", "foodie-guilty", "caption", "round", "patting belly contentedly with a carefree shameless smile"),
    ("169_food_feed_me", "foodie", "饿饿饭饭", "餓餓飯飯", "Feed me pls", "배고파 밥 줘", "お腹すいた〜", "foodie-hungry", "bubble", "round", "holding chopsticks upright and looking at the viewer with hungry eyes"),
    ("170_food_so_yummy", "foodie", "香迷糊了", "香迷糊了", "So yummy!", "존맛탱!!", "うますぎる!", "foodie-delighted", "caption", "heart", "cupping one cheek in bliss with eyes curved into happy crescents"),
    ("171_food_hotpot_call", "foodie", "走，吃火锅!", "走，吃火鍋!", "Hotpot tonight!", "훠궈 먹으러 가자!", "鍋パしよう!", "foodie-energetic", "bubble", "shout", "waving one arm forward like leading a charge to a restaurant"),
    ("172_food_coffee_iv", "foodie", "冰美式续命", "冰美式續命", "Iced Americano IV", "아아 수혈 중", "カフェイン補給", "foodie-tired", "caption", "round", "holding an iced coffee cup against forehead with half-awake eyes"),
    ("173_food_too_spicy", "foodie", "斯哈斯哈好辣", "斯哈斯哈好辣", "So spicy!!", "습하습하 매워!", "辛すぎて無理!", "foodie-spicy", "bubble", "shout", "fanning open mouth with one hand with flushed cheeks"),
    ("174_food_full_coma", "foodie", "撑到走不动", "撐到走不動", "Food coma", "배불러서 못 걸어", "お腹いっぱい", "foodie-stuffed", "caption", "thought", "slouching back in chair rubbing stomach in a blissful food coma"),
    ("175_food_share_bite", "foodie", "分你一口", "分你一口", "Have a bite~", "한 입 줄게~", "一口あげる", "foodie-sweet", "bubble", "heart", "offering a spoonful forward toward the camera with a sweet smile"),
    ("176_food_cheers_drink", "foodie", "吨吨吨干杯", "噸噸噸乾杯", "Bottoms up!", "원샷 노브레이크!", "カンパーイ!", "foodie-festive", "caption", "round", "raising a glass high toward the camera with a bright toast smile"),

    # campus (学生考研 · 11)
    ("177_camp_cramming", "campus", "疯狂背书中", "瘋狂背書中", "Cramming hard", "벼락치기 중", "一夜漬け中", "campus-panic", "bubble", "thought", "flipping through a thick notebook rapidly with wide panicked eyes"),
    ("178_camp_pass_exam", "campus", "逢考必过!", "逢考必過!", "Ace the exam!", "무조건 합격!", "絶対合格!", "campus-confident", "bubble", "shout", "making an energetic double V-sign with a bright confident smile"),
    ("179_camp_8am_class", "campus", "早八人早八魂", "早八人早八魂", "8 AM zombie", "1교시 실화냐", "1限つらい", "campus-zombie", "caption", "thought", "resting chin on a stack of textbooks with sleepy half-closed eyes"),
    ("180_camp_thesis_pass", "campus", "论文一把过", "論文一把過", "Thesis approved!", "논문 통과!!", "卒論クリア!", "campus-relieved", "bubble", "shout", "hugging a laptop tightly with a huge relieved smile"),
    ("181_camp_ddl_rush", "campus", "极限赶DDL", "極限趕DDL", "Fighting DDL", "마감 직전 질주", "締切ヤバい", "campus-frantic", "caption", "shout", "typing furiously in mid-air with wind-blown hair"),
    ("182_camp_smart_glasses", "campus", "这题我会", "這題我會", "Easy question", "이 문제는 알지", "この問題は余裕", "campus-nerdy", "bubble", "round", "pushing up glasses on the bridge of the nose with a clever grin"),
    ("183_camp_vacation_free", "campus", "终于放假啦!", "終於放假啦!", "Vacation time!", "드디어 방학!", "やっと休みだ!", "campus-free", "bubble", "shout", "tossing a notebook aside and stretching arms wide in freedom"),
    ("184_camp_brain_empty", "campus", "大脑一片空白", "大腦一片空白", "Brain empty", "머리가 새하얘", "頭真っ白", "campus-blank", "caption", "thought", "staring into space with a dazed hollow smile holding a pen"),
    ("185_camp_roommate_call", "campus", "帮我带份饭", "幫我帶份飯", "Bring me food pls", "학식 포장 좀", "購買で買ってきて", "campus-lazy", "bubble", "heart", "peeking out from a cozy blanket with pleading eyes"),
    ("186_camp_library_study", "campus", "泡图书馆", "泡圖書館", "Studying quiet", "도서관 열공 모드", "図書館こもり中", "campus-quiet", "caption", "round", "holding a finger to lips in a quiet library shush while holding a book"),
    ("187_camp_high_score", "campus", "绩点拉满", "績點拉滿", "Straight A+!", "학점 만점!", "フル単確定!", "campus-proud", "bubble", "round", "forming an A+ shape with fingers and winking proudly"),

    # sassy (阴阳怪气/茶艺 · 11)
    ("188_sass_just_this", "sassy", "就这?", "就這?", "That's it?", "겨우 이거?", "たったそれだけ?", "sassy-unimpressed", "bubble", "round", "tilting chin up slightly with half-lidded unimpressed eyes and a tiny smirk"),
    ("189_sass_clap_slow", "sassy", "那你很棒哦", "那你很棒哦", "Good for you~", "참 잘했어요~", "すごいですね棒", "sassy-sarcastic", "bubble", "oval", "clapping hands slowly at chest level with a deadpan expression"),
    ("190_sass_eye_roll", "sassy", "给你个眼神", "給你個眼神", "Side-eyeing you", "눈빛으로 말함", "察してね", "sassy-sideeye", "caption", "round", "crossing arms and giving a sharp dramatic sideways glance"),
    ("191_sass_no_way", "sassy", "不会吧不会吧", "不會吧不會吧", "Surely not~", "설마 아니겠지~", "まさかね〜", "sassy-teasing", "bubble", "whisper", "covering mouth lightly with fingertips while eyes gleam with teasing amusement"),
    ("192_sass_so_scared", "sassy", "我好怕怕哦", "我好怕怕哦", "Sooo scared~", "어머 무서워라~", "こわ〜い(棒)", "sassy-mocking", "bubble", "heart", "patting chest in exaggerated fake fright with a playful smirk"),
    ("193_sass_polite_hehe", "sassy", "礼貌微笑", "禮貌微笑", "Polite smile", "비즈니스 미소", "愛想笑い", "sassy-fake-smile", "caption", "round", "curving lips into a textbook customer-service smile while eyes stay icy"),
    ("194_sass_sip_tea", "sassy", "品一口好茶", "品一口好茶", "Sipping tea", "조용히 구경 중", "お茶がうまい", "sassy-watching", "bubble", "round", "gracefully holding a teacup near lips while watching drama unfold"),
    ("195_sass_tui_tui", "sassy", "退!退!退!", "退!退!退!", "Back off!", "물러가라 훠이!", "悪霊退散!", "sassy-warding", "bubble", "shout", "thrusting one arm forward in a dramatic fencing-like warding pose"),
    ("196_sass_listen_nonsense", "sassy", "听君一席话", "聽君一席話", "Pure nonsense", "말이야 방구야", "何も言ってない", "sassy-speechless", "caption", "thought", "cupping one ear with a baffled amused expression"),
    ("197_sass_blame_me", "sassy", "怪我咯?", "怪我咯?", "My fault then?", "내 탓이라고?", "私のせい?", "sassy-innocent", "bubble", "round", "pointing at own nose with both index fingers and shrugging innocently"),
    ("198_sass_keep_acting", "sassy", "请开始你的表演", "請開始你的表演", "Go on, perform", "계속해 봐~", "どうぞ続けて", "sassy-audience", "bubble", "oval", "gesturing an open palm forward like inviting someone onto a stage"),

    # mental (发疯精神状态 · 11)
    ("199_ment_stable_fine", "mental", "精神状态美丽", "精神狀態美麗", "Totally sane", "정신줄 안녕함", "メンタル絶好調", "mental-chaotic", "bubble", "thought", "making double peace signs with a wildly unhinged cheerful smile"),
    ("200_ment_behaving_now", "mental", "已老实求放过", "已老實求放過", "I'll behave", "얌전히 있을게요", "おとなしくします", "mental-meek", "caption", "round", "sitting upright with hands neatly on knees and an overly obedient expression"),
    ("201_ment_destroy_all", "mental", "毁灭吧累了", "毀滅吧累了", "Done with everything", "다 귀찮아...", "もう全部どうでもいい", "mental-numb", "bubble", "thought", "tilting head back staring blankly at the ceiling in total exhaustion"),
    ("202_ment_ascended", "mental", "已升天勿扰", "已升天勿擾", "Soul left body", "영혼 가출 중", "召されました", "mental-peaceful", "caption", "thought", "closing eyes peacefully with hands crossed over chest like floating away"),
    ("203_ment_calm_crazy", "mental", "平静地发疯", "平靜地發瘋", "Calmly losing it", "차분하게 돌아버림", "静かに発狂中", "mental- eerie", "bubble", "whisper", "tilting head 30 degrees with a serene frozen smile"),
    ("204_ment_force_reboot", "mental", "强行开机中", "強行開機中", "Force rebooting", "강제 부팅 중", "強制起動中", "mental-lagging", "caption", "thought", "tapping own temple repeatedly to wake up the brain"),
    ("205_ment_scream_pillow", "mental", "无声尖叫", "無聲尖叫", "Silent scream", "음소거 비명", "無言の絶叫", "mental-scream", "bubble", "shout", "framing cheeks with both hands like Munch's Scream in comedic real-person style"),
    ("206_ment_no_sorrow", "mental", "大悲无泪", "大悲無淚", "Beyond tears", "웃프다 진짜", "泣く気力もない", "mental-hollow", "caption", "round", "staring straight at camera with a hollow Zen smile"),
    ("207_ment_social_battery_0", "mental", "社交电量0%", "社交電量0%", "Social battery 0%", "기가 다 빨림", "充電切れ0%", "mental-drained", "bubble", "thought", "slumping forward with head resting on arms and a drained pout"),
    ("208_ment_touch_grass", "mental", "需要吸点氧", "需要吸點氧", "Need fresh air", "산소 부족해", "酸素くれ", "mental-gasping", "caption", "round", "stretching neck upward taking a deep dramatic breath"),
    ("209_ment_dont_care", "mental", "随便吧都行", "隨便吧都行", "Whatever works", "아무렴 어때", "なんでもいいや", "mental-indifferent", "bubble", "oval", "waving one hand dismissively with a carefree half-smile"),

    # pet_collab (萌宠同框 · 11)
    ("210_pet_hug_cat", "pet_collab", "吸猫续命", "吸貓續命", "Cat therapy", "고양이 수혈", "猫吸い最高", "pet-loving", "bubble", "heart", "gently cradling a fluffy real cat in arms and pressing cheek softly against it"),
    ("211_pet_puppy_wave", "pet_collab", "修勾打招呼", "修勾打招呼", "Puppy says hi!", "멈머 인사해~", "わんこから挨拶", "pet-playful", "bubble", "round", "holding a cute real puppy and gently waving its front paw at the camera"),
    ("212_pet_cat_boss", "pet_collab", "猫主子驾到", "貓主子駕到", "Boss Cat here", "고양이 주인님", "猫様のお通り", "pet-proud", "caption", "round", "lifting a smug real cat up proudly like Simba while smiling"),
    ("213_pet_sync_tilt", "pet_collab", "同步歪头杀", "同步歪頭殺", "Twin head-tilt", "같이 갸우뚱", "シンクロ首かしげ", "pet-cute", "caption", "heart", "tilting head at the exact same angle as a cute puppy held beside the shoulder"),
    ("214_pet_meow_paws", "pet_collab", "喵呜贴贴", "喵嗚貼貼", "Meow cuddle~", "야옹 애교", "にゃんこポーズ", "pet-aegyo", "bubble", "heart", "curling both hands into cute cat paws beside cheeks while a kitten sits on shoulder"),
    ("215_pet_serve_treat", "pet_collab", "卑微铲屎官", "卑微鏟屎官", "Humble servant", "집사의 하루", "下僕の務め", "pet-humble", "caption", "round", "offering a cat treat stick respectfully to a cat in arms"),
    ("216_pet_dog_kisses", "pet_collab", "小狗热情贴贴", "小狗熱情貼貼", "Puppy kisses!", "강아지 뽀뽀 세례", "わんこ猛アタック", "pet-laughing", "bubble", "heart", "laughing brightly while a happy puppy licks the cheek"),
    ("217_pet_sleep_together", "pet_collab", "抱宠午睡", "抱寵午睡", "Nap with kitty", "냥이랑 낮잠", "猫とお昼寝", "pet-cozy", "caption", "thought", "resting chin on arms with eyes closed while a sleepy cat curls up beside"),
    ("218_pet_judge_stare", "pet_collab", "人和猫一起嫌弃", "人和貓一起嫌棄", "Both judging you", "둘 다 한심하게 봄", "猫と一緒にジト目", "pet-sassy", "bubble", "round", "giving a synchronized unimpressed side-eye together with the cat in arms"),
    ("219_pet_walk_time", "pet_collab", "出门遛弯啦", "出門遛彎啦", "Walkie time!", "산책 가자!", "お散歩いくよ!", "pet-energetic", "bubble", "shout", "holding up a cute puppy excitedly ready for a walk"),
    ("220_pet_goodnight_paw", "pet_collab", "和毛孩子晚安", "和毛孩子晚安", "Night from us~", "우리 둘 다 잘 자요", "ふたりでおやすみ", "pet-warm", "bubble", "heart", "waving goodnight softly while holding a sleepy puppy wrapped in a soft blanket"),
]


# 2. 60 NEW TWO-PERSON DUO PRESETS (3 new categories x 20 items = 60 -> total 168)
# Categories: yaoi (双男主/兄弟耽美 20), rivals (欢喜冤家/相爱相杀 20), family (亲子/姐弟萌娃 20)
NEW_DUOS = [
    # yaoi (双男主/兄弟耽美 · 20: d109 .. d128)
    ("d109_yaoi_tie_pull_gaze", "yaoi", "指尖拽领带对视", "哥哥别躲", "哥哥別躲", "Don't look away", "형, 피하지 마", "兄さん、逃げないで", "bubble", "heart", "Two real men in sharp tailored shirts: Person A gently pulling Person B's necktie closer, locking eyes with intense magnetic tension."),
    ("d110_yaoi_back_to_back_suit", "yaoi", "双男主西装背靠背", "并肩作战", "並肩作戰", "Watch my back", "등 뒤는 맡긴다", "背中は任せた", "caption", "round", "Two real men in dark suits standing back-to-back with cool composed expressions and cinematic rim lighting."),
    ("d111_yaoi_wall_whisper", "yaoi", "单手撑墙低声耳语", "听我的", "聽我的", "Listen to me", "내 말 들어", "俺の言う通りにして", "bubble", "whisper", "Person B leaning one hand against the wall beside Person A and whispering low near his ear."),
    ("d112_yaoi_shoulder_nap", "yaoi", "安静借肩小憩", "借个肩膀", "借個肩膀", "Rest on me", "어깨 빌려줄게", "肩を貸すよ", "caption", "thought", "Person A resting his head quietly on Person B's shoulder while Person B looks down with soft protective eyes."),
    ("d113_yaoi_collar_fix", "yaoi", "替对方整理衣领", "领口乱了", "領口亂了", "Hold still", "가만히 있어 봐", "じっとしてて", "bubble", "round", "Person B reaching out with both hands to neatly straighten Person A's shirt collar at close range."),
    ("d114_yaoi_black_umbrella", "yaoi", "雨夜共撑黑伞", "伞往你那边倾斜", "傘往你那邊傾斜", "Under one umbrella", "우산 같이 쓰자", "相合い傘しよう", "caption", "round", "Two real men standing close under a black umbrella in soft rain light, Person B tilting the umbrella toward Person A."),
    ("d115_yaoi_chin_touch_smirk", "yaoi", "拇指轻擦嘴角", "沾到东西了", "沾到東西了", "Got something there", "입가에 묻었어", "口元についてるよ", "bubble", "heart", "Person B brushing his thumb lightly across the corner of Person A's lip with a subtle teasing smirk."),
    ("d116_yaoi_forehead_temp", "yaoi", "贴额头试体温", "没发烧吧", "沒發燒吧", "Checking fever", "열나는 거 아니야?", "熱はないか?", "bubble", "round", "Person B pressing his forehead gently against Person A's forehead to check his temperature."),
    ("d117_yaoi_wrist_grab_stay", "yaoi", "反手扣住手腕挽留", "不准走", "不准走", "Stay right here", "가지 마", "行かないで", "bubble", "shout", "Person A turning slightly while Person B catches his wrist firmly with a deep emotional gaze."),
    ("d118_yaoi_coffee_clink", "yaoi", "冰美式碰杯相视一笑", "默契满分", "默契滿分", "Cheers, partner", "역시 내 파트너", "最高の相棒", "caption", "round", "Two real men clinking iced coffee cups together and sharing a warm knowing smile."),
    ("d119_yaoi_earphone_share", "yaoi", "一人一半耳机听歌", "同一首歌", "同一首歌", "Our song", "같은 노래 듣는 중", "同じ曲を聴こう", "bubble", "heart", "Two real men sitting close side-by-side sharing a pair of earbuds with relaxed smiles."),
    ("d120_yaoi_coat_drape", "yaoi", "披上宽大西装外套", "别着凉", "別著涼", "Take my coat", "감기 걸려, 걸쳐", "風邪ひくぞ", "bubble", "round", "Person B draping his tailored jacket over Person A's shoulders from behind."),
    ("d121_yaoi_glasses_remove", "yaoi", "伸手摘下对方眼镜", "看着我", "看著我", "Look at me", "나만 봐", "俺だけ見て", "bubble", "heart", "Person A gently removing Person B's wire-rimmed glasses while looking straight into his eyes."),
    ("d122_yaoi_fist_bump_promise", "yaoi", "双拳轻碰生死契约", "一言为定", "一言為定", "Deal is sealed", "약속한 거다", "約束だぞ", "caption", "round", "Two real men bumping fists at chest level with unwavering trust in their eyes."),
    ("d123_yaoi_head_ruffle", "yaoi", "揉乱对方头发宠溺笑", "拿你没辙", "拿你沒轍", "Can't say no to you", "너한테는 못 당해", "お前には敵わない", "bubble", "heart", "Person B ruffling Person A's hair affectionately while Person A smiles brightly."),
    ("d124_yaoi_scarf_pull", "yaoi", "冬日拉近围巾对视", "离近点暖和", "離近點暖和", "Come closer", "가까이 와, 추워", "もっと近くに来いよ", "bubble", "heart", "Two real men sharing a knit winter scarf, gently pulling each other closer."),
    ("d125_yaoi_gaming_couch", "yaoi", "并肩手柄打游戏较劲", "这局算你赢", "這局算你贏", "Letting you win", "이번엔 봐줬다", "今回は負けといてやる", "caption", "round", "Two real men holding game controllers shoulder-to-shoulder, leaning into each other playfully."),
    ("d126_yaoi_bandage_cheek", "yaoi", "轻贴创可贴心疼对视", "下次小心点", "下次小心點", "Be careful", "다치지 마", "無茶するなよ", "bubble", "round", "Person A carefully applying a small bandage to Person B's cheek with gentle concern."),
    ("d127_yaoi_rooftop_breeze", "yaoi", "天台晚风并肩远眺", "有你在就好", "有你在就好", "Glad you're here", "네가 있어서 다행이야", "お前がいてよかった", "caption", "round", "Two real men standing side-by-side in golden sunset breeze looking at each other warmly."),
    ("d128_yaoi_pinky_lock", "yaoi", "宿命感拉钩勾约定", "下辈子也一起", "下輩子也一起", "Forever bound", "다음 생에도 함께", "来世でも一緒に", "bubble", "heart", "Two real men locking pinky fingers in foreground focus with soft emotional smiles."),

    # rivals (欢喜冤家/相爱相杀 · 20: d129 .. d148)
    ("d129_rival_pinch_cheeks", "rivals", "互相扯脸颊肉较劲", "互相伤害", "互相傷害", "Mutual destruction!", "피차일반이거든!", "お互い様でしょ!", "caption", "shout", "Person A and Person B pinching and stretching each other's cheeks at the same time with funny competitive faces."),
    ("d130_rival_forehead_flick", "rivals", "石头剪刀布输了弹脑门", "愿赌服输!", "願賭服輸!", "Pay up!", "내기 졌으니 맞아라!", "罰ゲーム決定!", "bubble", "shout", "Person B aiming a playful finger-flick at Person A's forehead while Person A squints and covers forehead."),
    ("d131_rival_steal_boba", "rivals", "偷喝对方最后一口奶茶", "最后一口归我!", "最後一口歸我!", "Mine now!", "마지막 한 입은 내 거!", "最後の一口いただき!", "bubble", "round", "Person A sneaking a sip from Person B's boba straw while Person B gasps in betrayal."),
    ("d132_rival_back_sulking", "rivals", "背对背抱臂假装冷战", "哼，绝交三分钟", "哼，絕交三分鐘", "Hmph, ignoring you", "흥, 3분 동안 절교!", "ふん、3分間絶交!", "bubble", "thought", "Both people standing back-to-back with arms crossed pouting, yet secretly peeking back at each other."),
    ("d133_rival_headlock_tease", "rivals", "锁喉功揽脖子打闹", "服不服?!", "服不服?!", "Say uncle!", "항복해 안 해?!", "参ったか!", "bubble", "shout", "Person B playfully wrapping an arm around Person A's neck in a friendly headlock while both laugh."),
    ("d134_rival_nag_cover_ears", "rivals", "一个碎碎念一个捂耳朵", "不听不听王八念经", "不聽不聽王八念經", "Blah blah can't hear", "안 들려 안 들려~", "聞こえませーん!", "bubble", "round", "Person B wagging a finger lecturing while Person A covers both ears making a cheeky face."),
    ("d135_rival_blame_each_other", "rivals", "同时指对方甩锅", "都怪你!", "都怪你!", "All your fault!", "다 너 때문이야!", "全部あんたのせい!", "bubble", "shout", "Person A and Person B pointing accusingly at each other at the exact same time."),
    ("d136_rival_fake_punch", "rivals", "假装挥小拳拳吓唬", "信不信揍你", "信不信揍你", "Wanna fight?!", "한 대 맞을래?!", "パンチするぞ!", "bubble", "shout", "Person A raising a playful fist while Person B exaggeratedly cowers with a teasing grin."),
    ("d137_rival_peace_horns", "rivals", "合照偷偷在对方头上比兔耳", "暗中捣乱", "暗中搗亂", "Photobomb!", "몰래 장난치기", "後ろでいたずら", "caption", "round", "Person A posing nicely while Person B sneaks bunny-ear fingers behind Person A's head."),
    ("d138_rival_push_away_face", "rivals", "单手推开凑近的大脸", "莫挨老子", "莫挨老子", "Personal space pls", "저리 가 질척대지 마", "近いってば!", "bubble", "round", "Person A trying to lean in for a hug while Person B playfully pushes Person A's face back with one palm."),
    ("d139_rival_smug_vs_mad", "rivals", "一个得瑟挑眉一个咬牙切齿", "气死你略略略", "氣死你略略略", "Stay mad~", "약오르지 메롱~", "悔しいでしょ〜", "bubble", "round", "Person A sticking tongue out smugly while Person B puffs cheeks in comical rage."),
    ("d140_rival_tug_of_snack", "rivals", "争抢同一包薯片", "放手是我的!", "放手是我的!", "Hands off my snack!", "내 과자 손 떼!", "私のお菓子返して!", "bubble", "shout", "Both people pulling on opposite ends of a snack bag refusing to let go."),
    ("d141_rival_eye_squint_duel", "rivals", "鼻子贴鼻子瞪眼比赛", "谁先眨眼谁请客", "誰先眨眼誰請客", "Staring contest!", "눈 먼저 깜빡이면 쏘기!", "まばたきしたら奢り!", "bubble", "round", "Two real people leaning nose-to-nose in an intense funny staring contest."),
    ("d142_rival_bribe_milk_tea", "rivals", "递上一杯奶茶求原谅", "大人不记小人过", "大人不記小人過", "Peace offering~", "이거 먹고 풀어~", "これで許して〜", "bubble", "heart", "Person B offering a milk tea with an apologetic grin while Person A looks away trying not to smile."),
    ("d143_rival_step_on_shadow", "rivals", "凑在一起看对方黑历史照片", "公开处刑!", "公開處刑!", "Blackmail material!", "흑역사 박제 완료!", "黒歴史発見!", "bubble", "shout", "Person B holding up a phone laughing while Person A reaches desperately to grab it."),
    ("d144_rival_sync_facepalm", "rivals", "两人同时扶额无语", "没眼看", "沒眼看", "Double facepalm", "둘 다 할 말 잃음", "同時に頭抱える", "caption", "thought", "Both Person A and Person B doing a synchronized facepalm with identical speechless expressions."),
    ("d145_rival_poke_cheek_annoy", "rivals", "疯狂戳对方脸颊肉", "戳戳戳理我!", "戳戳戳理我!", "Poke poke!", "콕콕 나 좀 봐줘!", "ツンツン構って!", "bubble", "round", "Person A repeatedly poking Person B's cheek with both index fingers while Person B sighs."),
    ("d146_rival_fake_cry_tattle", "rivals", "一个假哭告状一个慌张捂嘴", "别嚎了祖宗!", "別嚎了祖宗!", "Shh don't snitch!", "야 울지 마 조용히 해!", "泣かないでよ〜!", "bubble", "shout", "Person A pretending to wail dramatically while Person B panics trying to cover Person A's mouth."),
    ("d147_rival_high_five_miss", "rivals", "假装击掌突然收回手", "溜了溜了", "溜了溜了", "Too slow~", "속았지롱~", "残念でした〜", "bubble", "round", "Person A pulling hand back to smooth hair right as Person B goes for a high-five."),
    ("d148_rival_make_up_hug", "rivals", "吵完架秒和好抱抱", "还是你最好", "還是你最好", "Still best friends", "그래도 네가 최고야", "やっぱり仲良し", "bubble", "heart", "Both people hugging warmly and laughing right after a silly argument."),

    # family (亲子/姐弟兄妹萌娃 · 20: d149 .. d168)
    ("d149_fam_copy_paste_pose", "family", "大小同款双手托腮歪头", "复制粘贴", "複製粘貼", "Copy & paste", "붕어빵 가족", "そっくりそのまま", "caption", "heart", "Both people resting chins in their palms at the exact same angle with matching bright smiles."),
    ("d150_fam_sister_shield", "family", "姐姐霸气把弟妹护在身后", "有姐在别怕", "有姐在別怕", "Big sis got you", "누나만 믿어!", "お姉ちゃんに任せて!", "bubble", "shout", "Person A standing protectively in front while Person B peeks out from behind her shoulder."),
    ("d151_fam_pinch_soft_cheek", "family", "宠溺轻捏软乎乎脸蛋", "我们家乖宝", "我們家乖寶", "Cutie pie", "우리 집 귀요미", "うちの可愛い子", "bubble", "heart", "Person A gently pinching Person B's soft cheek with a warm doting smile."),
    ("d152_fam_red_envelope_pat", "family", "发红包摸摸头祝福", "岁岁平安长大", "歲歲平安長大", "Grow up happy!", "건강하게만 자라다오", "すくすく育ってね", "bubble", "heart", "Person A handing a festive red packet to Person B while patting their head warmly."),
    ("d153_fam_piggyback_joy", "family", "背着弟妹欢快比耶", "出发咯!", "出發咯!", "Off we go!", "출발한다 꽉 잡아!", "しゅっぱーつ!", "bubble", "shout", "Person B giving Person A a cheerful piggyback ride while both flash peace signs."),
    ("d154_fam_wipe_mouth_snack", "family", "帮小吃货擦嘴角残渣", "慢点吃没人抢", "慢點吃沒人搶", "Eat slowly~", "천천히 먹어~", "ゆっくり食べなさい", "bubble", "round", "Person A wiping the corner of Person B's mouth with a handkerchief while Person B grins."),
    ("d155_fam_measure_height", "family", "手比头顶量身高", "又长高啦!", "又長高啦!", "Grew taller!", "키 많이 컸네!", "背が伸びたね!", "caption", "round", "Person A holding a flat hand over Person B's head to measure their height with pride."),
    ("d156_fam_homework_sigh", "family", "辅导作业血压飙升", "深呼吸亲生的", "深呼吸親生的", "Breathe... family...", "참자 내 동생이다...", "深呼吸…大事な家族…", "bubble", "thought", "Person A pointing at a notebook while pressing one hand to forehead in comedic tutoring stress."),
    ("d157_fam_praise_thumbs_up", "family", "双手竖大拇指夸奖宝贝", "太争气了!", "太爭氣了!", "So proud of you!", "우리 장하다 최고!", "よく頑張ったね!", "bubble", "shout", "Person A giving double thumbs-up and beaming with pride at Person B."),
    ("d158_fam_share_ice_cream", "family", "一人一口冰淇淋甜笑", "甜甜的日常", "甜甜的日常", "Sweet day", "달콤한 일상", "甘いひととき", "caption", "heart", "Both people holding ice cream cones close together with happy summer smiles."),
    ("d159_fam_whisper_secret", "family", "手拢嘴边说悄悄话", "别告诉爸妈哦", "別告訴爸媽哦", "Our little secret", "엄마한테는 비밀이야", "ママには内緒だよ", "bubble", "whisper", "Person A whispering a secret into Person B's ear with a playful wink."),
    ("d160_fam_warm_shoulder_hug", "family", "一左一右揽肩全家福笑", "相亲相爱一家人", "相親相愛一家人", "Family love", "사랑하는 우리 가족", "仲良しファミリー", "caption", "heart", "Both people standing close with arms around each other's shoulders in a warm family portrait."),
    ("d161_fam_fix_hair_clip", "family", "温柔帮整理刘海发卡", "打扮得美美的", "打扮得美美的", "All pretty now", "예쁘게 단장 끝!", "可愛くなったよ", "bubble", "heart", "Person A gently adjusting a hair clip on Person B's bangs with a tender smile."),
    ("d162_fam_cheer_pom_pom", "family", "一起挥拳加油打气", "冲鸭必胜!", "衝鴨必勝!", "You got this!", "파이팅 할 수 있어!", "絶対勝てるよ!", "bubble", "shout", "Both people pumping fists together in synchronized family cheering."),
    ("d163_fam_sleepy_lean", "family", "困困靠在姐姐肩头揉眼", "困困要抱抱", "困困要抱抱", "Sleepy cuddle", "졸려 안아줘~", "眠い〜抱っこ", "bubble", "round", "Person B rubbing sleepy eyes while leaning against Person A's comforting shoulder."),
    ("d164_fam_funny_glasses", "family", "一起戴搞怪眼镜比耶", "快乐加倍", "快樂加倍", "Double fun!", "즐거움도 두 배!", "楽しさ2倍!", "caption", "round", "Both people making finger-glasses over their eyes with big goofy grins."),
    ("d165_fam_umbrella_pickup", "family", "下雨天撑伞来接你", "接你回家啦", "接你回家啦", "Let's go home", "집에 가자 데리러 왔어", "お迎えに来たよ", "bubble", "heart", "Person A holding an umbrella over Person B with a warm welcoming smile."),
    ("d166_fam_cooking_taste", "family", "拿勺子喂尝一口美味", "尝尝咸淡", "嚐嚐鹹淡", "Taste this!", "간 좀 봐봐 맛있다!", "味見してみて!", "bubble", "round", "Person A holding a tasting spoon for Person B who leans in eagerly."),
    ("d167_fam_Wrap_blanket", "family", "把俩人裹进同一条毛毯", "暖呼呼过冬", "暖呼呼過冬", "Cozy together", "따뜻하게 꽁꽁", "ぬくぬく一緒", "caption", "heart", "Both people wrapped snugly together inside one soft fluffy blanket."),
    ("d168_fam_heart_crown", "family", "一高一低合体头顶比心", "爱你一万年", "愛你一萬年", "Love you lots!", "사랑해 우리 가족!", "ずっと大好き!", "bubble", "heart", "Both people forming a big heart over their heads together with radiant smiles."),
]


# 3. 22 NEW MEME TEMPLATES (m39 .. m60 -> total 60)
# Tuple: (id, name_zh, cat, zh_cn, zh_tw, en, ja, ko, mood, pose, elements)
NEW_MEMES = [
    ("m39_mbti_enfp", "MBTI快乐小狗标签", "abstract", "ENFP快乐小狗", "ENFP快樂小狗", "ENFP Golden Retriever", "ENFPハッピーわんこ", "ENFP 해피 강아지", "energetic", "beaming with a huge puppy-like smile and waving both hands excitedly", [
        {"type": "chip", "position": "top-left", "text": {"zh-CN": "MBTI: ENFP", "zh-TW": "MBTI: ENFP", "en": "MBTI: ENFP", "ja": "MBTI: ENFP", "ko": "MBTI: ENFP"}},
        {"type": "notice", "position": "bottom", "text": {"zh-CN": "快乐小狗 摇尾入场", "zh-TW": "快樂小狗 搖尾入場", "en": "PURE GOLDEN RETRIEVER ENERGY", "ja": "ハッピーわんこ登場", "ko": "인간 리트리버 등장"}, "color": "#10B981"}
    ]),
    ("m40_mbti_intj", "MBTI冷漠学霸标签", "abstract", "INTJ莫挨老子", "INTJ莫挨老子", "INTJ Do Not Disturb", "INTJ話しかけるな", "INTJ 말 걸지 마", "cold", "crossing arms with an icy composed stare and raised chin", [
        {"type": "chip", "position": "top-left", "text": {"zh-CN": "MBTI: INTJ", "zh-TW": "MBTI: INTJ", "en": "MBTI: INTJ", "ja": "MBTI: INTJ", "ko": "MBTI: INTJ"}},
        {"type": "notice", "position": "bottom", "text": {"zh-CN": "生人勿近 正在布局", "zh-TW": "生人勿近 正在佈局", "en": "CALCULATING — DO NOT DISTURB", "ja": "思考中につき接近禁止", "ko": "접근 금지 · 뇌 풀가동"}, "color": "#6366F1"}
    ]),
    ("m41_cyber_wooden_fish", "赛博木鱼功德+1", "abstract", "功德+1", "功德+1", "Karma +1", "徳+1", "공덕 +1", "zen", "pressing palms together in calm mock-piety with eyes peacefully closed", [
        {"type": "chip", "position": "top-right", "text": {"zh-CN": "功德 +1", "zh-TW": "功德 +1", "en": "KARMA +1", "ja": "功徳 +1", "ko": "공덕 +1"}, "color": "#F59E0B"},
        {"type": "notice", "position": "bottom", "text": {"zh-CN": "敲碎赛博木鱼 佛祖原谅我", "zh-TW": "敲碎賽博木魚 佛祖原諒我", "en": "CYBER WOODEN FISH: FORGIVE ME", "ja": "サイバー木魚ポクポク", "ko": "사이버 목탁 톡톡"}, "color": "#D97706"}
    ]),
    ("m42_battery_1_percent", "社交电量仅剩1%", "chat-ui", "电量1%", "電量1%", "Battery 1%", "残量1%", "배터리 1%", "drained", "slumping forward with half-closed eyes and a completely drained expression", [
        {"type": "top_bar", "position": "top", "text": {"zh-CN": "⚠️ 社交电量仅剩 1%", "zh-TW": "⚠️ 社交電量僅剩 1%", "en": "⚠️ SOCIAL BATTERY 1%", "ja": "⚠️ 社交バッテリー残り1%", "ko": "⚠️ 소셜 배터리 1%"}, "color": "#EF4444"}
    ]),
    ("m43_wechat_transfer_520", "微信转账520待收款", "chat-ui", "请收款520", "請收款520", "Transfer $520", "送金¥52000", "52만원 송금", "generous", "extending one hand forward with a suave generous smile", [
        {"type": "notice", "position": "bottom", "text": {"zh-CN": "💴 转账 ¥520.00 请收款", "zh-TW": "💴 轉帳 ¥520.00 請收款", "en": "💸 TRANSFER $520.00 SENT", "ja": "💴 送金を受け取ってください", "ko": "💸 송금 도착 · 받기"}, "color": "#F97316"}
    ]),
    ("m44_voice_msg_60s", "60秒语音方阵轰炸", "chat-ui", "60秒语音轰炸", "60秒語音轟炸", "60s Voice Note", "60秒ボイス爆撃", "60초 음성폭격", "talkative", "holding phone to mouth speaking non-stop with animated hand gestures", [
        {"type": "chip", "position": "top-left", "text": {"zh-CN": "(( 60'' ████████ •", "zh-TW": "(( 60'' ████████ •", "en": "(( 60s ████████ •", "ja": "(( 60秒 ████████ •", "ko": "(( 60초 ████████ •"}, "color": "#22C55E"}
    ]),
    ("m45_behaving_stamp", "已老实求放过红章", "ban-warning", "已老实求放过", "已老實求放過", "Behaving Now", "反省してます", "반성 중입니다", "meek", "looking up with big obedient puppy eyes and hands neatly folded", [
        {"type": "stamp", "position": "bottom-right", "text": {"zh-CN": "已老实", "zh-TW": "已老實", "en": "BEHAVING", "ja": "反省済", "ko": "순해짐"}, "color": "#DC2626", "angle": -15, "animate": "slam"}
    ]),
    ("m46_crazy_meter_999", "发疯指数999%检测仪", "abstract", "发疯指数999%", "發瘋指數999%", "Sanity 0%", "狂気度999%", "광기 지수 999%", "unhinged", "laughing wildly with hands in hair and chaotic energy", [
        {"type": "top_bar", "position": "top", "text": {"zh-CN": "🚨 精神发疯指数：999%", "zh-TW": "🚨 精神發瘋指數：999%", "en": "🚨 CHAOS LEVEL: 999%", "ja": "🚨 テンション異常値 999%", "ko": "🚨 텐션 폭주 999%"}, "color": "#E11D48"}
    ]),
    ("m47_tui_tui_barrier", "退退退红字结界", "classic-meme", "退!退!退!", "退!退!退!", "BACK OFF!", "悪霊退散!", "물러가라!", "fierce", "thrusting one arm forward in a dramatic fencing warding stance", [
        {"type": "stamp", "position": "top-right", "text": {"zh-CN": "退！退！退！", "zh-TW": "退！退！退！", "en": "BACK OFF!", "ja": "退散！", "ko": "물러가라!"}, "color": "#DC2626", "angle": 10, "animate": "slam"}
    ]),
    ("m48_sweating_bro", "汗流浃背了吧老弟", "classic-meme", "汗流浃背了吧", "汗流浹背了吧", "Sweating yet?", "冷や汗かいてる?", "식은땀 나지?", "smug", "pointing at the camera with a teasing knowing grin", [
        {"type": "notice", "position": "bottom", "text": {"zh-CN": "汗流浃背了吧老弟", "zh-TW": "汗流浹背了吧老弟", "en": "SWEATING BULLETS YET?", "ja": "冷や汗かいてるでしょ", "ko": "식은땀 좀 흘렸겠는데?"}, "color": "#0284C7"}
    ]),
    ("m49_zundu_jiadu", "尊嘟假嘟O.o弹窗", "classic-meme", "尊嘟假嘟O.o", "尊嘟假嘟O.o", "For real?! O.o", "マ?! O.o", "진짜루?! O.o", "curious", "tilting head with one eyebrow raised and big curious eyes", [
        {"type": "chip", "position": "top-left", "text": {"zh-CN": "尊嘟假嘟 O.o", "zh-TW": "尊嘟假嘟 O.o", "en": "For real?! O.o", "ja": "ホントに?! O.o", "ko": "진짜루?! O.o"}, "color": "#EC4899"}
    ]),
    ("m50_heavy_stealth", "偷感很重探测框", "abstract", "偷感很重", "偷感很重", "Sneaky mode", "こっそり感満載", "몰래 온 손님", "sneaky", "tiptoeing and glancing sideways with a funny guilty expression", [
        {"type": "chip", "position": "top-right", "text": {"zh-CN": "🔍 偷感很重", "zh-TW": "🔍 偷感很重", "en": "🔍 SNEAKY VIBES", "ja": "🔍 こっそりモード", "ko": "🔍 은밀한 기운"}, "color": "#475569"}
    ]),
    ("m51_hard_control_10s", "硬控全场10秒", "ai-meme", "硬控我10秒", "硬控我10秒", "Stunned for 10s", "10秒間フリーズ", "10초간 정지", "stunned", "frozen mid-gesture with wide eyes and jaw slightly dropped", [
        {"type": "spinner", "position": "top-left", "text": {"zh-CN": "硬控中 10.0s...", "zh-TW": "硬控中 10.0s...", "en": "STUNNED 10.0s...", "ja": "硬直中 10.0秒...", "ko": "홀딩 중 10.0초..."}, "color": "#8B5CF6"}
    ]),
    ("m52_three_days_visible", "仅三天可见锁头", "chat-ui", "仅三天可见", "僅三天可見", "Last 3 Days Only", "3日間のみ公開", "최근 3일만 공개", "aloof", "turning slightly away with a cool mysterious half-smile", [
        {"type": "notice", "position": "bottom", "text": {"zh-CN": "🔒 朋友仅展示最近三天的朋友圈", "zh-TW": "🔒 朋友僅展示最近三天的朋友圈", "en": "🔒 MOMENTS: LAST 3 DAYS ONLY", "ja": "🔒 直近3日間の投稿のみ表示", "ko": "🔒 최근 3일 게시물만 표시"}, "color": "#64748B"}
    ]),
    ("m53_read_no_reply", "已读不回暴击印章", "work-life", "已读不回", "已讀不回", "Left on Read", "既読スルー", "읽씹 완료", "indifferent", "glancing down at phone and casually tossing it aside", [
        {"type": "stamp", "position": "bottom-right", "text": {"zh-CN": "已读不回", "zh-TW": "已讀不回", "en": "READ · NO REPLY", "ja": "既読スルー", "ko": "읽씹"}, "color": "#EA580C", "angle": -12, "animate": "slam"}
    ]),
    ("m54_god_of_wealth_feed", "泼天的富贵砸中我", "work-life", "泼天的富贵", "潑天的富貴", "Sudden Jackpot", "爆益到来", "대박 행운 당첨", "blessed", "opening arms wide looking upward with a radiant blessed smile", [
        {"type": "notice", "position": "bottom", "text": {"zh-CN": "✨ 接住这波泼天的富贵 ✨", "zh-TW": "✨ 接住這波潑天的富貴 ✨", "en": "✨ CATCHING MASSIVE FORTUNE ✨", "ja": "✨ 最高の金運キャッチ ✨", "ko": "✨ 대박 행운 접수 완료 ✨"}, "color": "#EAB308"}
    ]),
    ("m55_love_brain_cert", "确诊恋爱脑诊断书", "abstract", "确诊恋爱脑", "確診戀愛腦", "Certified Simp", "恋愛脳確定", "연애세포 과다", "lovestruck", "cupping blushing cheeks with heart-struck dreamy eyes", [
        {"type": "stamp", "position": "top-right", "text": {"zh-CN": "确诊恋爱脑", "zh-TW": "確診戀愛腦", "en": "LOVE BRAIN", "ja": "恋愛脳確定", "ko": "사랑꾼 확정"}, "color": "#F43F5E", "angle": 12, "animate": "slam"}
    ]),
    ("m56_iq_insufficient", "智商余额不足弹窗", "ai-meme", "智商余额不足", "智商餘額不足", "IQ Low Balance", "知能残高不足", "뇌 용량 부족", "derp", "scratching head with a cute blank confused smile", [
        {"type": "top_bar", "position": "top", "text": {"zh-CN": "⚠️ 您的智商余额不足 请及时充值", "zh-TW": "⚠️ 您的智商餘額不足 請及時充值", "en": "⚠️ IQ BALANCE LOW — PLEASE RECHARGE", "ja": "⚠️ 思考回路の残高が不足しています", "ko": "⚠️ 뇌 용량이 부족합니다"}, "color": "#F59E0B"}
    ]),
    ("m57_no_empty_promises", "禁止画饼警示牌", "work-life", "禁止画饼", "禁止畫餅", "No Empty Promises", "口約束禁止", "희망고문 금지", "stern", "holding up both hands in an X gesture with a deadpan office look", [
        {"type": "prohibition", "position": "top-right", "text": {"zh-CN": "禁止画饼", "zh-TW": "禁止畫餅", "en": "NO HYPE", "ja": "空手形禁止", "ko": "빈말 금지"}, "color": "#DC2626"}
    ]),
    ("m58_slacking_permit", "官方持证摸鱼印章", "work-life", "持证摸鱼", "持證摸魚", "Licensed Slacker", "公認サボり中", "합법적 농땡이", "relaxed", "leaning back sipping tea leisurely at work with a peaceful grin", [
        {"type": "stamp", "position": "bottom-right", "text": {"zh-CN": "持证摸鱼", "zh-TW": "持證摸魚", "en": "SLACK PERMIT", "ja": "サボり許可証", "ko": "농땡이 허가"}, "color": "#16A34A", "angle": -10, "animate": "slam"}
    ]),
    ("m59_clock_out_timer", "光速下班倒计时", "work-life", "光速下班", "光速下班", "Clocking Out!", "定時ダッシュ", "칼퇴근 준비", "eager", "checking wristwatch and poised like a sprinter at the starting line", [
        {"type": "chip", "position": "top-left", "text": {"zh-CN": "⏱️ 下班倒计时 00:01", "zh-TW": "⏱️ 下班倒計時 00:01", "en": "⏱️ CLOCK OUT 00:01", "ja": "⏱️ 定時まで 00:01", "ko": "⏱️ 퇴근 1초 전"}, "color": "#0EA5E9"}
    ]),
    ("m60_ai_hallucination", "AI一本正经胡说八道", "ai-meme", "一本正经胡说", "一本正經胡說", "Confident Hallucination", "堂々とデタラメ", "뻔뻔한 아무말", "confident", "gesturing like a professor giving a lecture with a totally confident poker face", [
        {"type": "spinner", "position": "top-left", "text": {"zh-CN": "AI 正在编造事实...", "zh-TW": "AI 正在編造事實...", "en": "AI HALLUCINATING...", "ja": "もっともらしい嘘を生成中...", "ko": "그럴싸한 아무말 생성 중..."}, "color": "#D97757"}
    ]),
]


def main() -> None:
    # 1. Update expression-presets.json
    expr_path = REF / "expression-presets.json"
    exprs = json.loads(expr_path.read_text(encoding="utf-8"))[:132]
    existing_ids = {x["id"] for x in exprs}

    for eid, cat, zh_cn, zh_tw, en, ko, ja, mood, layout, shape, pose in NEW_EXPRS:
        if eid in existing_ids:
            continue
        bubble = None
        if layout in ("bubble", "both"):
            bubble = {
                "texts": {"zh-CN": zh_cn, "zh-TW": zh_tw, "en": en, "ja": ja, "ko": ko},
                "shape": shape,
                "position": "auto",
                "animation": "pop",
            }
        exprs.append({
            "id": eid,
            "category": cat,
            "caption": zh_cn,
            "captions": {"zh-CN": zh_cn, "zh-TW": zh_tw, "en": en, "ja": ja, "ko": ko},
            "mood": mood,
            "static_pose": f"Photorealistic real-person portrait sticker cutout: {pose}. Preserve exact facial bone structure, real skin texture, hairstyle, and outfit.",
            "text_layout": layout,
            "bubble": bubble,
            "motion": {
                "type": "wave_hand",
                "duration_ms": 1280,
                "frames": 8,
                "loop": "seamless",
                "amplitude": "medium",
                "keyframe_poses": [
                    f"Frame 1 (Top-Left): Starting real-person pose — {pose}; eyes open, lower torso anchored.",
                    f"Frame 2 (Top-Right): Mid-action progression — {pose} with natural eye blink or micro-expression shift; lower torso anchored.",
                    f"Frame 3 (Bottom-Left): Peak expressive moment — {pose} at full expressive intensity; lower torso anchored.",
                    f"Frame 4 (Bottom-Right): Smooth return toward Frame 1 for seamless loop; lower torso anchored.",
                ],
                "stationary_parts": ["lower_torso", "outfit", "hair_or_fur_pattern"],
            },
        })

    expr_path.write_text(json.dumps(exprs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {expr_path}: {len(exprs)} expressions")

    # 2. Update duo-presets.json
    duo_path = REF / "duo-presets.json"
    duos = json.loads(duo_path.read_text(encoding="utf-8"))[:108]
    existing_duo_ids = {x["id"] for x in duos}

    for did, cat, name_zh, zh_cn, zh_tw, en, ko, ja, layout, shape, pose in NEW_DUOS:
        if did in existing_duo_ids:
            continue
        duos.append({
            "id": did,
            "name_zh": name_zh,
            "category": cat,
            "caption": zh_cn,
            "captions": {"zh-CN": zh_cn, "zh-TW": zh_tw, "en": en, "ko": ko, "ja": ja},
            "mood": f"{cat}: {name_zh}",
            "static_pose": f"Two-person real-photo portrait sticker cutout: {pose} Faithfully preserve BOTH Person A and Person B's exact real facial features, bone structure, real skin texture, hairstyles, and outfits from their reference photos.",
            "text_layout": layout,
            "bubble": {
                "texts": {"zh-CN": zh_cn, "zh-TW": zh_tw, "en": en, "ko": ko, "ja": ja},
                "shape": shape,
                "position": "auto",
                "animation": "pop",
            },
            "motion": {
                "type": "duo_interaction",
                "duration_ms": 600,
                "frames": 8,
                "loop": "pingpong",
                "amplitude": "medium",
                "keyframe_poses": [
                    f"Frame 1 (top-left): Starting pose — {pose} Both real people maintain exact facial likeness.",
                    f"Frame 2 (top-right): Mid-motion — Both people lean slightly closer into the interaction ({name_zh}), natural eye blink and warm micro-expressions.",
                    f"Frame 3 (bottom-left): Peak interaction — Full expressive peak of '{name_zh}', authentic chemistry and lively hand/head movement.",
                    f"Frame 4 (bottom-right): Settling back smoothly toward Frame 1 for a seamless loop.",
                ],
                "stationary_parts": ["lower_torso", "camera_frame", "identities"],
            },
        })

    duo_path.write_text(json.dumps(duos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {duo_path}: {len(duos)} duo presets")

    # 3. Update meme-templates.json
    meme_path = REF / "meme-templates.json"
    memes = json.loads(meme_path.read_text(encoding="utf-8"))[:38]
    existing_meme_ids = {x["id"] for x in memes}

    for mid, name_zh, cat, zh_cn, zh_tw, en, ja, ko, mood, pose, elements in NEW_MEMES:
        if mid in existing_meme_ids:
            continue
        memes.append({
            "id": mid,
            "name_zh": name_zh,
            "category": cat,
            "caption": zh_cn,
            "captions": {"zh-CN": zh_cn, "zh-TW": zh_tw, "en": en, "ja": ja, "ko": ko},
            "mood": mood,
            "static_pose": pose,
            "text_layout": "none",
            "bubble": None,
            "motion": {
                "type": "nod",
                "duration_ms": 1280,
                "frames": 8,
                "loop": "seamless",
                "amplitude": "medium",
                "keyframe_poses": [
                    f"Frame 1: {pose}; eyes open, lower body stays in place.",
                    f"Frame 2: Mid-action shift in expression ({name_zh}), natural blink; lower body stays in place.",
                    f"Frame 3: Peak reaction for {name_zh}; lower body stays in place.",
                    f"Frame 4: Smooth return to Frame 1; lower body stays in place.",
                ],
                "stationary_parts": ["lower_torso", "outfit", "hair_or_fur_pattern"],
            },
            "meme": {
                "style_hint": f"Expressive real-person reaction for {name_zh}, no text in raster image",
                "background": None,
                "filters": [],
                "elements": elements,
            },
        })

    meme_path.write_text(json.dumps(memes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {meme_path}: {len(memes)} meme templates")


if __name__ == "__main__":
    main()
