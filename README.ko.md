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
[![Real Person Only](https://img.shields.io/badge/Subject-100%25%20Real%20Person%20Portrait-ff69b4.svg)](#108가지-실사-전용-사진-스타일-referencesstyle-presetsjson)
[![Styles](https://img.shields.io/badge/Photographic%20Styles-108%20Presets%20(General%20%7C%20KR%20%7C%20JP%20%7C%20CN)-blue.svg)](#108가지-실사-전용-사진-스타일-referencesstyle-presetsjson)
[![Expressions & Memes](https://img.shields.io/badge/Catalog-132%20Expressions%20%7C%2038%20Memes%20%7C%20129%20Motions-success.svg)](#14대-실사-표정-카테고리)
[![Languages](https://img.shields.io/badge/Single--Language%20Bubbles-zh--CN%20%7C%20zh--TW%20%7C%20en%20%7C%20ja%20%7C%20ko-orange.svg)](#7가지-말풍선-디자인--5개국어-단일-언어-엄격-분리)
[![Platforms](https://img.shields.io/badge/Export-23%20Social%20Platforms-purple.svg)](#23개-소셜-플랫폼-자동-변환-및-커버-생성)

</div>

![실사 이모티콘 쇼케이스](docs/gallery/images/hero.jpg)

> **[전체 실사 이모티콘 갤러리 보기 (108종 스타일 / 10종 모션 GIF / 38종 밈 템플릿 / 14개 표정 분류) → `docs/gallery/README.md`](docs/gallery/README.md)**

**지원되는 23개 플랫폼**: 카카오톡(KakaoTalk), 라인(LINE), 인스타그램(Instagram), 틱톡(TikTok), 텔레그램(Telegram), 왓츠앱(WhatsApp), 디스코드(Discord), 슬랙(Slack), iMessage, Signal, Viber, GIPHY, X(트위터), 페이스북, 위챗(WeChat), QQ, 샤오홍슈(RED), 더우인, 웨이보 등.

---

## 핵심 기능

- **108가지 실사 전용 사진 스타일 (기본 / 한국 감성 / 일본 감성 / 중국 감성 4대 시리즈)**: 기본값 `real-cutout`으로 깔끔한 4px 다이컷 화이트 스티커 테두리를 생성합니다. 조명과 색감, 분위기만 바꾸며 실제 얼굴을 만화로 왜곡하지 않습니다.
- **Codex AI 네이티브 드로잉 기반 진짜 모션 GIF**: 손 흔들기, 윙크, 고개 갸웃거리기 등 모든 동작을 Codex AI가 `2×2` 4컷 연속 모션 시트(`build_sprite_sheet_prompt`)로 직접 그리며, Python은 정밀 누끼(배경 제거), 몸통 중심선 정렬, 테두리 및 자막 합성만 수행합니다.
- **방대한 표정 & 동작 라이브러리**: 14개 카테고리 132종 표정 × 129종 모션 라이브러리(`references/motion-library.json`), 모든 표정에 4프레임 AI 스토리보드 내장.
- **38종 실사 밈(Meme) & 추상 짤 템플릿**: AI "생각 중..." 로딩 스피너, "접근 금지 경고", "한 마디만 더 하면 차단", "999초 동안 깊이 생각함", "요청 횟수 초과", "뇌 과부하(404)" 등 38가지 밈 템플릿(`references/meme-templates.json`) 제공.
- **말풍선 & 단일 언어 엄격 분리**: 하단 자막(`caption`), 말풍선(`bubble`), 동시 표시(`both`), 텍스트 없음(`none`) 및 7가지 말풍선 모양 지원. 한국어(`ko`), 중국어 간체/번체(`zh-CN`/`zh-TW`), 영어(`en`), 일본어(`ja`)를 지원하며 **하나의 스티커에는 반드시 하나의 언어만 표기(이중 언어 혼용 금지)**합니다.
- **원스톱 23개 플랫폼 자동 패키징**: 720px 고해상도 마스터 본을 한 번 생성한 뒤 각 메신저의 규격·용량 제한에 맞춘 파일과 SNS 업로드용 카드(인스타 스토리 9:16, 피드 3:4 커버, 3×3 그리드)를 자동 출력합니다.

---

## 108가지 실사 전용 사진 스타일 (`references/style-presets.json`)

**기본(18종) / 한국 감성(30종) / 일본 감성(30종) / 중국 감성(30종)** 총 108가지 실사 전용 사진 스타일로 구성되며, CLI에서 시리즈별 조회가 가능합니다: `wechat-sticker-maker styles --region kr`.

![4대 실사 사진 스타일 시리즈 비교](docs/gallery/images/four-series.jpg)

![실사 스티커 스타일 한눈에 보기](docs/gallery/images/styles-overview.jpg)

### 기본 시리즈 (18종)
| # | 스타일 ID (`--style`) | 스타일 이름 | 조명 프로필 & 프리셋 |
|---|---|---|---|
| 1 | `real-cutout` | **실사 화보 누끼 스티커 (기본값)** | `studio-portrait` · 真人写真抠图贴纸 |
| 2 | `real-bobblehead` | **실사 대두 캐리커처 스티커** | `bright-studio` · 真人搞怪大头贴 |
| 3 | `real-street-cool` | **매거진 스트릿 직광 스냅** | `editorial-flash` · 真人潮酷街拍贴纸 |
| 4 | `real-vintage-ccd` | **Y2K 빈티지 CCD 디카** | `ccd-warm-flash` · 真人复古CCD胶片贴纸 |
| 5 | `real-work-emo` | **직장인 리얼 공감 짤** | `natural-candid` · 真人打工人纪实梗图 |
| 6 | `real-high-contrast` | **고대비 흑백 밈 스티커** | `high-contrast-studio` · 真人黑白高反差梗图 |
| 7 | `real-polaroid-instant` | **폴라로이드 SX-70 즉석사진** | `polaroid-instant` · 真人拍立得即时相纸 |
| 8 | `real-fisheye-y2k` | **Y2K 16mm 어안렌즈 클로즈업** | `fisheye-y2k-flash` · 真人千禧鱼眼大头贴 |
| 9 | `real-paparazzi-flash` | **야간 파파라치 직광 플래시** | `paparazzi-direct-flash` · 真人狗仔直闪抓拍 |
| 10 | `real-golden-hour` | **골든아워 노을 역광** | `golden-hour-sunset` · 真人落日夕阳逆光 |
| 11 | `real-blue-hour` | **블루아워 새벽 시네마틱** | `blue-hour-cinematic` · 真人蓝调时刻电影感 |
| 12 | `real-cyber-neon` | **사이버펑크 듀얼 네온 야경** | `cyber-dual-neon` · 真人赛博霓虹夜景 |
| 13 | `real-film-kodak-gold` | **코닥 골드 200 따뜻한 필름** | `kodak-gold-200` · 真人柯达Gold200胶片 |
| 14 | `real-film-cinestill-800t` | **씨네스틸 800T 텅스텐 필름** | `cinestill-800t` · 真人CineStill钨丝灯胶片 |
| 15 | `real-vogue-editorial` | **하이패션 매거진 화보 조명** | `vogue-rembrandt-studio` · 真人高定时尚杂志封面 |
| 16 | `real-french-effortless` | **파리지앵 오후 자연광 스냅** | `french-afternoon-sun` · 真人法式慵懒午后写真 |
| 17 | `real-american-yearbook` | **90년대 하이틴 졸업앨범 스튜디오** | `retro-yearbook-studio` · 真人美式复古毕业年鉴 |
| 18 | `real-thermal-ir` | **페스티벌 UV 듀오톤 컬러 조명** | `uv-festival-duo` · 真人潮流伪彩视觉 |

### 한국 감성 시리즈 (`韩系` · 30종)
![한국 감성 스타일 프리뷰](docs/gallery/images/series-kr.jpg)

| # | 스타일 ID (`--style`) | 스타일 이름 | 조명 프로필 & 프리셋 |
|---|---|---|---|
| 1 | `real-purikura` | **한국 인생네컷 포토부스** | `creamy-kbeauty` · 韩系人生四格大头贴 |
| 2 | `real-kr-idol-selfie` | **K-POP 아이돌 셀카** | `kpop-ringlight` · 韩系爱豆自拍 |
| 3 | `real-kr-glass-skin` | **한국식 물광 유리알 피부** | `kbeauty-dewy` · 韩系水光肌清透 |
| 4 | `real-kr-photocard` | **K-POP 아이돌 포토카드** | `pastel-gradient-studio` · 韩系爱豆小卡 |
| 5 | `real-kr-cafe-film` | **서울 카페 감성 필름** | `window-daylight` · 韩系咖啡馆胶片 |
| 6 | `real-kr-drama` | **K-드라마 주인공 역광 무드** | `kdrama-backlight` · 韩剧主角氛围 |
| 7 | `real-kr-variety` | **한국 예능 자막 리액션 짤** | `kvariety-highkey` · 韩综字幕斗图 |
| 8 | `real-kr-music-bank` | **음악방송 엔딩요정 스포트라이트** | `kpop-stage-ending` · 韩系打歌舞台Ending妖精 |
| 9 | `real-kr-fansign-soft` | **아이돌 팬사인회 대포 카메라 소프트광** | `kr-fansign-telephoto` · 韩系签售会奶油柔光 |
| 10 | `real-kr-airport-snap` | **인천공항 출국길 자연광 스냅** | `kr-airport-daylight` · 韩系仁川机场路透街拍 |
| 11 | `real-kr-hongdae-street` | **홍대 스트릿 패션 스냅** | `kr-hongdae-overcast` · 韩系弘大街头潮拍 |
| 12 | `real-kr-seongsu-industrial` | **성수동 인더스트리얼 채광 화보** | `kr-seongsu-concrete` · 韩系圣水洞工业风写真 |
| 13 | `real-kr-hannam-oldmoney` | **한남동 올드머니 캐시미어 무드** | `kr-hannam-cashmere` · 韩系汉南洞千金氛围 |
| 14 | `real-kr-apgujeong-glam` | **압구정 나이트 직광 글램 스냅** | `kr-apgujeong-flash` · 韩系狎鸥亭闪光夜拍 |
| 15 | `real-kr-jeju-breeze` | **제주도 바닷바람 청량 필름** | `kr-jeju-coastal-sun` · 韩系济州岛海风胶片 |
| 16 | `real-kr-hanok-sunlight` | **북촌 한옥마을 따뜻한 햇살** | `kr-hanok-warm-wood` · 韩系北村韩屋暖阳 |
| 17 | `real-kr-winter-snow` | **첫눈 오는 날 겨울 드라마 무드** | `kr-first-snow-soft` · 韩系初雪围巾恋歌 |
| 18 | `real-kr-cherry-blossom` | **여의도 벚꽃길 봄날 로맨스** | `kr-yeouido-blossom` · 韩系汝矣岛樱花柔光 |
| 19 | `real-kr-rainy-pocha` | **비 오는 밤 포장마차 감성 조명** | `kr-pocha-warm-amber` · 韩系雨夜布帐马车 |
| 20 | `real-kr-high-teen` | **하이틴 캠퍼스 하이키 팝 조명** | `kr-highteen-pop` · 韩系High-Teen复古校园 |
| 21 | `real-kr-y2k-metallic` | **Y2K 실버 메탈릭 걸그룹 컨셉** | `kr-y2k-silver-frost` · 韩系Y2K千禧银光 |
| 22 | `real-kr-balletcore` | **한국식 발레코어 펄 핑크 소프트** | `kr-balletcore-pearl` · 韩系芭蕾风柔粉写真 |
| 23 | `real-kr-clean-fit` | **강남 클린핏 화이트 호리존 스튜디오** | `kr-cleanfit-cyclorama` · 韩系Clean-Fit极简白棚 |
| 24 | `real-kr-id-photo` | **서울 시그니처 증명사진 스튜디오** | `kr-id-butterfly-light` · 韩系最美证件照精修 |
| 25 | `real-kr-high-angle-booth` | **하이앵글 항공샷 포토부스** | `kr-high-angle-booth` · 韩系俯拍高角度四格 |
| 26 | `real-kr-bw-fourcut` | **홍대 흑백 셀프사진관 실버필름** | `kr-mono-photobooth` · 韩系黑白胶片四格 |
| 27 | `real-kr-practice-mirror` | **연습실 거울 셀카 데일리 라이트** | `kr-practice-room-bright` · 韩系练习室对镜自拍 |
| 28 | `real-kr-convenience-night` | **심야 편의점 형광등 감성 스냅** | `kr-convenience-fluorescent` · 韩系深夜便利店霓虹 |
| 29 | `real-kr-magazine-dazed` | **서울 컨셉추얼 매거진 화보 조명** | `kr-avant-garde-gel` · 韩系先锋画报冷冽光 |
| 30 | `real-kr-webtoon-real` | **웹툰 실사화 주인공 등장 역광** | `kr-webtoon-hero-glow` · 韩系漫改主角神颜光 |

### 일본 감성 시리즈 (`日系` · 30종)
![일본 감성 스타일 프리뷰](docs/gallery/images/series-jp.jpg)

| # | 스타일 ID (`--style`) | 스타일 이름 | 조명 프로필 & 프리셋 |
|---|---|---|---|
| 1 | `real-jp-airy` | **일본 에이리(Airy) 투명 감성** | `airy-overexposed` · 日系空气感清新 |
| 2 | `real-jp-fuji-film` | **일본 후지필름 포트라** | `fuji-film` · 日系富士胶片 |
| 3 | `real-jp-purikura` | **도쿄 프리쿠라(プリクラ) 스티커** | `purikura-booth` · 日系大头贴プリクラ |
| 4 | `real-jp-summer` | **가마쿠라 여름 역광 스냅** | `summer-backlight` · 日系夏日逆光 |
| 5 | `real-jp-harajuku` | **하라주쿠 스트릿 스냅** | `street-flash` · 日系原宿街头 |
| 6 | `real-jp-showa` | **80년대 쇼와 레트로 필름** | `showa-retro` · 日系昭和复古 |
| 7 | `real-jp-rinko-pastel` | **카와우치 린코풍 하이키 파스텔** | `jp-rinko-highkey-pastel` · 日系川内伦子风淡彩 |
| 8 | `real-jp-hideaki-clean` | **하마다 히데아키풍 청량 중형필름** | `jp-hideaki-medium-format` · 日系滨田英明风清透 |
| 9 | `real-jp-moriyama-bw` | **모리야마 다이도풍 거친 흑백 스트릿** | `jp-moriyama-gritty-bw` · 日系森山大道粗颗粒黑白 |
| 10 | `real-jp-ninagawa-vivid` | **니나가와 미카풍 고채도 플라워 조명** | `jp-ninagawa-saturated` · 日系蜷川实花浓郁花影 |
| 11 | `real-jp-shibuya-neon` | **시부야 스크램블 야간 네온 스냅** | `jp-shibuya-night-neon` · 日系涩谷十字路口霓虹 |
| 12 | `real-jp-shimokita-vintage` | **시모키타자와 빈티지숍 웜필름** | `jp-shimokita-warm-film` · 日系下北泽古着胶片 |
| 13 | `real-jp-daikanyama-morning` | **다이칸야마 아침 서점 창가 채광** | `jp-daikanyama-morning` · 日系代官山晨光书店 |
| 14 | `real-jp-ginza-luxury` | **긴자 나이트 샴페인 골드 보케** | `jp-ginza-champagne-glow` · 日系银座夜色流光 |
| 15 | `real-jp-kyoto-komorebi` | **교토 정원 나뭇잎 햇살(코모레비)** | `jp-kyoto-komorebi` · 日系京都木漏日和风 |
| 16 | `real-jp-hokkaido-snow` | **홋카이도 러브레터 설원 반사광** | `jp-hokkaido-snow-bounce` · 日系北海道情书雪景 |
| 17 | `real-jp-okinawa-sun` | **오키나와 한여름 바다소금 청량광** | `jp-okinawa-sea-salt` · 日系冲绳盛夏海盐 |
| 18 | `real-jp-sakura-film` | **메구로강 벚꽃 시즌 핑크 필름** | `jp-sakura-spring-film` · 日系樱花季春光胶片 |
| 19 | `real-jp-autumn-icho` | **메이지진구 은행나무 가로수길 가을빛** | `jp-autumn-ginkgo-gold` · 日系银杏大道秋日暖光 |
| 20 | `real-jp-rainy-hydrangea` | **가마쿠라 장마철 수국 블루 무드** | `jp-kamakura-rainy-blue` · 日系镰仓梅雨紫阳花 |
| 21 | `real-jp-onsen-steam` | **하코네 온천 료칸 따뜻한 김 서림** | `jp-onsen-warm-mist` · 日系温泉旅馆暖雾 |
| 22 | `real-jp-izakaya-warm` | **심야식당 이자카야 제등 조명** | `jp-izakaya-lantern` · 日系深夜食堂居酒屋 |
| 23 | `real-jp-kissaten-retro` | **쇼와 킷사텐 호박색 테이블 램프** | `jp-kissaten-amber` · 日系纯喫茶昭和咖啡 |
| 24 | `real-jp-school-rooftop` | **청춘 드라마 학교 옥상 맑은 하늘** | `jp-rooftop-clear-sky` · 日系青春天台晴空 |
| 25 | `real-jp-matsuri-fireworks` | **여름 축제 선향불꽃(불꽃놀이) 미광** | `jp-sparkler-warm-glow` · 日系夏日祭花火微光 |
| 26 | `real-jp-nonno-magazine` | **일본 패션잡지 스위트 스튜디오** | `jp-sweet-magazine-studio` · 日系甜美日杂画报 |
| 27 | `real-jp-popeye-cityboy` | **도쿄 시티보이 매거진 자연광 스냅** | `jp-popeye-cityboy-sun` · 日系CityBoy街头画报 |
| 28 | `real-jp-utsurundesu` | **후지 우츠룬데스 일회용 필름카메라** | `jp-quicksnap-disposable` · 日系写ルンです一次性胶片 |
| 29 | `real-jp-drama-subtitle` | **일드 골든타임 명장면 스틸컷** | `jp-prime-drama-cinematic` · 日剧黄金档电影感剧照 |
| 30 | `real-jp-variety-telop` | **일본 예능 강렬한 컬러 자막 리액션** | `jp-variety-tv-bright` · 日综夸张大字报斗图 |

### 중국 감성 시리즈 (`中式` · 30종)
![중국 감성 스타일 프리뷰](docs/gallery/images/series-cn.jpg)

| # | 스타일 ID (`--style`) | 스타일 이름 | 조명 프로필 & 프리셋 |
|---|---|---|---|
| 1 | `real-variety-meme` | **버라이어티 컬러 자막 짤** | `high-key-tv` · 真人综艺花字斗图 |
| 2 | `real-cn-new-chinese` | **네오 차이니즈 고풍 포트레이트** | `oriental-warm` · 新中式国风写真 |
| 3 | `real-cn-hk-retro` | **90년대 홍콩 영화 네온 필름** | `hk-neon-film` · 港风复古胶片 |
| 4 | `real-cn-xhs-vibe` | **샤오홍슈 크리미 무드** | `creamy-soft` · 小红书氛围感 |
| 5 | `real-cn-douyin` | **스튜디오 하이키 뷰티 라이트** | `ringlight-bright` · 抖音网红美颜 |
| 6 | `real-cn-studio-retro` | **90년대 레트로 사진관** | `retro-studio-softfocus` · 复古影楼风 |
| 7 | `real-cn-tw-youth` | **대만 청춘 인디 필름** | `afternoon-sun` · 台式青春胶片 |
| 8 | `real-cn-jiangnan-mist` | **강남 연우(안개비) 청자빛 포트레이트** | `cn-jiangnan-celadon-mist` · 中式江南烟雨清冷 |
| 9 | `real-cn-palace-redwall` | **고궁 붉은 담장 따스한 오후 햇살** | `cn-crimson-wall-sun` · 中式红墙琉璃暖阳 |
| 10 | `real-cn-song-minimal` | **송나라 여요(汝窯) 미니멀 여백 미학** | `cn-song-ruyao-minimal` · 中式宋韵极简留白 |
| 11 | `real-cn-tang-splendor` | **성당(盛唐) 금빛 연회 촛불 무드** | `cn-tang-gilded-lantern` · 中式盛唐鎏金夜宴 |
| 12 | `real-cn-dunhuang-sunset` | **둔황 사막 황혼의 금빛 역광** | `cn-dunhuang-amber-dusk` · 中式敦煌大漠流沙 |
| 13 | `real-cn-ink-wash-light` | **수묵 농담(濃淡) 흑백 실사 조명** | `cn-ink-studio-monochrome` · 中式水墨光影写真 |
| 14 | `real-cn-republican-velvet` | **1930년대 올드 상하이 벨벳 조명** | `cn-vintage-shanghai-tungsten` · 中式民国复古画报 |
| 15 | `real-cn-shanghai-bund` | **상하이 와이탄 유금(流金) 앰버 야경** | `cn-bund-amber-cinema` · 中式外滩流光夜色 |
| 16 | `real-cn-hk-tvb-90s` | **90년대 홍콩 TVB 드라마 스틸컷** | `cn-hk-tvb-90s-warm` · 港风90年代TVB剧照 |
| 17 | `real-cn-hk-cyber-rain` | **몽콕 비 오는 밤 홍록 네온 사인** | `cn-mongkok-rain-neon` · 港风旺角雨夜霓虹 |
| 18 | `real-cn-tw-nightmarket` | **타이베이 야시장 따뜻한 등불 보케** | `cn-taipei-nightmarket` · 台式夜市烟火霓虹 |
| 19 | `real-cn-chengdu-teahouse` | **청두 대나무 찻집 여유로운 햇살** | `cn-chengdu-bamboo-sun` · 中式成都竹椅茶馆 |
| 20 | `real-cn-chongqing-cyber` | **충칭 산성 강안개와 네온 야경** | `cn-chongqing-fog-neon` · 中式重庆山城迷雾夜 |
| 21 | `real-cn-dali-sunshine` | **다리 얼하이 호수 고원 투명 햇살** | `cn-dali-highland-sun` · 中式大理洱海慢生活 |
| 22 | `real-cn-hulunbuir-wind` | **후룬베이얼 초원 바람과 황금빛 들판** | `cn-grassland-open-sky` · 中式草原旷野清风 |
| 23 | `real-cn-80s-factory` | **80년대 빈티지 시걸(해오) 필름 카메라** | `cn-80s-seagull-film` · 中式80年代怀旧胶片 |
| 24 | `real-cn-90s-calendar` | **90년대 레트로 달력 화보 스튜디오** | `cn-90s-calendar-bright` · 中式90年代挂历画报 |
| 25 | `real-cn-cny-festive` | **설날 신춘(新春) 레드 골드 축복 조명** | `cn-lunar-new-year-gold` · 中式新春贺岁红金 |
| 26 | `real-cn-wuxia-breeze` | **무협 영화 청회색 검기 & 바람 역광** | `cn-wuxia-cinematic-cool` · 中式武侠清风江湖 |
| 27 | `real-cn-tea-zen` | **화로 차 우려내기(위로조차) 선(禪) 무드** | `cn-tea-hearth-zen` · 中式围炉煮茶禅意 |
| 28 | `real-cn-guochao-street` | **국조(Guochao) 레드·틸 스트릿 플래시** | `cn-guochao-crimson-teal` · 中式国潮街头撞色 |
| 29 | `real-cn-work-survival` | **오피스 모니터 조명 직장인 생존 짤** | `cn-office-monitor-glow` · 中式大厂打工人图鉴 |
| 30 | `real-cn-bazi-lucky` | **행운의 비단잉어(금리) 골든 후광** | `cn-auspicious-golden-halo` · 中式锦鲤好运玄学风 |
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

### 언어별 100% 단일 언어 이모티콘 세트 (한국어 / 일본어 / 영어 / 중국어)

![전부 한국어 이모티콘 세트](docs/gallery/images/pack-ko.jpg)
![전부 일본어 이모티콘 세트](docs/gallery/images/pack-ja.jpg)
![전부 영어 이모티콘 세트](docs/gallery/images/pack-en.jpg)
![전부 중국어 이모티콘 세트](docs/gallery/images/pack-zh-CN.jpg)

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
