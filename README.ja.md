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
[![Real Person Only](https://img.shields.io/badge/Subject-100%25%20Real%20Person%20Portrait-ff69b4.svg)](#内蔵された26種類の実写フォトスタイル-referencesstyle-presetsjson)
[![Styles](https://img.shields.io/badge/Photographic%20Styles-26%20Presets%20(General%20%7C%20KR%20%7C%20JP%20%7C%20CN)-blue.svg)](#内蔵された26種類の実写フォトスタイル-referencesstyle-presetsjson)
[![Expressions & Memes](https://img.shields.io/badge/Catalog-132%20Expressions%20%7C%2038%20Memes%20%7C%20129%20Motions-success.svg)](#14カテゴリーの実写表情カタログ)
[![Languages](https://img.shields.io/badge/Single--Language%20Bubbles-zh--CN%20%7C%20zh--TW%20%7C%20en%20%7C%20ja%20%7C%20ko-orange.svg)](#7種類の吹き出しデザインと5言語の単一言語出力)
[![Platforms](https://img.shields.io/badge/Export-23%20Social%20Platforms-purple.svg)](#23プラットフォームへの一括書き出しとsnsカバー生成)

</div>

![実写スタンプショーケース](docs/gallery/images/hero.jpg)

> **[実写スタンプギャラリー全文を見る（全26スタイル / 10種類のアニメーションGIF / 38種類のミーム / 14種類の表情カテゴリー） → `docs/gallery/README.md`](docs/gallery/README.md)**

**対応する全23プラットフォーム**：LINE、Instagram、TikTok、X（旧Twitter）、Telegram、WhatsApp、Discord、Slack、KakaoTalk、iMessage、Signal、Viber、GIPHY、Facebook、WeChat（微信）、QQ、小紅書（RED）、Douyin、Weibo など。

---

## 主な特徴

- **全26種類の実写専用フォトスタイル（汎用 / 韓国系 / 日本系 / 中国系の4大シリーズ）**：デフォルトの `real-cutout` では美しい4pxの白フチ付きダイカットステッカーを生成。ライティングや色調、空気感のみを変化させ、本人の顔立ちを100%リアルに保ちます。
- **Codex AIの描画能力による本格マルチフレームアニメーション**：手を振る、ウインクする、首をかしげるといった動きを、Codex AIが `2×2` の4コマ連続アクションシート（`build_sprite_sheet_prompt`）として描き下ろします。Python側は非破壊の背景透過、体幹基準の位置合わせ、白フチ・文字入れ・エンコードのみを担当し、不自然な画像の引き伸ばしは一切行いません。
- **豊富な表情＆モーションライブラリ**：14カテゴリー・132種類の表情 × 129種類のモーション（`references/motion-library.json`）を収録し、すべての表情に4フレームのAI絵コンテを備えています。
- **38種類の実写ミーム＆ネタ画像テンプレート**：AI「思考中...」スピナー、「中国IP検知・接近禁止」、「これ以上喋ったらBAN」、「999秒間深く思考しました」、「レート制限超過」、「脳内404エラー」など38種類のテンプレート（`references/meme-templates.json`）を内蔵。
- **7種類の吹き出し＆厳格な単一言語ルール**：下部テロップ（`caption`）、吹き出し（`bubble`）、両方（`both`）、文字なし（`none`）に対応。日本語（`ja`）、韓国語（`ko`）、英語（`en`）、中国語簡体字・繁体字（`zh-CN`/`zh-TW`）を内蔵し、**1枚のスタンプには必ず1つの言語のみを表示（複数言語の混在を完全に防止）**します。
- **1つのマスターから23プラットフォームへ自動変換**：720pxの透過マスターから、各アプリの透過PNG / アニメーションGIF / APNG / WebP / WebM規格およびSNS投稿用カバー画像（9:16 ストーリー、3:4 カバー、3×3 グリッド）を自動出力します。

---

## 内蔵された26種類の実写フォトスタイル（`references/style-presets.json`）

**汎用 / 韓国系（KR） / 日本系（JP） / 中国系（CN）** の4シリーズに分かれており、CLIからシリーズ別に絞り込み可能です：`wechat-sticker-maker styles --region jp`。

![4大フォトスタイルシリーズ比較](docs/gallery/images/four-series.jpg)

![全26種類の実写スタンプスタイル一覧](docs/gallery/images/styles-overview.jpg)

### 汎用シリーズ（6）
| スタイルID (`--style`) | 名称 | 特徴 |
|---|---|---|
| `real-cutout` | **実写ポートレート切り抜き（デフォルト）** | 本人のリアルな顔立ち・肌質を維持＋4pxの白フチ |
| `real-bobblehead` | 実写デフォルメ頭身ステッカー | リアルな顔立ち＋遊び心のある大きめ頭身バランス＆5px白フチ |
| `real-street-cool` | ストリートフラッシュスナップ | 雑誌スナップ風の直射フラッシュとハイコントラストな陰影 |
| `real-vintage-ccd` | Y2K ヴィンテージCCDデジカメ | 2000年代初頭の温かみのあるCCDコンデジフラッシュ質感 |
| `real-work-emo` | 社会人リアル日常スナップ | 仕事疲れ・虚無感・限界リアクションをリアルに切り抜き |
| `real-high-contrast` | 白黒ハイコントラストミーム | 定番のモノクロ高コントラスト実写ミーム風 |

### 韓国系シリーズ（`韩系` · 7）
![韓国系 7スタイル](docs/gallery/images/series-kr.jpg)

| スタイルID | 名称 | 特徴 |
|---|---|---|
| `real-kr-idol-selfie` | K-POPアイドルセルフィー | リングライトの瞳の輝き、ツヤ感グラデリップ、指ハート＆ウインク |
| `real-kr-glass-skin` | 韓国水光肌（グラススキン） | 透明感あふれるツヤ肌と柔らかなパステルスタジオ照明 |
| `real-kr-photocard` | K-POPトレーディングカード風 | パステルピンク＆アイスブルーのリムライト、推し活トレカ質感 |
| `real-kr-cafe-film` | ソウルカフェ・ウォームフィルム | 窓辺の自然光、ミルクティーベージュの色調と繊細な粒子感 |
| `real-kr-drama` | 韓国ドラマヒロイン逆光ムード | 映画のような浅い被写界深度と温かいゴールデンアワーの逆光 |
| `real-kr-variety` | 韓国バラエティ番組テロップ風 | 豊かなリアクション＋カラフルな縁取りバラエティ字幕 |
| `real-purikura` | 韓国「人生4カット」フォトブース | クリーンなパステル照明とピンクホワイトのステッカー枠 |

### 日本系シリーズ（`日系` · 6）
![日本系 6スタイル](docs/gallery/images/series-jp.jpg)

| スタイルID | 名称 | 特徴 |
|---|---|---|
| `real-jp-airy` | 日系エアリー透明感 | わずかにハイキーで低コントラストなシアン・ピンク系の自然光 |
| `real-jp-fuji-film` | 富士フイルム・ノスタルジック調 | 青みがかったシャドウと温かみのある肌色、繊細な35mmフィルム粒子 |
| `real-jp-purikura` | 東京プリクラ（プリクラ）風 | 明るい美白ライティングとパステルフレーム（※目の大きさは不自然に拡大しません） |
| `real-jp-summer` | 鎌倉サマーバックライト | 夏の日差しに透ける髪と爽やかな海風の空気感 |
| `real-jp-harajuku` | 原宿ストリートスナップ | ポップな直焚きフラッシュと鮮やかなカラーコントラスト |
| `real-jp-showa` | 80年代昭和レトロフィルム | 温かく色褪せたアンバーの光滲みとヴィンテージなソフトフォーカス |

### 中国系シリーズ（`中式` · 7）
![中国系 7スタイル](docs/gallery/images/series-cn.jpg)

| スタイルID | 名称 | 特徴 |
|---|---|---|
| `real-cn-new-chinese` | ネオチャイニーズ（新中式）写真 | 柔らかな暖色ライトと朱赤・ゴールドの洗練されたアクセント |
| `real-cn-hk-retro` | 90年代香港シネマネオン | ウォン・カーウァイ映画風の赤とティールのネオンリムライト |
| `real-cn-xhs-vibe` | RED（小紅書）クリーミームード | 柔らかい拡散光と上品な低彩度トーン |
| `real-cn-douyin` | スタジオビューティーリングライト | くっきりしたキャッチライトと元気な表情（輪郭は本人のまま維持） |
| `real-cn-studio-retro` | 90年代レトロ写真館風 | どこか懐かしい90年代写真館のソフトフォーカス質感 |
| `real-cn-tw-youth` | 台湾青春インディーフィルム | 午後の暖かい日差しとノスタルジックなグリーンゴールド調 |
| `real-variety-meme` | バラエティ番組ポップ文字スタンプ | 鮮やかな黄色×黒フチ文字を組み合わせたリアクションスタンプ |

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

---

## 23プラットフォームへの一括書き出しとSNSカバー生成

![SNS投稿用カバー素材](docs/gallery/images/platforms.jpg)

---

## クイックスタート（Quick Start）

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# 環境チェック＆日本系（jp）スタイル一覧の確認
wechat-sticker-maker doctor
wechat-sticker-maker styles
wechat-sticker-maker styles --region jp

# 日本語（ja）と日系エアリー透明感スタイルで16個のスタンプパックを計画・生成
wechat-sticker-maker plan \
  --input photo.jpg \
  --output output/my-jp-pack \
  --mode both \
  --count 16 \
  --style real-jp-airy \
  --language ja \
  --platforms line,instagram,telegram,wechat

wechat-sticker-maker generate --job output/my-jp-pack/job.json

# 単発の実写ミームGIFを素早く生成
wechat-sticker-maker meme -t claude -i photo.jpg --language ja -o output/thinking.gif
wechat-sticker-maker meme -t m02_china_ip_blocked -i photo.jpg --language ja -o output/ip_blocked.gif
wechat-sticker-maker meme -t m03_ban_threat -i photo.jpg --language ja -o output/ban.gif
```

## テスト

```bash
pytest -v
python scripts/smoke_test.py
```

## ライセンス（License）

MIT License. 詳細は [`LICENSE`](LICENSE) をご覧ください。
