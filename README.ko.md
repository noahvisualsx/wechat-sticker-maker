<p align="right">
  <strong>Language:</strong>
  <a href="README.md"><b>简体中文</b></a> |
  <a href="README.en.md"><b>English</b></a> |
  <a href="README.ko.md"><b>한국어</b></a> |
  <a href="README.ja.md"><b>日本語</b></a>
</p>

# WeChat Sticker Maker · 실사 인물 전용 AI 이모티콘 & 짤 생성 엔진

> **Your Face, Your Vibe, Your Sticker Pack.**  
> **실제 인물 사진(`human-portrait`)**만을 위해 설계된 올인원 ChatGPT / Codex 스킬 및 Python 이모티콘·짤 생성 엔진입니다. 본인의 실제 이목구비, 얼굴형, 피부결, 헤어스타일과 착장을 그대로 유지하며 **절대 2D 애니메이션이나 어색한 만화 캐릭터로 변형하지 않습니다.** 한 번의 생성으로 위챗(WeChat), 카카오톡(KakaoTalk), 라인(LINE), 인스타그램, 틱톡 등 **전 세계 23개 메신저 및 소셜 플랫폼** 규격으로 동시 내보내기를 지원합니다.

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Real Person Only](https://img.shields.io/badge/Subject-100%25%20Real%20Person%20Portrait-ff69b4.svg)](#26가지-실사-전용-사진-스타일-referencesstyle-presetsjson)
[![Styles](https://img.shields.io/badge/Photographic%20Styles-26%20Presets%20(General%20%7C%20KR%20%7C%20JP%20%7C%20CN)-blue.svg)](#26가지-실사-전용-사진-스타일-referencesstyle-presetsjson)
[![Expressions & Memes](https://img.shields.io/badge/Catalog-132%20Expressions%20%7C%2038%20Memes%20%7C%20129%20Motions-success.svg)](#14대-실사-표정-카테고리)
[![Languages](https://img.shields.io/badge/Single--Language%20Bubbles-zh--CN%20%7C%20zh--TW%20%7C%20en%20%7C%20ja%20%7C%20ko-orange.svg)](#7가지-말풍선-디자인--5개국어-단일-언어-엄격-분리)
[![Platforms](https://img.shields.io/badge/Export-23%20Social%20Platforms-purple.svg)](#23개-소셜-플랫폼-자동-변환-및-커버-생성)

</div>

![실사 이모티콘 쇼케이스](docs/gallery/images/hero.jpg)

> **[전체 실사 이모티콘 갤러리 보기 (26종 스타일 / 10종 모션 GIF / 38종 밈 템플릿 / 14개 표정 분류) → `docs/gallery/README.md`](docs/gallery/README.md)**

**지원되는 23개 플랫폼**: 카카오톡(KakaoTalk), 라인(LINE), 인스타그램(Instagram), 틱톡(TikTok), 텔레그램(Telegram), 왓츠앱(WhatsApp), 디스코드(Discord), 슬랙(Slack), iMessage, Signal, Viber, GIPHY, X(트위터), 페이스북, 위챗(WeChat), QQ, 샤오홍슈(RED), 더우인, 웨이보 등.

---

## 핵심 기능

- **26가지 실사 전용 사진 스타일 (기본 / 한국 감성 / 일본 감성 / 중국 감성 4대 시리즈)**: 기본값 `real-cutout`으로 깔끔한 4px 다이컷 화이트 스티커 테두리를 생성합니다. 조명과 색감, 분위기만 바꾸며 실제 얼굴을 만화로 왜곡하지 않습니다.
- **Codex AI 네이티브 드로잉 기반 진짜 모션 GIF**: 손 흔들기, 윙크, 고개 갸웃거리기 등 모든 동작을 Codex AI가 `2×2` 4컷 연속 모션 시트(`build_sprite_sheet_prompt`)로 직접 그리며, Python은 정밀 누끼(배경 제거), 몸통 중심선 정렬, 테두리 및 자막 합성만 수행합니다.
- **방대한 표정 & 동작 라이브러리**: 14개 카테고리 132종 표정 × 129종 모션 라이브러리(`references/motion-library.json`), 모든 표정에 4프레임 AI 스토리보드 내장.
- **38종 실사 밈(Meme) & 추상 짤 템플릿**: AI "생각 중..." 로딩 스피너, "접근 금지 경고", "한 마디만 더 하면 차단", "999초 동안 깊이 생각함", "요청 횟수 초과", "뇌 과부하(404)" 등 38가지 밈 템플릿(`references/meme-templates.json`) 제공.
- **말풍선 & 단일 언어 엄격 분리**: 하단 자막(`caption`), 말풍선(`bubble`), 동시 표시(`both`), 텍스트 없음(`none`) 및 7가지 말풍선 모양 지원. 한국어(`ko`), 중국어 간체/번체(`zh-CN`/`zh-TW`), 영어(`en`), 일본어(`ja`)를 지원하며 **하나의 스티커에는 반드시 하나의 언어만 표기(이중 언어 혼용 금지)**합니다.
- **원스톱 23개 플랫폼 자동 패키징**: 720px 고해상도 마스터 본을 한 번 생성한 뒤 각 메신저의 규격·용량 제한에 맞춘 파일과 SNS 업로드용 카드(인스타 스토리 9:16, 피드 3:4 커버, 3×3 그리드)를 자동 출력합니다.

---

## 26가지 실사 전용 사진 스타일 (`references/style-presets.json`)

**기본 / 한국 감성(KR) / 일본 감성(JP) / 중국 감성(CN)** 4개 시리즈로 구성되며, CLI에서 시리즈별 조회가 가능합니다: `wechat-sticker-maker styles --region kr`.

![4대 실사 사진 스타일 시리즈 비교](docs/gallery/images/four-series.jpg)

![26종 실사 스티커 스타일 한눈에 보기](docs/gallery/images/styles-overview.jpg)

### 기본 시리즈 (6)
| 스타일 ID (`--style`) | 이름 | 특징 |
|---|---|---|
| `real-cutout` | **실사 화보 누끼 스티커 (기본값)** | 실제 이목구비와 피부결 유지 + 4px 화이트 다이컷 테두리 |
| `real-bobblehead` | 실사 대두 캐리커처 스티커 | 실제 얼굴 + 귀여운 대두 비율 & 5px 페이퍼컷 테두리 |
| `real-street-cool` | 매거진 스트릿 직광 스냅 | 패션 화보 스타일 직광 플래시와 강렬한 대비 |
| `real-vintage-ccd` | Y2K 빈티지 CCD 디카 | 2000년대 초반 따뜻한 CCD 디지털 카메라 감성 |
| `real-work-emo` | 직장인 리얼 공감 짤 | 영혼 가출 / 야근에 지친 리얼한 표정 포착 |
| `real-high-contrast` | 고대비 흑백 밈 스티커 | 클래식 흑백 고대비 실사 짤 스타일 |

### 한국 감성 시리즈 (`韩系` · 7)
![한국 감성 7종 스타일](docs/gallery/images/series-kr.jpg)

| 스타일 ID | 이름 | 특징 |
|---|---|---|
| `real-kr-idol-selfie` | K-POP 아이돌 셀카 | 부드러운 링라이트 눈망울, 과즙미 글로시 립, 볼하트/윙크 |
| `real-kr-glass-skin` | 한국식 물광 유리알 피부 | 맑고 투명한 물광 피부 표현과 내추럴 파스텔 스튜디오 조명 |
| `real-kr-photocard` | K-POP 아이돌 포토카드 | 파스텔 핑크·아이스블루 림라이트, 최애 포카 감성 |
| `real-kr-cafe-film` | 서울 카페 감성 필름 | 창가 자연광, 따뜻한 라떼·베이지 톤과 은은한 필름 입자 |
| `real-kr-drama` | K-드라마 주인공 역광 무드 | 시네마틱 아웃포커싱과 따뜻한 골든아워 역광 효과 |
| `real-kr-variety` | 한국 예능 자막 리액션 짤 | 런닝맨 스타일의 생생한 리액션 + 컬러풀한 예능 자막 테두리 |
| `real-purikura` | 한국 인생네컷 포토부스 | 깔끔한 파스텔 스튜디오 조명과 핑크 화이트 스티커 라인 |

### 일본 감성 시리즈 (`日系` · 6)
![일본 감성 6종 스타일](docs/gallery/images/series-jp.jpg)

| 스타일 ID | 이름 | 특징 |
|---|---|---|
| `real-jp-airy` | 일본 에이리(Airy) 투명 감성 | 살짝 노출을 높인 저대비 시안·핑크빛 맑은 자연광 |
| `real-jp-fuji-film` | 일본 후지필름 포트라 | 청록빛 섀도우와 따뜻한 피부톤, 섬세한 35mm 필름 그레인 |
| `real-jp-purikura` | 도쿄 프리쿠라(プリクラ) 스티커 | 화사한 뷰티 조명과 카와이 파스텔 프레임 (눈 크기 왜곡 없음) |
| `real-jp-summer` | 가마쿠라 여름 역광 스냅 | 햇살에 반짝이는 머릿결과 청량한 여름 바람 무드 |
| `real-jp-harajuku` | 하라주쿠 스트릿 스냅 | 경쾌한 직광 플래시와 비비드한 컬러 포인트 |
| `real-jp-showa` | 80년대 쇼와 레트로 필름 | 따뜻하게 바랜 호박색 빛 번짐과 80년대 빈티지 소프트 포커스 |

### 중국 감성 시리즈 (`中式` · 7)
![중국 감성 7종 스타일](docs/gallery/images/series-cn.jpg)

| 스타일 ID | 이름 | 특징 |
|---|---|---|
| `real-cn-new-chinese` | 네오 차이니즈 고풍 포트레이트 | 은은한 등불 조명과 주홍·골드 포인트의 우아한 분위기 |
| `real-cn-hk-retro` | 90년대 홍콩 영화 네온 필름 | 왕가위 영화풍 레드·틸(Teal) 네온 조명과 깊은 필름 질감 |
| `real-cn-xhs-vibe` | 샤오홍슈 크리미 무드 | 부드러운 확산광과 세련된 저채도 크림 톤 |
| `real-cn-douyin` | 스튜디오 하이키 뷰티 라이트 | 선명한 캐치라이트와 통통 튀는 표정 (실제 얼굴형 그대로 유지) |
| `real-cn-studio-retro` | 90년대 레트로 사진관 | 유머러스한 90년대 옛날 사진관 소프트 포커스 감성 |
| `real-cn-tw-youth` | 대만 청춘 인디 필름 | 따뜻한 오후 햇살과 그리운 그린·골드 필름 톤 |
| `real-variety-meme` | 버라이어티 컬러 자막 짤 | 강렬한 옐로우·블랙 포인트 자막이 결합된 리액션 스티커 |

---

## Codex AI 4프레임 모션 GIF 쇼케이스

![실사 모션 GIF 쇼케이스](docs/gallery/images/animated-showcase.gif)

---

## 14대 실사 표정 카테고리

![실사 표정 분류 1/2](docs/gallery/images/expressions-01.jpg)
![실사 표정 분류 2/2](docs/gallery/images/expressions-02.jpg)

---

## 38종 실사 밈(Meme) & 추상 짤 템플릿 (6대 분류)

![실사 밈 템플릿 총람](docs/gallery/images/memes-overview.jpg)

---

## 7가지 말풍선 디자인 & 5개국어 단일 언어 엄격 분리

![7가지 말풍선 모양](docs/gallery/images/bubbles.jpg)
![5개국어 단일 언어 분리](docs/gallery/images/languages.jpg)

---

## 23개 소셜 플랫폼 자동 변환 및 커버 생성

![소셜 플랫폼 배포용 커버 에셋](docs/gallery/images/platforms.jpg)

---

## 빠른 시작 (Quick Start)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# 환경 점검 및 한국 감성(kr) 스타일 목록 확인
wechat-sticker-maker doctor
wechat-sticker-maker styles
wechat-sticker-maker styles --region kr

# 한국어(ko) 말풍선과 한국 아이돌 셀카 스타일로 이모티콘 16종 생성 계획 수립
wechat-sticker-maker plan \
  --input photo.jpg \
  --output output/my-kr-pack \
  --mode both \
  --count 16 \
  --style real-kr-idol-selfie \
  --language ko \
  --platforms kakaotalk,instagram,telegram,wechat

wechat-sticker-maker generate --job output/my-kr-pack/job.json

# 실사 밈(짤) 단건 빠른 생성
wechat-sticker-maker meme -t claude -i photo.jpg --language ko -o output/thinking.gif
wechat-sticker-maker meme -t m02_china_ip_blocked -i photo.jpg --language ko -o output/ip_blocked.gif
wechat-sticker-maker meme -t m03_ban_threat -i photo.jpg --language ko -o output/ban.gif
```

## 테스트

```bash
pytest -v
python scripts/smoke_test.py
```

## 라이선스 (License)

MIT License. 자세한 내용은 [`LICENSE`](LICENSE) 파일을 참고하세요.
