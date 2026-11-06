"""Language registry, locale normalization, caption resolution, and per-script font discovery.

Supports every language Pillow can draw with an installed font. Five languages ship with
built-in hand-written sticker captions (zh-CN, zh-TW, en, ja, ko); any other language can be
provided through a captions file (see ``references/text-bubbles-and-languages.md``).
"""

from __future__ import annotations

import json
import logging
import os
import platform
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from PIL import ImageFont, features

logger = logging.getLogger(__name__)

BUILTIN_CAPTION_LANGUAGES: Tuple[str, ...] = ("zh-CN", "zh-TW", "en", "ja", "ko")

RAQM_AVAILABLE: bool = bool(features.check("raqm"))


@dataclass(frozen=True)
class LanguageInfo:
    code: str
    name_native: str
    name_zh: str
    script: str  # hans | hant | jpan | kore | latin | cyrillic | greek | thai | arabic | hebrew | devanagari ...
    wrap: str  # cjk | space | thai
    direction: str = "ltr"
    needs_shaping: bool = False
    pack_title: str = "Sticker Pack"


LANGUAGES: Dict[str, LanguageInfo] = {
    "zh-CN": LanguageInfo("zh-CN", "简体中文", "简体中文", "hans", "cjk", pack_title="表情包"),
    "zh-TW": LanguageInfo("zh-TW", "繁體中文", "繁体中文", "hant", "cjk", pack_title="貼圖"),
    "en": LanguageInfo("en", "English", "英语", "latin", "space", pack_title="Sticker Pack"),
    "ja": LanguageInfo("ja", "日本語", "日语", "jpan", "cjk", pack_title="スタンプ"),
    "ko": LanguageInfo("ko", "한국어", "韩语", "kore", "space", pack_title="이모티콘"),
    "es": LanguageInfo("es", "Español", "西班牙语", "latin", "space", pack_title="Stickers"),
    "fr": LanguageInfo("fr", "Français", "法语", "latin", "space", pack_title="Autocollants"),
    "de": LanguageInfo("de", "Deutsch", "德语", "latin", "space", pack_title="Sticker"),
    "it": LanguageInfo("it", "Italiano", "意大利语", "latin", "space", pack_title="Sticker"),
    "pt": LanguageInfo("pt", "Português", "葡萄牙语", "latin", "space", pack_title="Figurinhas"),
    "nl": LanguageInfo("nl", "Nederlands", "荷兰语", "latin", "space", pack_title="Stickers"),
    "pl": LanguageInfo("pl", "Polski", "波兰语", "latin", "space", pack_title="Naklejki"),
    "tr": LanguageInfo("tr", "Türkçe", "土耳其语", "latin", "space", pack_title="Çıkartmalar"),
    "vi": LanguageInfo("vi", "Tiếng Việt", "越南语", "latin", "space", pack_title="Nhãn dán"),
    "id": LanguageInfo("id", "Bahasa Indonesia", "印尼语", "latin", "space", pack_title="Stiker"),
    "ms": LanguageInfo("ms", "Bahasa Melayu", "马来语", "latin", "space", pack_title="Pelekat"),
    "fil": LanguageInfo("fil", "Filipino", "菲律宾语", "latin", "space", pack_title="Stickers"),
    "ru": LanguageInfo("ru", "Русский", "俄语", "cyrillic", "space", pack_title="Стикеры"),
    "uk": LanguageInfo("uk", "Українська", "乌克兰语", "cyrillic", "space", pack_title="Стікери"),
    "el": LanguageInfo("el", "Ελληνικά", "希腊语", "greek", "space", pack_title="Αυτοκόλλητα"),
    "th": LanguageInfo("th", "ไทย", "泰语", "thai", "thai", pack_title="สติกเกอร์"),
    "ar": LanguageInfo("ar", "العربية", "阿拉伯语", "arabic", "space", "rtl", True, "ملصقات"),
    "fa": LanguageInfo("fa", "فارسی", "波斯语", "arabic", "space", "rtl", True, "استیکر"),
    "he": LanguageInfo("he", "עברית", "希伯来语", "hebrew", "space", "rtl", False, "מדבקות"),
    "hi": LanguageInfo("hi", "हिन्दी", "印地语", "devanagari", "space", "ltr", True, "स्टिकर"),
}

