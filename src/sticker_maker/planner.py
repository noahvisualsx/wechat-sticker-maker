"""Expression catalog planning (categories, explicit picks, motion library) and
multilingual text resolution (captions, speech bubbles, bilingual subtitles)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from .i18n import BUILTIN_CAPTION_LANGUAGES, foreign_text_issue, normalize_language, resolve_localized_text
from .schemas import WECHAT_ALLOWED_COUNTS, ExpressionItem, JobConfig, MemeSpec, TextSpec
from .styles import resolve_style_preset

CATEGORY_LABELS: Dict[str, Dict[str, str]] = {
    "greeting": {"zh": "问候", "en": "Greetings"},
    "positive": {"zh": "开心", "en": "Happy"},
    "negative": {"zh": "难过/生气", "en": "Sad & Angry"},
    "surprise": {"zh": "震惊/疑惑", "en": "Surprise"},
    "reply": {"zh": "回复应答", "en": "Replies"},
    "polite": {"zh": "礼貌", "en": "Polite"},
    "love": {"zh": "爱意/亲密", "en": "Love"},
    "praise": {"zh": "夸奖/加油", "en": "Praise & Cheer"},
    "daily": {"zh": "日常生活", "en": "Daily Life"},
    "work": {"zh": "打工/学习", "en": "Work & Study"},
    "meme": {"zh": "梗/吐槽", "en": "Memes"},
    "festival": {"zh": "节日祝福", "en": "Festivals"},
    "status": {"zh": "状态", "en": "Status"},
    "social": {"zh": "社交互动", "en": "Social"},
    "gaming": {"zh": "开黑电竞", "en": "Gaming & Esports"},
    "fandom": {"zh": "追星打Call", "en": "Fandom & Stan"},
    "wealth": {"zh": "搞钱暴富", "en": "Wealth & Red Packet"},
    "foodie": {"zh": "干饭奶茶", "en": "Foodie & Boba"},
    "campus": {"zh": "学生考研", "en": "Campus & Exams"},
    "sassy": {"zh": "阴阳怪气/茶艺", "en": "Sassy & Sarcastic"},
    "mental": {"zh": "发疯精神状态", "en": "Unhinged Mental State"},
    "pet_collab": {"zh": "萌宠同框", "en": "Pet Collab"},
}

CATEGORY_ALIASES: Dict[str, str] = {
    "问候": "greeting", "开心": "positive", "难过": "negative", "生气": "negative",
    "震惊": "surprise", "回复": "reply", "礼貌": "polite", "爱意": "love", "亲密": "love",
    "夸奖": "praise", "日常": "daily", "打工": "work", "职场": "work", "吐槽": "meme",
    "节日": "festival", "状态": "status", "社交": "social",
    "电竞": "gaming", "游戏": "gaming", "开黑": "gaming", "game": "gaming",
    "追星": "fandom", "打call": "fandom", "爱豆": "fandom", "stan": "fandom",
    "搞钱": "wealth", "暴富": "wealth", "财运": "wealth", "红包": "wealth", "money": "wealth",
    "干饭": "foodie", "吃货": "foodie", "奶茶": "foodie", "美食": "foodie", "food": "foodie",
    "学生": "campus", "校园": "campus", "考研": "campus", "早八": "campus", "study": "campus",
    "阴阳怪气": "sassy", "茶艺": "sassy", "反讽": "sassy", "怼人": "sassy",
    "发疯": "mental", "精神状态": "mental", "emo": "mental", "crazy": "mental",
    "萌宠": "pet_collab", "猫狗": "pet_collab", "吸猫": "pet_collab", "pet": "pet_collab",
}

THEME_PACKS: Dict[str, Dict[str, object]] = {
    "打工人": {"pack_type": "mixed", "categories": ["work", "mental", "reply"], "meme_categories": ["work-life"], "style": "real-cn-work-survival", "desc": "早八困成狗、收到、持证摸鱼、光速下班全套打工人续命包"},
    "发疯": {"pack_type": "mixed", "categories": ["mental", "sassy", "meme"], "meme_categories": ["abstract"], "style": "real-high-contrast", "desc": "精神状态美丽、已老实求放过、发疯指数999%高能抽象包"},
    "干饭": {"pack_type": "expressions", "categories": ["foodie", "daily", "positive"], "style": "real-kr-cafe-film", "desc": "奶茶续命、夜宵烧烤、吃饱再减肥吃货专属包"},
    "搞钱": {"pack_type": "expressions", "categories": ["wealth", "festival", "praise"], "style": "real-cn-bazi-lucky", "desc": "接泼天富贵、红包拿来、老板大气、一夜暴富锦鲤包"},
    "电竞": {"pack_type": "expressions", "categories": ["gaming", "meme", "sassy"], "style": "real-cyber-neon", "desc": "上号开黑、求大佬带飞、这波天秀、网卡460开黑包"},
    "追星": {"pack_type": "expressions", "categories": ["fandom", "love", "praise"], "style": "real-kr-photocard", "desc": "为姐姐打Call、神颜暴击、嗑死我了、抢到票了追星同好包"},
    "阴阳怪气": {"pack_type": "expressions", "categories": ["sassy", "meme"], "style": "real-vogue-editorial", "desc": "就这？那你很棒哦、品一口好茶、退退退反讽斗图包"},
    "学生党": {"pack_type": "expressions", "categories": ["campus", "mental", "daily"], "style": "real-jp-school-rooftop", "desc": "逢考必过、极限赶DDL、早八人、论文一把过校园包"},
    "萌宠": {"pack_type": "expressions", "categories": ["pet_collab", "love", "daily"], "style": "real-jp-airy", "desc": "吸猫续命、修勾打招呼、同步歪头杀、卑微铲屎官萌宠同框包"},
    "闺蜜": {"pack_type": "duo", "duo_categories": ["besties"], "style": "real-purikura", "desc": "贴脸比耶、奶茶干杯、吃瓜八卦、护短抱抱闺蜜双人包"},
    "情侣": {"pack_type": "duo", "duo_categories": ["couple"], "style": "real-kr-drama", "desc": "摸头杀、背后抱、捏脸宠溺、额头相抵情侣甜宠双人包"},
    "百合": {"pack_type": "duo", "duo_categories": ["yuri"], "style": "real-jp-sakura-film", "desc": "指尖挑下巴、清冷姐姐壁咚、双女主宿命感贴脸百合双人包"},
    "双男主": {"pack_type": "duo", "duo_categories": ["yaoi"], "style": "real-blue-hour", "desc": "拽领带对视、西装背靠背、雨夜共撑黑伞双男主宿命感包"},
    "欢喜冤家": {"pack_type": "duo", "duo_categories": ["rivals"], "style": "real-variety-meme", "desc": "互相扯脸、弹脑门、偷喝奶茶、吵架秒和好相爱相杀双人包"},
    "亲子": {"pack_type": "duo", "duo_categories": ["family"], "style": "real-film-kodak-gold", "desc": "大小同款托腮、有姐在别怕、戳乖宝脸蛋家庭温情双人包"},
    "猫主子": {"pack_type": "pet", "pet_categories": ["cat_boss", "pet_meme"], "style": "real-jp-airy", "desc": "蔑视眼神、飞机耳哈气、踩奶营业、讨罐罐全套真宠实拍猫主子包"},
    "快乐修勾": {"pack_type": "pet", "pet_categories": ["dog_happy", "pet_meme"], "style": "real-film-kodak-gold", "desc": "歪头杀、飞奔接下班、吐舌傻笑、委屈垂耳全套真宠实拍修勾包"},
    "AI冲浪梗": {"pack_type": "memes", "meme_categories": ["ai-meme", "chat-ui", "ban-warning"], "style": "real-cutout", "desc": "正在思考、Token耗尽、转账520、仅三天可见、已老实全套冲浪热梗包"},
}

MEME_CATEGORY_LABELS: Dict[str, Dict[str, str]] = {
    "ai-meme": {"zh": "AI 梗", "en": "AI memes"},
    "ban-warning": {"zh": "封号/警告", "en": "Ban & warning"},
    "chat-ui": {"zh": "聊天界面梗", "en": "Chat UI"},
    "abstract": {"zh": "抽象/发疯", "en": "Abstract"},
    "classic-meme": {"zh": "经典梗图", "en": "Classic memes"},
    "work-life": {"zh": "打工人", "en": "Work life"},
}

CURATED_8 = [
    "01_hello",
    "03_goodnight",
    "04_laugh",
    "06_cry",
    "09_acknowledged",
    "11_thanks",
    "13_yay",
    "16_love",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def get_default_presets_path() -> Path:
    ref_path = _repo_root() / "references" / "expression-presets.json"
    if ref_path.exists():
        return ref_path
    raise FileNotFoundError("expression-presets.json not found in references/")


def get_motion_library_path() -> Path:
    return _repo_root() / "references" / "motion-library.json"


@lru_cache(maxsize=2)
def load_motion_library(path_str: Optional[str] = None) -> Dict[str, dict]:
    p = Path(path_str) if path_str else get_motion_library_path()
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_all_presets(presets_path: Path | None = None) -> List[ExpressionItem]:
    path = presets_path or get_default_presets_path()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    items = [ExpressionItem(**item) for item in data]
    library = load_motion_library()

    ids = set()
    captions = set()
    for item in items:
        if not item.id or not item.caption:
            raise ValueError(f"Preset item missing id or caption: {item}")
        if item.id in ids:
            raise ValueError(f"Duplicate preset id: {item.id}")
        if item.caption in captions:
            raise ValueError(f"Duplicate preset caption: {item.caption}")
        ids.add(item.id)
        captions.add(item.caption)
        if "zh-CN" not in item.captions:
            item.captions["zh-CN"] = item.caption
        # Fill generic AI keyframe poses from the motion library when an entry has none
        if not item.motion.keyframe_poses and item.motion.type in library:
            lib = library[item.motion.type]
            item.motion.keyframe_poses = list(lib.get("keyframe_poses", []))
            if lib.get("stationary_parts"):
                item.motion.stationary_parts = list(lib["stationary_parts"])
    return items


def get_meme_templates_path() -> Path:
    return _repo_root() / "references" / "meme-templates.json"


def load_meme_templates(path: Path | None = None) -> List[ExpressionItem]:
    p = path or get_meme_templates_path()
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    items = [ExpressionItem(**d) for d in data]
    library = load_motion_library()
    seen = set()
    for it in items:
        if it.id in seen:
            raise ValueError(f"Duplicate meme template id: {it.id}")
        seen.add(it.id)
        it.captions.setdefault("zh-CN", it.caption)
        if not it.motion.keyframe_poses and it.motion.type in library:
            it.motion.keyframe_poses = list(library[it.motion.type].get("keyframe_poses", []))
    return items


def get_item_by_id(item_id: str) -> ExpressionItem:
    from .duo import load_duo_presets
    from .pets import load_pet_presets
    for it in load_all_presets() + load_meme_templates() + load_duo_presets() + load_pet_presets():
        if it.id == item_id:
            return it
    raise ValueError(f"Unknown expression / meme / duo / pet id: {item_id}")


def plan_memes(
    count: int,
    template_ids: Optional[Sequence[str]] = None,
    categories: Optional[Sequence[str]] = None,
) -> List[ExpressionItem]:
    memes = load_meme_templates()
    by_id = {m.id: m for m in memes}
    selected: List[ExpressionItem] = []
    for tid in template_ids or []:
        if tid not in by_id:
            raise ValueError(f"Unknown meme template: {tid}. See `wechat-sticker-maker memes`.")
        if by_id[tid] not in selected:
            selected.append(by_id[tid])
    if categories:
        cats = {c.strip().lower() for c in categories if c.strip()}
        unknown = cats - set(MEME_CATEGORY_LABELS)
        if unknown:
            raise ValueError(f"Unknown meme categories: {sorted(unknown)}. Available: {sorted(MEME_CATEGORY_LABELS)}")
        selected.extend(_round_robin([m for m in memes if m.category in cats and m not in selected], count - len(selected)))
    if len(selected) < count:
        selected.extend([m for m in memes if m not in selected][: count - len(selected)])
    if len(selected) < count:
        raise ValueError(f"Only {len(memes)} meme templates available, cannot plan {count}")
    return selected[:count]


def plan_pack(job: JobConfig, strict_counts: bool = True) -> List[ExpressionItem]:
    """Plan a pack of expressions, memes, duo interactions, or a mix (``job.pack_type``)."""
    if strict_counts and job.count not in WECHAT_ALLOWED_COUNTS:
        raise ValueError(f"Count must be 8, 16, or 24, got {job.count}")
    if job.pack_type == "duo":
        from .duo import plan_duo_expressions
        return plan_duo_expressions(
            job.count,
            categories=job.duo_categories or job.categories,
            duo_ids=job.duo_ids or job.expression_ids,
        )
    if job.pack_type == "pet":
        from .pets import plan_pet_expressions
        return plan_pet_expressions(
            job.count,
            categories=job.pet_categories or job.categories,
            pet_ids=job.pet_ids or job.expression_ids,
        )
    if job.pack_type == "memes":
        return plan_memes(job.count, job.meme_templates, job.meme_categories)
    if job.pack_type == "mixed":
        n_memes = len(job.meme_templates) if job.meme_templates else max(1, job.count // 4)
        n_memes = min(n_memes, job.count - 1) if job.count > 1 else 1
        exprs = plan_expressions(job.count - n_memes, categories=job.categories, expression_ids=job.expression_ids, strict_counts=False)
        return exprs + plan_memes(n_memes, job.meme_templates, job.meme_categories)
    return plan_expressions(job.count, categories=job.categories, expression_ids=job.expression_ids, strict_counts=strict_counts)


def localize_meme(
    item: ExpressionItem,
    job: JobConfig,
    custom_captions: Optional[Dict[str, object]] = None,
) -> Optional[MemeSpec]:
    """Return the item's meme spec in the job language.

    Applies ``job.meme_texts`` (main text override) and captions-file translations of the form
    ``{"m02_china_ip_blocked": {"elements": {"1": {"es": "..."}}}}`` (keys are element indexes).
    """
    if item.meme is None:
        return None
    lang = normalize_language(job.language)
    meme = item.meme.model_copy(deep=True)
    entry = (custom_captions or {}).get(item.id)
    if isinstance(entry, dict) and isinstance(entry.get("elements"), dict):
        for key, texts in entry["elements"].items():
            try:
                el = meme.elements[int(key)]
            except (ValueError, IndexError):
                continue
            if isinstance(texts, dict):
                has_fields = any(f in texts for f in ("text", "title", "button"))
                mapping = texts if has_fields else {"text": texts}
                for field in ("text", "title", "button"):
                    sub = mapping.get(field)
                    if isinstance(sub, str):
                        sub = {lang: sub}
                    if isinstance(sub, dict) and sub.get(lang):
                        getattr(el, field)[lang] = sub[lang]
    override = (job.meme_texts or {}).get(item.id)
    if override:
        for el in meme.elements:
            if el.text:
                el.text = {lang: override}
                break
    return meme


def sticker_texts(spec: TextSpec, meme: Optional[MemeSpec]) -> List[str]:
    """Every string that will be drawn on one sticker (in the job language)."""
    texts = [t for t in (spec.caption, spec.bubble_text) if t]
    if meme is not None:
        for el in meme.elements:
            for field in ("text", "title", "button"):
                d = getattr(el, field) or {}
                if d:
                    t, exact = resolve_localized_text(d, spec.language, allow_english_fallback=False)
                    if el.value is not None:
                        v = el.value
                        t = t.replace("{value}", str(int(v)) if float(v).is_integer() else f"{v:g}")
                    texts.append(t if exact else "")
    return texts


def language_issues(
    items: Sequence[ExpressionItem],
    job: JobConfig,
    custom_captions: Optional[Dict[str, object]] = None,
) -> List[str]:
    """Pre-flight check: every sticker must contain text in exactly ONE language (the job language).

    Reports missing translations (would otherwise fall back to another language) and any
    mixed-language strings (e.g. "你好 Hi there!").
    """
    issues: List[str] = []
    lang = normalize_language(job.language)
    for it in items:
        spec = resolve_text_spec(it, job, custom_captions)
        meme = localize_meme(it, job, custom_captions)
        if spec.needs_translation and spec.layout != "none":
            issues.append(f"{it.id}: 没有 {lang} 文案（请用 captions-template 生成翻译模板并传入 --captions-file）")
        if meme is not None:
            for i, el in enumerate(meme.elements):
                for field in ("text", "title", "button"):
                    d = getattr(el, field) or {}
                    if d and not resolve_localized_text(d, lang, allow_english_fallback=False)[1]:
                        issues.append(f"{it.id}: 梗图元素 #{i} ({el.type}.{field}) 没有 {lang} 文字")
        for t in sticker_texts(spec, meme):
            problem = foreign_text_issue(t, lang)
            if problem:
                issues.append(f"{it.id}: {problem}")
    return issues


def list_categories(presets_path: Path | None = None) -> Dict[str, Dict[str, object]]:
    counts: Dict[str, int] = {}
    for item in load_all_presets(presets_path):
        counts[item.category] = counts.get(item.category, 0) + 1
    out: Dict[str, Dict[str, object]] = {}
    for cid, n in counts.items():
        label = CATEGORY_LABELS.get(cid, {"zh": cid, "en": cid})
        out[cid] = {"zh": label["zh"], "en": label["en"], "count": n}
    return out


def _round_robin(pool: List[ExpressionItem], count: int) -> List[ExpressionItem]:
    """Pick diversely across categories, keeping catalog order inside each category."""
    buckets: Dict[str, List[ExpressionItem]] = {}
    order: List[str] = []
    for it in pool:
        if it.category not in buckets:
            buckets[it.category] = []
            order.append(it.category)
        buckets[it.category].append(it)
    picked: List[ExpressionItem] = []
    while len(picked) < count and any(buckets.values()):
        for cat in order:
            if buckets[cat] and len(picked) < count:
                picked.append(buckets[cat].pop(0))
    return picked


def plan_expressions(
    count: int = 16,
    presets_path: Path | None = None,
    categories: Optional[Sequence[str]] = None,
    expression_ids: Optional[Sequence[str]] = None,
    strict_counts: bool = True,
) -> List[ExpressionItem]:
    """Select expressions for a pack.

    - default: curated 8 / first 16 / first 24 core expressions (WeChat-friendly)
    - ``expression_ids``: explicit picks in order (filled up to ``count`` from the catalog)
    - ``categories``: diverse round-robin selection within the given categories
    - ``strict_counts``: enforce WeChat's 8/16/24 rule (disable for Telegram/LINE/... packs)
    """
    if strict_counts and count not in WECHAT_ALLOWED_COUNTS:
        raise ValueError(f"Count must be 8, 16, or 24, got {count}")
    if count < 1:
        raise ValueError("Count must be positive")

    all_items = load_all_presets(presets_path)
    item_map = {item.id: item for item in all_items}
    selected: List[ExpressionItem] = []

    if expression_ids:
        for iid in expression_ids:
            if iid not in item_map:
                raise ValueError(f"Unknown expression id: {iid}")
            if item_map[iid] not in selected:
                selected.append(item_map[iid])

    if categories:
        cats = {CATEGORY_ALIASES.get(c.strip().lower(), CATEGORY_ALIASES.get(c.strip(), c.strip().lower())) for c in categories if c.strip()}
        unknown = cats - {it.category for it in all_items}
        if unknown:
            raise ValueError(f"Unknown categories: {sorted(unknown)}. Available: {sorted(CATEGORY_LABELS)}")
        pool = [it for it in all_items if it.category in cats and it not in selected]
        selected.extend(_round_robin(pool, count - len(selected)))

    if not selected:
        if count == 8:
            selected = [item_map[i] for i in CURATED_8 if i in item_map]
        else:
            selected = all_items[:count]

    if len(selected) < count:
        rest = [it for it in all_items if it not in selected]
        selected.extend(rest[: count - len(selected)])
    if len(selected) < count:
        raise ValueError(f"Catalog only has {len(all_items)} expressions, cannot plan {count}")
    return selected[:count]


# ---------------------------------------------------------------------------
# Text resolution
# ---------------------------------------------------------------------------


def _custom_entry(custom: Dict[str, object], item_id: str, part: str, language: str) -> Optional[str]:
    entry = custom.get(item_id)
    if entry is None:
        return None
    if isinstance(entry, str):
        return entry if part == "caption" else None
    if isinstance(entry, dict):
        if part in entry and isinstance(entry[part], (dict, str)):
            sub = entry[part]
            if isinstance(sub, str):
                return sub
            text, ok = resolve_localized_text(sub, language, allow_english_fallback=False)
            return text if ok else None
        if part == "caption" and not ({"caption", "bubble"} & set(entry)):
            text, ok = resolve_localized_text({k: v for k, v in entry.items() if isinstance(v, str)}, language, allow_english_fallback=False)
            return text if ok else None
    return None


def localized_caption(item: ExpressionItem, language: str, custom: Optional[Dict[str, object]] = None) -> tuple[str, bool]:
    """Return (caption, needs_translation) for the language."""
    language = normalize_language(language)
    if custom:
        c = _custom_entry(custom, item.id, "caption", language)
        if c:
            return c, False
    texts = dict(item.captions)
    texts.setdefault("zh-CN", item.caption)
    text, exact = resolve_localized_text(texts, language, default=item.caption)
    return text, not exact


def localized_bubble(item: ExpressionItem, language: str, custom: Optional[Dict[str, object]] = None) -> Optional[str]:
    language = normalize_language(language)
    if custom:
        b = _custom_entry(custom, item.id, "bubble", language)
        if b:
            return b
    if item.bubble and item.bubble.texts:
        text, _ = resolve_localized_text(item.bubble.texts, language)
        return text or None
    return None


def resolve_text_spec(
    item: ExpressionItem,
    job: JobConfig,
    custom_captions: Optional[Dict[str, object]] = None,
) -> TextSpec:
    """Resolve what text to draw (caption / bubble / bilingual subtitle) for one sticker."""
    language = normalize_language(job.language)
    caption, needs_tr = localized_caption(item, language, custom_captions)
    bubble_line = localized_bubble(item, language, custom_captions)
    override = (job.meme_texts or {}).get(item.id)
    if override:
        if item.meme is not None and any(el.text for el in item.meme.elements):
            pass  # the override replaces the main meme element text (see localize_meme)
        else:
            caption, needs_tr = override, False

    layout = item.text_layout if job.text_layout == "auto" else job.text_layout
    preset = resolve_style_preset(job.style)
    shape = job.bubble_shape or (item.bubble.shape if item.bubble else preset.bubble.default_shape)
    position = item.bubble.position if item.bubble else "auto"
    animation = (item.bubble.animation if item.bubble and item.bubble.animation else None) or job.bubble_animation

    spec = TextSpec(
        language=language,
        layout=layout,
        bubble_shape=shape,
        bubble_position=position,
        bubble_animation=animation,
        needs_translation=needs_tr,
    )
    if layout == "caption":
        spec.caption = caption
    elif layout == "bubble":
        spec.bubble_text = caption
    elif layout == "both":
        if bubble_line and bubble_line != caption:
            spec.bubble_text = bubble_line
            spec.caption = caption
        else:
            spec.layout = "bubble"
            spec.bubble_text = caption
    else:  # none
        spec.caption = ""
    return spec


def translation_template(
    items: Sequence[ExpressionItem],
    language: str,
) -> Dict[str, Dict[str, object]]:
    """Build a captions-file skeleton for a language without built-in captions."""
    language = normalize_language(language)
    out: Dict[str, Dict[str, object]] = {}
    for it in items:
        entry: Dict[str, object] = {
            "_source": {k: v for k, v in it.captions.items() if k in BUILTIN_CAPTION_LANGUAGES},
            "_mood": it.mood,
            "caption": {language: it.captions.get(language, "")},
        }
        if it.bubble and it.bubble.texts:
            entry["_bubble_source"] = it.bubble.texts
            entry["bubble"] = {language: it.bubble.texts.get(language, "")}
        if it.meme and any(el.text or el.title or el.button for el in it.meme.elements):
            elements: Dict[str, object] = {}
            for i, el in enumerate(it.meme.elements):
                fields = {}
                for field in ("text", "title", "button"):
                    d = getattr(el, field) or {}
                    if d:
                        fields[field] = {language: d.get(language, "")}
                        fields[f"_{field}_source"] = {k: v for k, v in d.items() if k in BUILTIN_CAPTION_LANGUAGES}
                if fields:
                    elements[str(i)] = fields
            entry["elements"] = elements
        out[it.id] = entry
    return out
