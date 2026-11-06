<p align="right">
  <strong>Language:</strong>
  <a href="README.md"><b>简体中文</b></a> |
  <a href="README.en.md"><b>English</b></a> |
  <a href="README.ko.md"><b>한국어</b></a> |
  <a href="README.ja.md"><b>日本語</b></a>
</p>

# WeChat Sticker Maker · 実写人物専用 AIスタンプ＆ミーム生成エンジン

> **Your Face, Your Vibe, Your Sticker Pack.**  
> **実写の人物写真（`human-portrait`）**専用に設計された、ChatGPT / Codex スキル＆Pythonスタンプ・ミーム一括生成エンジンです。ご本人の顔立ち、骨格、肌の質感、髪型、服装を忠実に保ち、**勝手に2Dアニメ風やデフォルメイラストに変えてしまうことはありません。** 一度の生成で LINE、WeChat、Instagram、TikTok、Telegram、Discord など**世界23種類の主要SNS・チャットアプリ**の規格へ同時に書き出せます。

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Real Person Only](https://img.shields.io/badge/Subject-100%25%20Real%20Person%20Portrait-ff69b4.svg)](#内蔵された108種類の実写フォトスタイル-referencesstyle-presetsjson)
[![Styles](https://img.shields.io/badge/Photographic%20Styles-108%20Presets%20(General%20%7C%20KR%20%7C%20JP%20%7C%20CN)-blue.svg)](#内蔵された108種類の実写フォトスタイル-referencesstyle-presetsjson)
[![Duo Interactions](https://img.shields.io/badge/Two--Person%20Duo-108%20Presets%20(Besties%2036%20%7C%20Couple%2036%20%7C%20Yuri%2036)-ff2d55.svg)](#内蔵された108種類の2人ペア実写スタンププリセット-親友--カップル--百合)
[![Expressions & Memes](https://img.shields.io/badge/Catalog-132%20Expressions%20%7C%2038%20Memes%20%7C%20129%20Motions-success.svg)](#14カテゴリーの実写表情カタログ)
[![Languages](https://img.shields.io/badge/Single--Language%20Bubbles-zh--CN%20%7C%20zh--TW%20%7C%20en%20%7C%20ja%20%7C%20ko-orange.svg)](#7種類の吹き出しデザインと5言語の単一言語出力)
[![Platforms](https://img.shields.io/badge/Export-23%20Social%20Platforms-purple.svg)](#23プラットフォームへの一括書き出しとsnsカバー生成)

</div>

![実写スタンプショーケース](docs/gallery/images/hero.jpg)

> **[実写スタンプギャラリー全文を見る（全108スタイル / 10種類のアニメーションGIF / 38種類のミーム / 14種類の表情カテゴリー） → `docs/gallery/README.md`](docs/gallery/README.md)**

**対応する全23プラットフォーム**：LINE、Instagram、TikTok、X（旧Twitter）、Telegram、WhatsApp、Discord、Slack、KakaoTalk、iMessage、Signal、Viber、GIPHY、Facebook、WeChat（微信）、QQ、小紅書（RED）、Douyin、Weibo など。

---

## 主な特徴

- **全108種類の実写専用フォトスタイル（汎用 / 韓国系 / 日本系 / 中国系の4大シリーズ）**：デフォルトの `real-cutout` では美しい4pxの白フチ付きダイカットステッカーを生成。ライティングや色調、空気感のみを変化させ、本人の顔立ちを100%リアルに保ちます。
- **Codex AIの描画能力による本格マルチフレームアニメーション**：手を振る、ウインクする、首をかしげるといった動きを、Codex AIが `2×2` の4コマ連続アクションシート（`build_sprite_sheet_prompt`）として描き下ろします。Python側は非破壊の背景透過、体幹基準の位置合わせ、白フチ・文字入れ・エンコードのみを担当し、不自然な画像の引き伸ばしは一切行いません。
- **豊富な表情＆モーションライブラリ**：14カテゴリー・132種類の表情 × 129種類のモーション（`references/motion-library.json`）を収録し、すべての表情に4フレームのAI絵コンテを備えています。
- **38種類の実写ミーム＆ネタ画像テンプレート**：AI「思考中...」スピナー、「中国IP検知・接近禁止」、「これ以上喋ったらBAN」、「999秒間深く思考しました」、「レート制限超過」、「脳内404エラー」など38種類のテンプレート（`references/meme-templates.json`）を内蔵。
- **7種類の吹き出し＆厳格な単一言語ルール**：下部テロップ（`caption`）、吹き出し（`bubble`）、両方（`both`）、文字なし（`none`）に対応。日本語（`ja`）、韓国語（`ko`）、英語（`en`）、中国語簡体字・繁体字（`zh-CN`/`zh-TW`）を内蔵し、**1枚のスタンプには必ず1つの言語のみを表示（複数言語の混在を完全に防止）**します。
- **1つのマスターから23プラットフォームへ自動変換**：720pxの透過マスターから、各アプリの透過PNG / アニメーションGIF / APNG / WebP / WebM規格およびSNS投稿用カバー画像（9:16 ストーリー、3:4 カバー、3×3 グリッド）を自動出力します。

---

## 内蔵された108種類の実写フォトスタイル（`references/style-presets.json`）

**汎用（18種） / 韓国系（30種） / 日本系（30種） / 中国系（30種）** の計108スタイルを収録しており、CLIからシリーズ別に絞り込み可能です：`wechat-sticker-maker styles --region jp`。

![4大フォトスタイルシリーズ比較](docs/gallery/images/four-series.jpg)

![実写スタンプスタイル一覧](docs/gallery/images/styles-overview.jpg)

### 汎用シリーズ（18種）
| # | スタイルID (`--style`) | スタイル名 | ライティング＆プリセット名 |
|---|---|---|---|
| 1 | `real-cutout` | **実写ポートレート切り抜き（デフォルト）** | `studio-portrait` · 真人写真抠图贴纸 |
| 2 | `real-bobblehead` | **実写デフォルメ頭身ステッカー** | `bright-studio` · 真人搞怪大头贴 |
| 3 | `real-street-cool` | **ストリートフラッシュスナップ** | `editorial-flash` · 真人潮酷街拍贴纸 |
| 4 | `real-vintage-ccd` | **Y2K ヴィンテージCCDデジカメ** | `ccd-warm-flash` · 真人复古CCD胶片贴纸 |
| 5 | `real-work-emo` | **社会人リアル日常スナップ** | `natural-candid` · 真人打工人纪实梗图 |
| 6 | `real-high-contrast` | **白黒ハイコントラストミーム** | `high-contrast-studio` · 真人黑白高反差梗图 |
| 7 | `real-polaroid-instant` | **ポラロイド SX-70 インスタント写真** | `polaroid-instant` · 真人拍立得即时相纸 |
| 8 | `real-fisheye-y2k` | **Y2K 16mm 魚眼レンズ風クローズアップ** | `fisheye-y2k-flash` · 真人千禧鱼眼大头贴 |
| 9 | `real-paparazzi-flash` | **夜間パパラッチ直焚きフラッシュ** | `paparazzi-direct-flash` · 真人狗仔直闪抓拍 |
| 10 | `real-golden-hour` | **ゴールデンアワー夕暮れ逆光** | `golden-hour-sunset` · 真人落日夕阳逆光 |
| 11 | `real-blue-hour` | **ブルーアワー映画風トワイライト** | `blue-hour-cinematic` · 真人蓝调时刻电影感 |
| 12 | `real-cyber-neon` | **サイバーパンク・デュアルネオン夜景** | `cyber-dual-neon` · 真人赛博霓虹夜景 |
| 13 | `real-film-kodak-gold` | **Kodak Gold 200 ウォームフィルム** | `kodak-gold-200` · 真人柯达Gold200胶片 |
| 14 | `real-film-cinestill-800t` | **CineStill 800T タングステン映画フィルム** | `cinestill-800t` · 真人CineStill钨丝灯胶片 |
| 15 | `real-vogue-editorial` | **ハイファッション誌スタジオ照明** | `vogue-rembrandt-studio` · 真人高定时尚杂志封面 |
| 16 | `real-french-effortless` | **パリジェンヌ午後の窓辺自然光** | `french-afternoon-sun` · 真人法式慵懒午后写真 |
| 17 | `real-american-yearbook` | **90年代アメリカ卒業アルバム風スタジオ** | `retro-yearbook-studio` · 真人美式复古毕业年鉴 |
| 18 | `real-thermal-ir` | **フェスUVデュオトーン・ステージ照明** | `uv-festival-duo` · 真人潮流伪彩视觉 |

### 韓国系シリーズ（`韩系` · 30種）
![韓国系スタイルプレビュー](docs/gallery/images/series-kr.jpg)

| # | スタイルID (`--style`) | スタイル名 | ライティング＆プリセット名 |
|---|---|---|---|
| 1 | `real-purikura` | **韓国「人生4カット」フォトブース** | `creamy-kbeauty` · 韩系人生四格大头贴 |
| 2 | `real-kr-idol-selfie` | **K-POPアイドルセルフィー** | `kpop-ringlight` · 韩系爱豆自拍 |
| 3 | `real-kr-glass-skin` | **韓国水光肌（グラススキン）** | `kbeauty-dewy` · 韩系水光肌清透 |
| 4 | `real-kr-photocard` | **K-POPトレーディングカード風** | `pastel-gradient-studio` · 韩系爱豆小卡 |
| 5 | `real-kr-cafe-film` | **ソウルカフェ・ウォームフィルム** | `window-daylight` · 韩系咖啡馆胶片 |
| 6 | `real-kr-drama` | **韓国ドラマヒロイン逆光ムード** | `kdrama-backlight` · 韩剧主角氛围 |
| 7 | `real-kr-variety` | **韓国バラエティ番組テロップ風** | `kvariety-highkey` · 韩综字幕斗图 |
| 8 | `real-kr-music-bank` | **K-POP音楽番組「エンディング妖精」照明** | `kpop-stage-ending` · 韩系打歌舞台Ending妖精 |
| 9 | `real-kr-fansign-soft` | **アイドルサイン会・ふんわりソフト光** | `kr-fansign-telephoto` · 韩系签售会奶油柔光 |
| 10 | `real-kr-airport-snap` | **仁川空港セレブ私服スナップ風** | `kr-airport-daylight` · 韩系仁川机场路透街拍 |
| 11 | `real-kr-hongdae-street` | **弘大（ホンデ）ストリートスナップ** | `kr-hongdae-overcast` · 韩系弘大街头潮拍 |
| 12 | `real-kr-seongsu-industrial` | **聖水洞（ソンスドン）無機質カフェ自然光** | `kr-seongsu-concrete` · 韩系圣水洞工业风写真 |
| 13 | `real-kr-hannam-oldmoney` | **漢南洞（ハンナムドン）上品カシミヤムード** | `kr-hannam-cashmere` · 韩系汉南洞千金氛围 |
| 14 | `real-kr-apgujeong-glam` | **狎鴎亭（アックジョン）ナイトフラッシュ** | `kr-apgujeong-flash` · 韩系狎鸥亭闪光夜拍 |
| 15 | `real-kr-jeju-breeze` | **済州島（チェジュ）海風クリアフィルム** | `kr-jeju-coastal-sun` · 韩系济州岛海风胶片 |
| 16 | `real-kr-hanok-sunlight` | **北村韓屋（ハノク）木漏れ日ウォーム光** | `kr-hanok-warm-wood` · 韩系北村韩屋暖阳 |
| 17 | `real-kr-winter-snow` | **初雪マフラー・冬ソナタ風ソフト光** | `kr-first-snow-soft` · 韩系初雪围巾恋歌 |
| 18 | `real-kr-cherry-blossom` | **汝矣島（ヨイド）桜並木スプリング光** | `kr-yeouido-blossom` · 韩系汝矣岛樱花柔光 |
| 19 | `real-kr-rainy-pocha` | **ソウル雨夜の屋台（ポチャ）暖色ライト** | `kr-pocha-warm-amber` · 韩系雨夜布帐马车 |
| 20 | `real-kr-high-teen` | **K-POPハイティーン学園ポップ照明** | `kr-highteen-pop` · 韩系High-Teen复古校园 |
| 21 | `real-kr-y2k-metallic` | **Y2Kシルバーメタリック・コンセプト照明** | `kr-y2k-silver-frost` · 韩系Y2K千禧银光 |
| 22 | `real-kr-balletcore` | **韓国バレエコア・パールピンク柔光** | `kr-balletcore-pearl` · 韩系芭蕾风柔粉写真 |
| 23 | `real-kr-clean-fit` | **江南クリーンフィット純白スタジオ照明** | `kr-cleanfit-cyclorama` · 韩系Clean-Fit极简白棚 |
| 24 | `real-kr-id-photo` | **ソウル写真館・韓国証明写真ライティング** | `kr-id-butterfly-light` · 韩系最美证件照精修 |
| 25 | `real-kr-high-angle-booth` | **韓国ハイアングル（俯瞰）プリクラ照明** | `kr-high-angle-booth` · 韩系俯拍高角度四格 |
| 26 | `real-kr-bw-fourcut` | **韓国モノクロ・セルフ写真館風** | `kr-mono-photobooth` · 韩系黑白胶片四格 |
| 27 | `real-kr-practice-mirror` | **K-POP練習室ミラーセルフィー照明** | `kr-practice-room-bright` · 韩系练习室对镜自拍 |
| 28 | `real-kr-convenience-night` | **韓国深夜コンビニ・ネオン白色光** | `kr-convenience-fluorescent` · 韩系深夜便利店霓虹 |
| 29 | `real-kr-magazine-dazed` | **韓国モード誌アバンギャルド照明** | `kr-avant-garde-gel` · 韩系先锋画报冷冽光 |
| 30 | `real-kr-webtoon-real` | **韓国ウェブトゥーン実写化ヒロイン逆光** | `kr-webtoon-hero-glow` · 韩系漫改主角神颜光 |

### 日本系シリーズ（`日系` · 30種）
![日本系スタイルプレビュー](docs/gallery/images/series-jp.jpg)

| # | スタイルID (`--style`) | スタイル名 | ライティング＆プリセット名 |
|---|---|---|---|
| 1 | `real-jp-airy` | **日系エアリー透明感** | `airy-overexposed` · 日系空气感清新 |
| 2 | `real-jp-fuji-film` | **富士フイルム・ノスタルジック調** | `fuji-film` · 日系富士胶片 |
| 3 | `real-jp-purikura` | **東京プリクラ風パステル美肌** | `purikura-booth` · 日系大头贴プリクラ |
| 4 | `real-jp-summer` | **鎌倉サマーバックライト** | `summer-backlight` · 日系夏日逆光 |
| 5 | `real-jp-harajuku` | **原宿ストリートスナップ** | `street-flash` · 日系原宿街头 |
| 6 | `real-jp-showa` | **80年代昭和レトロフィルム** | `showa-retro` · 日系昭和复古 |
| 7 | `real-jp-rinko-pastel` | **川内倫子風ハイキー・パステル透明感** | `jp-rinko-highkey-pastel` · 日系川内伦子风淡彩 |
| 8 | `real-jp-hideaki-clean` | **濱田英明風・中判フィルム清涼自然光** | `jp-hideaki-medium-format` · 日系滨田英明风清透 |
| 9 | `real-jp-moriyama-bw` | **森山大道風ハイコントラスト粗粒子モノクロ** | `jp-moriyama-gritty-bw` · 日系森山大道粗颗粒黑白 |
| 10 | `real-jp-ninagawa-vivid` | **蜷川実花風・極彩色ビビッドライティング** | `jp-ninagawa-saturated` · 日系蜷川实花浓郁花影 |
| 11 | `real-jp-shibuya-neon` | **渋谷スクランブル交差点ナイトネオン** | `jp-shibuya-night-neon` · 日系涩谷十字路口霓虹 |
| 12 | `real-jp-shimokita-vintage` | **下北沢古着屋・ウォームフィルム調** | `jp-shimokita-warm-film` · 日系下北泽古着胶片 |
| 13 | `real-jp-daikanyama-morning` | **代官山モーニング書店・窓辺の朝光** | `jp-daikanyama-morning` · 日系代官山晨光书店 |
| 14 | `real-jp-ginza-luxury` | **銀座イブニング・シャンパンゴールド光** | `jp-ginza-champagne-glow` · 日系银座夜色流光 |
| 15 | `real-jp-kyoto-komorebi` | **京都庭園の木漏れ日（こもれび）和風光** | `jp-kyoto-komorebi` · 日系京都木漏日和风 |
| 16 | `real-jp-hokkaido-snow` | **北海道『Love Letter』雪原バウンス柔光** | `jp-hokkaido-snow-bounce` · 日系北海道情书雪景 |
| 17 | `real-jp-okinawa-sun` | **沖縄サマー・シーソルトブルー太陽光** | `jp-okinawa-sea-salt` · 日系冲绳盛夏海盐 |
| 18 | `real-jp-sakura-film` | **目黒川桜シーズン・春光ピンクフィルム** | `jp-sakura-spring-film` · 日系樱花季春光胶片 |
| 19 | `real-jp-autumn-icho` | **明治神宮外苑・銀杏並木オータム逆光** | `jp-autumn-ginkgo-gold` · 日系银杏大道秋日暖光 |
| 20 | `real-jp-rainy-hydrangea` | **鎌倉梅雨の紫陽花（あじさい）ブルー微光** | `jp-kamakura-rainy-blue` · 日系镰仓梅雨紫阳花 |
| 21 | `real-jp-onsen-steam` | **箱根温泉旅館・湯けむりウォームライト** | `jp-onsen-warm-mist` · 日系温泉旅馆暖雾 |
| 22 | `real-jp-izakaya-warm` | **深夜食堂・居酒屋提灯の暖色あかり** | `jp-izakaya-lantern` · 日系深夜食堂居酒屋 |
| 23 | `real-jp-kissaten-retro` | **昭和純喫茶・琥珀色ランプのレトロ光** | `jp-kissaten-amber` · 日系纯喫茶昭和咖啡 |
| 24 | `real-jp-school-rooftop` | **青春高校屋上・青空バックライト** | `jp-rooftop-clear-sky` · 日系青春天台晴空 |
| 25 | `real-jp-matsuri-fireworks` | **夏祭り線香花火のウォームオレンジ微光** | `jp-sparkler-warm-glow` · 日系夏日祭花火微光 |
| 26 | `real-jp-nonno-magazine` | **日系ファッション誌スウィート棚拍柔光** | `jp-sweet-magazine-studio` · 日系甜美日杂画报 |
| 27 | `real-jp-popeye-cityboy` | **東京シティボーイ誌面風・自然光スナップ** | `jp-popeye-cityboy-sun` · 日系CityBoy街头画报 |
| 28 | `real-jp-utsurundesu` | **富士『写ルンです』フラッシュ＆粒子感** | `jp-quicksnap-disposable` · 日系写ルンです一次性胶片 |
| 29 | `real-jp-drama-subtitle` | **日本ドラマ黄金枠・映画風シネマ照明** | `jp-prime-drama-cinematic` · 日剧黄金档电影感剧照 |
| 30 | `real-jp-variety-telop` | **日本バラエティ番組・極太テロップ風** | `jp-variety-tv-bright` · 日综夸张大字报斗图 |

### 中国系シリーズ（`中式` · 30種）
![中国系スタイルプレビュー](docs/gallery/images/series-cn.jpg)

| # | スタイルID (`--style`) | スタイル名 | ライティング＆プリセット名 |
|---|---|---|---|
| 1 | `real-variety-meme` | **バラエティ番組ポップ文字スタンプ** | `high-key-tv` · 真人综艺花字斗图 |
| 2 | `real-cn-new-chinese` | **ネオチャイニーズ（新中式）写真** | `oriental-warm` · 新中式国风写真 |
| 3 | `real-cn-hk-retro` | **90年代香港シネマネオン** | `hk-neon-film` · 港风复古胶片 |
| 4 | `real-cn-xhs-vibe` | **RED（小紅書）クリーミームード** | `creamy-soft` · 小红书氛围感 |
| 5 | `real-cn-douyin` | **スタジオビューティーリングライト** | `ringlight-bright` · 抖音网红美颜 |
| 6 | `real-cn-studio-retro` | **90年代レトロ写真館風** | `retro-studio-softfocus` · 复古影楼风 |
| 7 | `real-cn-tw-youth` | **台湾青春インディーフィルム** | `afternoon-sun` · 台式青春胶片 |
| 8 | `real-cn-jiangnan-mist` | **江南水郷・青磁色の霧雨ソフト光** | `cn-jiangnan-celadon-mist` · 中式江南烟雨清冷 |
| 9 | `real-cn-palace-redwall` | **故宮の朱벽・ウォームサンライト** | `cn-crimson-wall-sun` · 中式红墙琉璃暖阳 |
| 10 | `real-cn-song-minimal` | **宋代ミニマリズム・宣紙ホワイト柔光** | `cn-song-ruyao-minimal` · 中式宋韵极简留白 |
| 11 | `real-cn-tang-splendor` | **盛唐ゴールド＆紅・華麗ランタン光** | `cn-tang-gilded-lantern` · 中式盛唐鎏金夜宴 |
| 12 | `real-cn-dunhuang-sunset` | **敦煌デザート・琥珀サンセット逆光** | `cn-dunhuang-amber-dusk` · 中式敦煌大漠流沙 |
| 13 | `real-cn-ink-wash-light` | **水墨グラデーション風モノクロ実写照明** | `cn-ink-studio-monochrome` · 中式水墨光影写真 |
| 14 | `real-cn-republican-velvet` | **1930年代オールド上海ベルベット暖光** | `cn-vintage-shanghai-tungsten` · 中式民国复古画报 |
| 15 | `real-cn-shanghai-bund` | **上海外灘『繁花』風アンバーゴールド夜景** | `cn-bund-amber-cinema` · 中式外滩流光夜色 |
| 16 | `real-cn-hk-tvb-90s` | **90年代香港TVBドラマ風ウォーム照明** | `cn-hk-tvb-90s-warm` · 港风90年代TVB剧照 |
| 17 | `real-cn-hk-cyber-rain` | **香港・旺角（モンコック）雨夜ネオン光** | `cn-mongkok-rain-neon` · 港风旺角雨夜霓虹 |
| 18 | `real-cn-tw-nightmarket` | **台北夜市・ウォームランタン玉ボケ光** | `cn-taipei-nightmarket` · 台式夜市烟火霓虹 |
| 19 | `real-cn-chengdu-teahouse` | **成都・竹林茶館の木漏れ日リラックス光** | `cn-chengdu-bamboo-sun` · 中式成都竹椅茶馆 |
| 20 | `real-cn-chongqing-cyber` | **重慶・山城の川霧ブルー＆暖色ネオン夜景** | `cn-chongqing-fog-neon` · 中式重庆山城迷雾夜 |
| 21 | `real-cn-dali-sunshine` | **雲南・大理洱海のクリアハイランド陽光** | `cn-dali-highland-sun` · 中式大理洱海慢生活 |
| 22 | `real-cn-hulunbuir-wind` | **フルンボイル大草原・爽風と草原バウンス光** | `cn-grassland-open-sky` · 中式草原旷野清风 |
| 23 | `real-cn-80s-factory` | **80年代中国レトロ・海鴎フィルムカメラ調** | `cn-80s-seagull-film` · 中式80年代怀旧胶片 |
| 24 | `real-cn-90s-calendar` | **90年代レトロカレンダー風・高彩度照明** | `cn-90s-calendar-bright` · 中式90年代挂历画报 |
| 25 | `real-cn-cny-festive` | **旧正月（春節）レッド＆ゴールド祝賀光** | `cn-lunar-new-year-gold` · 中式新春贺岁红金 |
| 26 | `real-cn-wuxia-breeze` | **武侠シネマ風クールスレート＆風になびく髪** | `cn-wuxia-cinematic-cool` · 中式武侠清风江湖 |
| 27 | `real-cn-tea-zen` | **囲炉裏茶室（囲炉煮茶）の禅ウォーム光** | `cn-tea-hearth-zen` · 中式围炉煮茶禅意 |
| 28 | `real-cn-guochao-street` | **国潮ストリート・朱赤×ピーコック青フラッシュ** | `cn-guochao-crimson-teal` · 中式国潮街头撞色 |
| 29 | `real-cn-work-survival` | **オフィスモニター光・社会人リアル表情** | `cn-office-monitor-glow` · 中式大厂打工人图鉴 |
| 30 | `real-cn-bazi-lucky` | **開運錦鯉（コイ）ゴールデンハロー柔光** | `cn-auspicious-golden-halo` · 中式锦鲤好运玄学风 |

---

## 内蔵された108種類の2人ペア実写スタンププリセット（親友 / カップル / 百合 · `references/duo-presets.json`）

2枚の人物写真（`-i personA.jpg -p personB.jpg`）を入力し、2人それぞれの本物の顔立ち・骨格・雰囲気を100%保ったペアスタンプを生成します（`wechat-sticker-maker duo --category besties|couple|yuri --language ja`）。

| カテゴリー (`--duo-category`) | 収録数 | ID範囲 | 代表的な2人アクション＆日本語単一言語セリフ例 |
|---|---|---|---|
| **👯‍♀️ 親友・女子会 (`besties` / `闺蜜`)** | **36種** | `d01` – `d36` | ほっぺ密着ピース自撮り (`最高の親友`)、2人でハートポーズ (`ぎゅっ`)、タピオカ乾杯 (`タピ活最高`)、ひそひそ恋バナ (`ここだけの話!`)、全力味方ハグ (`うちの子に何するの`) |
| **👩‍❤️‍👨 カップル・恋人 (`couple` / `情侣`)** | **36種** | `d37` – `d72` | 頭ぽんぽん (`いい子いい子`)、バックハグ (`充電中`)、ほっぺむにゅ (`大好きだよ`)、おでこコツン (`君だけ見てる`)、袖クイ甘え (`一緒にいて`)、マフラー半分こ |
| **🌸 百合・双女主 (`yuri` / `百合`)** | **36種** | `d73` – `d108` | 指先顎クイ見つめ合い (`お姉さま、私だけ見て`)、双女主の宿命感ほっぺ寄せ (`運命のふたり`)、クールお姉さま壁ドン (`ドキドキが止まらない...`)、肩借りうたた寝 (`ずっとそばにいるよ`)、赤い糸の約束 (`永遠に一緒`) |

---

## Codex AI 4フレームアニメーションGIFショーケース

![実写アニメーションGIFショーケース](docs/gallery/images/animated-showcase.gif)

---

## 14カテゴリーの実写表情カタログ

![実写表情カテゴリー 1/2](docs/gallery/images/expressions-01.jpg)
![実写表情カテゴリー 2/2](docs/gallery/images/expressions-02.jpg)

---

## 38種類の実写ミーム＆ネタ画像テンプレート（全6カテゴリー）

![実写ミームテンプレート一覧](docs/gallery/images/memes-overview.jpg)

---

## 7種類の吹き出しデザインと5言語の単一言語出力

![7種類の吹き出し形状](docs/gallery/images/bubbles.jpg)
![5言語の単一言語パック](docs/gallery/images/languages.jpg)

### 言語別100%単一言語スタンプセット（全日本語 / 全韓国語 / 全英語 / 全中国語）

![全日本語スタンプセット](docs/gallery/images/pack-ja.jpg)
![全韓国語スタンプセット](docs/gallery/images/pack-ko.jpg)
![全英語スタンプセット](docs/gallery/images/pack-en.jpg)
![全中国語スタンプセット](docs/gallery/images/pack-zh-CN.jpg)

---

## 23プラットフォームへの一括書き出しとSNSカバー生成

![SNS投稿用カバー素材](docs/gallery/images/platforms.jpg)

---

## クイックスタート（Quick Start）

```bash
# ワンクリックインストール（.venv作成＆Claude Code / Codexスキル自動リンク）
./install.sh
source .venv/bin/activate

# 環境チェック＆108種類のフォトスタイル / 108種類の2人ペアスタンプ一覧を確認
wechat-sticker-maker doctor
wechat-sticker-maker styles --region jp
wechat-sticker-maker duo --category yuri --language ja

# 1回のAI画像生成から日/中/英/韓の4言語別100%単一言語スタンプパックを同時出力
wechat-sticker-maker plan \
  --input photo.jpg \
  --output output/my-jp-pack \
  --mode both \
  --count 16 \
  --style real-jp-airy \
  --language auto \
  --languages ja,zh-CN,en,ko \
  --platforms line,instagram,telegram,wechat

wechat-sticker-maker generate --job output/my-jp-pack/job.json

# 2人ペア実写スタンプ（親友 / カップル / 百合）の生成
wechat-sticker-maker plan \
  --input personA.jpg \
  --partner personB.jpg \
  --duo-category yuri \
  --count 16 \
  --style real-jp-sakura-film \
  --language ja \
  --languages ja,zh-CN,en,ko \
  --output output/yuri-duo-pack

wechat-sticker-maker generate --job output/yuri-duo-pack/job.json
```

## テスト

```bash
pytest -v
python scripts/smoke_test.py
```

## ライセンス（License）

MIT License. 詳細は [`LICENSE`](LICENSE) をご覧ください。