_ALIASES: Dict[str, str] = {
    "zh": "zh-CN",
    "zh-cn": "zh-CN",
    "zh-hans": "zh-CN",
    "zh-sg": "zh-CN",
    "cn": "zh-CN",
    "zh-tw": "zh-TW",
    "zh-hant": "zh-TW",
    "zh-hk": "zh-TW",
    "zh-mo": "zh-TW",
    "tw": "zh-TW",
    "jp": "ja",
    "kr": "ko",
    "kor": "ko",
    "tl": "fil",
    "iw": "he",
    "in": "id",
}


def normalize_language(code: Optional[str]) -> str:
    """Normalize user language codes (zh_CN, zh-hans, en-US, ja-JP, ko_KR...) to registry codes."""
    if not code:
        return "zh-CN"
    raw = code.strip().replace("_", "-")
    low = raw.lower()
    if low in _ALIASES:
        return _ALIASES[low]
    for known in LANGUAGES:
        if known.lower() == low:
            return known
    base = low.split("-")[0]
    if base in _ALIASES:
        return _ALIASES[base]
    if base in LANGUAGES:
        return base
    return base or "zh-CN"


def get_language_info(code: Optional[str]) -> LanguageInfo:
    norm = normalize_language(code)
    if norm in LANGUAGES:
        return LANGUAGES[norm]
    # Unknown language: assume space-separated Latin-like script; fonts are resolved per-character anyway.
    return LanguageInfo(norm, norm, norm, "latin", "space")


def language_fallback_chain(code: Optional[str]) -> List[str]:
    norm = normalize_language(code)
    chain = [norm]
    base = norm.split("-")[0]
    if base != norm:
        chain.append(base)
    if norm.startswith("zh") and norm != "zh-CN":
        chain.append("zh-CN")
    return chain


def resolve_localized_text(
    texts: Dict[str, str],
    language: Optional[str],
    default: str = "",
    allow_english_fallback: bool = True,
) -> Tuple[str, bool]:
    """Pick the best localized text. Returns (text, is_exact_or_family_match)."""
    if not texts:
        return default, False
    normalized = {normalize_language(k): v for k, v in texts.items() if v}
    for c in language_fallback_chain(language):
        if c in normalized:
            return normalized[c], True
    if allow_english_fallback and "en" in normalized:
        return normalized["en"], False
    return default or next(iter(normalized.values()), ""), False


def load_captions_file(path: Optional[str]) -> Dict[str, Dict[str, object]]:
    """Load a custom captions/translations file.

    Accepted shapes::

        {"01_hello": "Hola"}                                  # text for the job language
        {"01_hello": {"es": "¡Hola!", "fr": "Coucou"}}        # multilingual
        {"01_hello": {"caption": {"es": "¡Hola!"}, "bubble": {"es": "¿Qué tal?"}}}
    """
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Captions file not found: {path}")
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Captions file must be a JSON object keyed by expression id")
    return data


def localized_pack_title(language: Optional[str]) -> str:
    return get_language_info(language).pack_title


_COUNT_LABELS: Dict[str, str] = {
    "zh-CN": "共 {n} 款",
    "zh-TW": "共 {n} 款",
    "ja": "全{n}種",
    "ko": "{n}종",
    "en": "{n} stickers",
    "es": "{n} stickers",
    "fr": "{n} autocollants",
    "de": "{n} Sticker",
    "pt": "{n} figurinhas",
    "ru": "{n} стикеров",
    "th": "{n} สติกเกอร์",
    "vi": "{n} nhãn dán",
    "id": "{n} stiker",
}


def localized_count_label(language: Optional[str], n: int) -> str:
    norm = normalize_language(language)
    tpl = _COUNT_LABELS.get(norm) or _COUNT_LABELS.get(norm.split("-")[0]) or "{n}"
    return tpl.format(n=n)


# ---------------------------------------------------------------------------
# Unicode script detection
# ---------------------------------------------------------------------------

_RANGES: Sequence[Tuple[int, int, str]] = (
    (0x0370, 0x03FF, "greek"),
    (0x0400, 0x052F, "cyrillic"),
    (0x0590, 0x05FF, "hebrew"),
    (0x0600, 0x06FF, "arabic"),
    (0x0750, 0x077F, "arabic"),
    (0x08A0, 0x08FF, "arabic"),
    (0x0900, 0x097F, "devanagari"),
    (0x0E00, 0x0E7F, "thai"),
    (0x1100, 0x11FF, "kore"),
    (0x2E80, 0x2FDF, "han"),
    (0x3000, 0x303F, "cjk-punct"),
    (0x3040, 0x30FF, "kana"),
    (0x3130, 0x318F, "kore"),
    (0x31F0, 0x31FF, "kana"),
    (0x3400, 0x4DBF, "han"),
    (0x4E00, 0x9FFF, "han"),
    (0xA960, 0xA97F, "kore"),
    (0xAC00, 0xD7FF, "kore"),
    (0xF900, 0xFAFF, "han"),
    (0xFB1D, 0xFB4F, "hebrew"),
    (0xFB50, 0xFDFF, "arabic"),
    (0xFE30, 0xFE4F, "cjk-punct"),
    (0xFE70, 0xFEFF, "arabic"),
    (0xFF00, 0xFF60, "cjk-punct"),
    (0xFF61, 0xFF9F, "kana"),
    (0xFFE0, 0xFFEF, "cjk-punct"),
    (0x1F000, 0x1FAFF, "emoji"),
    (0x20000, 0x3134F, "han"),
)


def char_script(ch: str) -> str:
    """Classify a character into a rendering script bucket; 'neutral' for spaces/digits/ASCII punct."""
    cp = ord(ch)
    if ch.isspace():
        return "neutral"
    if cp < 0x0370:
        if ch.isalpha():
            return "latin"
        return "neutral"
    if 0x1E00 <= cp <= 0x1EFF:
        return "latin"
    if 0x2600 <= cp <= 0x27BF or cp in (0x2B50, 0x2B55, 0x2764):
        return "emoji"
    if cp in (0xFE0F, 0x200D) or 0x1F3FB <= cp <= 0x1F3FF:
        return "emoji-mod"
    for lo, hi, name in _RANGES:
        if lo <= cp <= hi:
            return name
    if unicodedata.category(ch).startswith("M"):
        return "mark"
    return "neutral"


def text_needs_complex_shaping(text: str) -> bool:
    return any(char_script(c) in ("arabic", "devanagari") for c in text)


# Scripts each language may legitimately use (besides neutral chars / emoji / short Latin acronyms like IP, CPU, OK)
_ALLOWED_SCRIPTS: Dict[str, Tuple[str, ...]] = {
    "hans": ("han", "cjk-punct"),
    "hant": ("han", "cjk-punct"),
    "jpan": ("han", "kana", "cjk-punct"),
    "kore": ("kore", "cjk-punct"),
    "latin": ("latin",),
    "cyrillic": ("cyrillic",),
    "greek": ("greek",),
    "thai": ("thai",),
    "arabic": ("arabic",),
    "hebrew": ("hebrew",),
    "devanagari": ("devanagari",),
}
_IGNORED_SCRIPTS = {"neutral", "mark", "emoji", "emoji-mod"}


def foreign_text_issue(text: str, language: Optional[str]) -> Optional[str]:
    """Return a description if ``text`` mixes in another language; None if it is single-language.

    Short Latin acronyms/tokens (IP, CPU, OK, AI, 404, BB …) are accepted inside CJK/Korean/Thai
    text because they are part of normal chat slang; full foreign words or other scripts are not.
    """
    if not text:
        return None
    info = get_language_info(language)
    allowed = set(_ALLOWED_SCRIPTS.get(info.script, (info.script,)))
    foreign_chars = sorted({char_script(c) for c in text} - allowed - _IGNORED_SCRIPTS - {"latin"})
    if info.script != "latin" and foreign_chars:
        return f"'{text}' 含有其他文字体系 {foreign_chars}，与语言 {info.code} 不一致"
    if info.script == "latin" and foreign_chars:
        return f"'{text}' 含有非拉丁文字 {foreign_chars}，与语言 {info.code} 不一致"
    if info.script not in ("latin",):
        # Latin words inside non-Latin languages: allow acronyms (≤3 letters or ALL CAPS), reject real words
        word = ""
        for c in text + " ":
            if char_script(c) == "latin":
                word += c
                continue
            if word and len(word) >= 4 and not word.isupper():
                return f"'{text}' 混入了外语单词 '{word}'，每张表情只能使用一种语言（{info.code}）"
            word = ""
    return None


# ---------------------------------------------------------------------------
# Per-script font discovery (macOS / Linux / Windows)
# ---------------------------------------------------------------------------

_MAC = "/System/Library/Fonts"
_MAC_SUP = "/System/Library/Fonts/Supplemental"
_NOTO = [
    "/usr/share/fonts/opentype/noto",
    "/usr/share/fonts/truetype/noto",
    "/usr/share/fonts/noto",
    "/usr/share/fonts/google-noto-cjk",
    "/usr/share/fonts/noto-cjk",
]
_WIN = "C:\\Windows\\Fonts"


def _noto(names: Sequence[str]) -> List[str]:
    return [f"{d}/{n}" for d in _NOTO for n in names]


def _win(names: Sequence[str]) -> List[str]:
    return [f"{_WIN}\\{n}" for n in names]


SCRIPT_FONT_CANDIDATES: Dict[str, List[str]] = {
    "hans": [
        f"{_MAC}/Hiragino Sans GB.ttc",
        f"{_MAC}/STHeiti Medium.ttc",
        *_noto(["NotoSansCJK-Bold.ttc", "NotoSansCJK-Black.ttc", "NotoSansCJK-Regular.ttc", "NotoSansCJKsc-Bold.otf"]),
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc",
        *_win(["msyhbd.ttc", "msyh.ttc", "simhei.ttf"]),
        f"{_MAC_SUP}/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ],
    "hant": [
        f"{_MAC}/STHeiti Medium.ttc",
        f"{_MAC}/Hiragino Sans GB.ttc",
        *_noto(["NotoSansCJK-Bold.ttc", "NotoSansCJK-Regular.ttc", "NotoSansCJKtc-Bold.otf"]),
        *_win(["msjhbd.ttc", "msjh.ttc", "mingliu.ttc"]),
        f"{_MAC_SUP}/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ],
    "jpan": [
        f"{_MAC}/ヒラギノ角ゴシック W6.ttc",
        f"{_MAC}/ヒラギノ丸ゴ ProN W4.ttc",
        f"{_MAC}/ヒラギノ角ゴシック W4.ttc",
        f"{_MAC}/Hiragino Sans GB.ttc",
        *_noto(["NotoSansCJK-Bold.ttc", "NotoSansCJK-Regular.ttc", "NotoSansCJKjp-Bold.otf"]),
        *_win(["YuGothB.ttc", "meiryob.ttc", "meiryo.ttc", "msgothic.ttc"]),
        f"{_MAC_SUP}/Arial Unicode.ttf",
    ],
    "kore": [
        f"{_MAC}/AppleSDGothicNeo.ttc",
        f"{_MAC_SUP}/AppleGothic.ttf",
        *_noto(["NotoSansCJK-Bold.ttc", "NotoSansCJK-Regular.ttc", "NotoSansCJKkr-Bold.otf"]),
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        *_win(["malgunbd.ttf", "malgun.ttf"]),
        f"{_MAC_SUP}/Arial Unicode.ttf",
    ],
    "latin": [
        f"{_MAC_SUP}/Arial Rounded Bold.ttf",
        f"{_MAC_SUP}/Arial Bold.ttf",
        f"{_MAC}/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        *_noto(["NotoSans-Bold.ttf"]),
        *_win(["arialbd.ttf", "segoeuib.ttf", "arial.ttf"]),
        f"{_MAC_SUP}/Arial Unicode.ttf",
    ],
    "cyrillic": [
        f"{_MAC_SUP}/Arial Bold.ttf",
        f"{_MAC}/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        *_noto(["NotoSans-Bold.ttf"]),
        *_win(["arialbd.ttf", "segoeuib.ttf"]),
        f"{_MAC_SUP}/Arial Unicode.ttf",
    ],
    "greek": [
        f"{_MAC_SUP}/Arial Bold.ttf",
        f"{_MAC}/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        *_win(["arialbd.ttf"]),
        f"{_MAC_SUP}/Arial Unicode.ttf",
    ],
    "thai": (
        [
            f"{_MAC_SUP}/Thonburi.ttc",
            f"{_MAC}/ThonburiUI.ttc",
            *_noto(["NotoSansThai-Bold.ttf", "NotoSansThai-Regular.ttf"]),
        ]
        if RAQM_AVAILABLE
        else []
    )
    + [
        # Without libraqm, legacy fonts with pre-positioned Thai marks render correctly
        f"{_MAC_SUP}/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/tlwg/Loma-Bold.ttf",
        "/usr/share/fonts/truetype/tlwg/Loma.ttf",
        *_win(["tahomabd.ttf", "tahoma.ttf", "leelawdb.ttf"]),
        f"{_MAC_SUP}/Thonburi.ttc",
        *_noto(["NotoSansThai-Bold.ttf"]),
    ],
    "arabic": [
        f"{_MAC}/SFArabicRounded.ttf",
        f"{_MAC}/SFArabic.ttf",
        f"{_MAC}/GeezaPro.ttc",
        *_noto(["NotoSansArabic-Bold.ttf", "NotoNaskhArabic-Bold.ttf"]),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        *_win(["arialbd.ttf", "segoeuib.ttf"]),
        f"{_MAC_SUP}/Arial Unicode.ttf",
    ],
    "hebrew": [
        f"{_MAC}/SFHebrewRounded.ttf",
        f"{_MAC}/SFHebrew.ttf",
        *_noto(["NotoSansHebrew-Bold.ttf"]),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        *_win(["arialbd.ttf"]),
        f"{_MAC_SUP}/Arial Unicode.ttf",
    ],
    "devanagari": [
        f"{_MAC}/Kohinoor.ttc",
        f"{_MAC_SUP}/DevanagariMT.ttc",
        f"{_MAC_SUP}/ITFDevanagari.ttc",
        *_noto(["NotoSansDevanagari-Bold.ttf"]),
        *_win(["Nirmala.ttf", "mangal.ttf"]),
        f"{_MAC_SUP}/Arial Unicode.ttf",
    ],
    "emoji": [
        f"{_MAC}/Apple Color Emoji.ttc",
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        "/usr/share/fonts/noto/NotoColorEmoji.ttf",
        *_win(["seguiemj.ttf"]),
    ],
    "symbol": [
        f"{_MAC}/Apple Symbols.ttf",
        f"{_MAC_SUP}/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        *_win(["seguisym.ttf"]),
    ],
}

# Noto/Source Han TTC face family tags per script (index selection)
_TTC_FAMILY_HINTS: Dict[str, Tuple[str, ...]] = {
    "hans": ("SC", "GB", "Simplified"),
    "hant": ("TC", "HK", "Traditional"),
    "jpan": ("JP", "ProN", "Japanese"),
    "kore": ("KR", "Korean", "Gothic Neo"),
}
_WEIGHT_PREFERENCE: Tuple[str, ...] = ("Bold", "W6", "SemiBold", "Semibold", "Heavy", "Medium", "W5", "W4", "Regular")


@lru_cache(maxsize=128)
def _ttc_faces(path: str) -> Tuple[Tuple[int, str, str], ...]:
    faces: List[Tuple[int, str, str]] = []
    for idx in range(0, 24):
        try:
            f = ImageFont.truetype(path, 24, index=idx)
        except Exception:
            break
        family, style = f.getname()
        faces.append((idx, family or "", style or ""))
        if not path.lower().endswith((".ttc", ".otc")):
            break
    return tuple(faces)


@lru_cache(maxsize=128)
def select_font_face_index(path: str, script: str) -> int:
    faces = _ttc_faces(path)
    if len(faces) <= 1:
        return 0
    hints = _TTC_FAMILY_HINTS.get(script, ())

    def score(face: Tuple[int, str, str]) -> Tuple[int, int, int]:
        _, family, style = face
        fam_score = 1 if any(h.lower() in family.lower() for h in hints) else 0
        visible = 0 if family.startswith(".") else 1  # skip hidden UI/interface faces
        st = style.strip().lower()
        w_rank = 0
        for i, w in enumerate(_WEIGHT_PREFERENCE):
            if st == w.lower():
                w_rank = 2 * (len(_WEIGHT_PREFERENCE) - i)
                break
        else:
            for i, w in enumerate(_WEIGHT_PREFERENCE):
                if w.lower() in (style + " " + family).lower():
                    w_rank = 2 * (len(_WEIGHT_PREFERENCE) - i) - 1
                    break
        return fam_score, visible, w_rank

    best = max(faces, key=score)
    return best[0]


_MISSING_PROBE = "\U0010FFFD"


@lru_cache(maxsize=4096)
def _probe_mask(path: str, index: int, ch: str) -> Optional[Tuple[Tuple[int, int, int, int], bytes]]:
    try:
        f = ImageFont.truetype(path, 40, index=index)
        m = f.getmask(ch)
        bbox = m.getbbox()
        return (bbox or (0, 0, 0, 0)), bytes(m)
    except Exception:
        return None


def font_has_glyph(path: str, index: int, ch: str) -> bool:
    """Heuristically detect glyph coverage by comparing against the font's .notdef rendering."""
    if ch.isspace():
        return True
    probe = _probe_mask(path, index, ch)
    if probe is None:
        return False
    bbox, data = probe
    if bbox == (0, 0, 0, 0):
        return unicodedata.category(ch) in ("Cf", "Mn", "Me")
    notdef = _probe_mask(path, index, _MISSING_PROBE)
    if notdef is not None and notdef == probe:
        return False
    return True


def _existing(paths: Sequence[str]) -> List[str]:
    return [p for p in paths if p and Path(p).exists()]


@lru_cache(maxsize=64)
def font_chain_for_script(script: str, user_font: Optional[str] = None) -> Tuple[Tuple[str, int], ...]:
    """Ordered (path, face_index) candidates for a script; the user font is tried first."""
    candidates: List[str] = []
    env_font = os.getenv("STICKER_FONT_PATH")
    for custom in (user_font, env_font):
        if custom and Path(custom).exists():
            candidates.append(custom)
    lookup = script
    if script in ("han", "cjk-punct"):
        lookup = "hans"
    if script == "kana":
        lookup = "jpan"
    candidates.extend(SCRIPT_FONT_CANDIDATES.get(lookup, []))
    # Universal fallbacks
    candidates.extend(SCRIPT_FONT_CANDIDATES["hans"])
    candidates.extend(SCRIPT_FONT_CANDIDATES["symbol"])
    seen = set()
    out: List[Tuple[str, int]] = []
    for p in _existing(candidates):
        if p in seen:
            continue
        seen.add(p)
        out.append((p, select_font_face_index(p, lookup)))
    return tuple(out)


def describe_font_support() -> List[Dict[str, object]]:
    """Report detected fonts per language for `wechat-sticker-maker languages`."""
    rows: List[Dict[str, object]] = []
    samples = {
        "zh-CN": "你好呀", "zh-TW": "謝謝你", "en": "Hello!", "ja": "了解です", "ko": "고마워",
        "es": "¡Hola!", "fr": "Ça va", "de": "Grüß dich", "it": "Ciao", "pt": "Olá", "nl": "Hoi",
        "pl": "Cześć", "tr": "Merhaba", "vi": "Xin chào", "id": "Halo", "ms": "Hai", "fil": "Kumusta",
        "ru": "Привет", "uk": "Привіт", "el": "Γεια", "th": "สวัสดี", "ar": "مرحبا", "fa": "سلام",
        "he": "שלום", "hi": "नमस्ते",
    }
    for code, info in LANGUAGES.items():
        sample = samples.get(code, "Hi")
        script = info.script
        chain = font_chain_for_script(script)
        font_used = None
        for path, idx in chain:
            if all(font_has_glyph(path, idx, c) for c in sample if not c.isspace() and char_script(c) != "neutral"):
                font_used = path
                break
        shaping_ok = (not info.needs_shaping) or RAQM_AVAILABLE
        rows.append(
            {
                "code": code,
                "name": info.name_native,
                "name_zh": info.name_zh,
                "script": script,
                "direction": info.direction,
                "builtin_captions": code in BUILTIN_CAPTION_LANGUAGES,
                "font": font_used,
                "render_ok": bool(font_used) and shaping_ok,
                "note": "" if shaping_ok else "需要 libraqm 才能正确连写/整形（brew install libraqm 后重装 Pillow）",
            }
        )
    return rows


def system_name() -> str:
    return platform.system()
