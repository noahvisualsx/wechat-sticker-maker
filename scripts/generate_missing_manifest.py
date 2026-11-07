#!/usr/bin/env python3
"""Generate the complete missing-images JSON queue and Markdown checklist for Codex."""

from __future__ import annotations

import json
from pathlib import Path

from sticker_maker.duo import build_duo_static_prompt, load_duo_presets
from sticker_maker.planner import CATEGORY_LABELS, load_all_presets
from sticker_maker.prompts import build_static_prompt
from sticker_maker.schemas import CharacterBible, RenderStyle
from sticker_maker.styles import infer_language_for_style, load_style_presets

ROOT = Path(__file__).resolve().parent.parent
W = ROOT / "output" / "real-gallery-20261106"

IDENTITY_FACTS = [
    "Exact same real person as the original supplied portrait",
    "Natural face shape, dark almond eyes at original size and spacing, original nose and pink lips, natural skin texture",
    "Long voluminous black wavy center-parted hair with forehead wisps",
    "Small gold hoop earrings",
    "Same white collared long-sleeve shirt, black sleeveless V-neck knit cardigan with gold buttons, navy and burgundy striped tie",
]

PARTNER_FACTS_BY_CAT = {
    "besties": ["Stylish young East Asian woman best friend with soft brown waves, bright expressive eyes, chic knit top"],
    "couple": ["Handsome young East Asian man with clean dark hair, warm gentle gaze, crisp casual shirt and jacket"],
    "yuri": ["Tall cool-beauty East Asian woman (older-sister aura) with sleek long dark hair, tailored black blazer, magnetic gaze"],
    "yaoi": ["Two handsome young East Asian men in tailored shirts/suits with sharp bone structure and cinematic chemistry"],
    "rivals": ["Playful young East Asian partner/friend with lively teasing expression and casual streetwear"],
    "family": ["Cute younger sibling / family member with matching bright eyes and warm affectionate family chemistry"],
}

P1_NEW_SINGLE_PICKS = [
    # (category, expr_id, style_id)
    ("gaming", "133_game_log_on", "real-cyber-neon"),
    ("gaming", "142_game_loot_gold", "real-kr-idol-selfie"),
    ("fandom", "144_fan_lightstick", "real-kr-photocard"),
    ("fandom", "147_fan_ship_otp", "real-kr-fansign-soft"),
    ("wealth", "155_wealth_get_rich", "real-cn-bazi-lucky"),
    ("wealth", "162_wealth_payday_joy", "real-cn-cny-festive"),
    ("foodie", "166_food_boba_gulp", "real-kr-cafe-film"),
    ("foodie", "171_food_hotpot_call", "real-cn-tw-nightmarket"),
    ("campus", "178_camp_pass_exam", "real-jp-school-rooftop"),
    ("campus", "181_camp_ddl_rush", "real-american-yearbook"),
    ("sassy", "188_sass_just_this", "real-vogue-editorial"),
    ("sassy", "194_sass_sip_tea", "real-cn-chengdu-teahouse"),
    ("mental", "199_ment_stable_fine", "real-work-emo"),
    ("mental", "200_ment_behaving_now", "real-high-contrast"),
    ("pet_collab", "210_pet_hug_cat", "real-jp-airy"),
    ("pet_collab", "211_pet_puppy_wave", "real-film-kodak-gold"),
]

P1_DUO_PICKS = [
    # besties (3)
    ("d01_bestie_cheek_selfie", "real-purikura"),
    ("d02_bestie_milk_tea_cheers", "real-kr-cafe-film"),
    ("d03_bestie_hype_queen", "real-kr-idol-selfie"),
    # couple (3)
    ("d37_couple_head_pat", "real-kr-drama"),
    ("d38_couple_back_hug", "real-golden-hour"),
    ("d41_couple_forehead_touch", "real-kr-winter-snow"),
    # yuri (4)
    ("d73_yuri_chin_lift_gaze", "real-kr-drama"),
    ("d74_yuri_destiny_cheek_touch", "real-jp-sakura-film"),
    ("d75_yuri_cool_unnie_kabedon", "real-vogue-editorial"),
    ("d76_yuri_hair_intertwine_sleep", "real-golden-hour"),
    # yaoi (2)
    ("d109_yaoi_tie_pull_gaze", "real-blue-hour"),
    ("d110_yaoi_back_to_back_suit", "real-film-cinestill-800t"),
    # rivals (2)
    ("d129_rival_pinch_cheeks", "real-variety-meme"),
    ("d131_rival_steal_boba", "real-kr-variety"),
    # family (2)
    ("d149_fam_copy_paste_pose", "real-film-kodak-gold"),
    ("d150_fam_sister_shield", "real-cn-xhs-vibe"),
]

DEFAULT_CAT_STYLE = {
    "gaming": "real-cyber-neon",
    "fandom": "real-kr-photocard",
    "wealth": "real-cn-bazi-lucky",
    "foodie": "real-kr-cafe-film",
    "campus": "real-jp-school-rooftop",
    "sassy": "real-vogue-editorial",
    "mental": "real-work-emo",
    "pet_collab": "real-jp-airy",
    "besties": "real-purikura",
    "couple": "real-kr-drama",
    "yuri": "real-jp-sakura-film",
    "yaoi": "real-blue-hour",
    "rivals": "real-variety-meme",
    "family": "real-film-kodak-gold",
}


def main() -> None:
    styles = load_style_presets()
    exprs = {x.id: x for x in load_all_presets()}
    duos = {x.id: x for x in load_duo_presets()}

    base_rem = json.loads((W / "plan_remaining_after_limit.json").read_text(encoding="utf-8"))
    # Filter out any items whose target_file already exists on disk
    existing_items = [x for x in base_rem if not (ROOT / x["target_file"]).exists()]

    p1_rep = [x for x in existing_items if x["priority"] == "P1-representative"]
    p1_anim = [x for x in existing_items if x["priority"] == "P1-animated-sheet"]
    p2_hello = [x for x in existing_items if x["priority"] == "P2-hello-comparison"]

    p1_new_single = []
    p1_single_ids = set()
    for cat, eid, style_id in P1_NEW_SINGLE_PICKS:
        p1_single_ids.add(eid)
        e = exprs[eid]
        st = styles[style_id]
        lang = infer_language_for_style(style_id)
        bible = CharacterBible(
            character_id="real-gallery",
            source_sha256="user-reference",
            subject_type="human-portrait",
            identity_facts=IDENTITY_FACTS,
            locked_attributes=IDENTITY_FACTS,
            master_anchor="original portrait reference",
            reference_image="original portrait reference",
            render_style=RenderStyle(style_id=style_id),
        )
        prompt = build_static_prompt(bible, e, style=style_id, text_layout=e.text_layout)
        key = f"{style_id}__{eid}"
        target = f"output/real-gallery-20261106/raw/{key}.png"
        if not (ROOT / target).exists():
            p1_new_single.append({
                "key": key,
                "target_file": target,
                "style": style_id,
                "name": st.display_name,
                "region": st.region,
                "language": lang,
                "expression": eid,
                "caption": e.caption,
                "category": cat,
                "layout": e.text_layout,
                "mode": "static",
                "priority": "P1-new-single-category",
                "prompt": prompt,
            })

    p1_duo = []
    p1_duo_ids = set()
    for did, style_id in P1_DUO_PICKS:
        p1_duo_ids.add(did)
        d = duos[did]
        st = styles[style_id]
        lang = infer_language_for_style(style_id)
        bible = CharacterBible(
            character_id="real-gallery-duo",
            source_sha256="user-reference",
            subject_type="human-portrait",
            identity_facts=IDENTITY_FACTS,
            locked_attributes=IDENTITY_FACTS,
            master_anchor="original portrait reference",
            reference_image="original portrait reference",
            render_style=RenderStyle(style_id=style_id),
        )
        prompt = build_duo_static_prompt(
            bible, d, partner_facts=PARTNER_FACTS_BY_CAT.get(d.category), style=style_id, text_layout=d.text_layout
        )
        key = f"{style_id}__{did}"
        target = f"output/real-gallery-20261106/raw/{key}.png"
        if not (ROOT / target).exists():
            p1_duo.append({
                "key": key,
                "target_file": target,
                "style": style_id,
                "name": st.display_name,
                "region": st.region,
                "language": lang,
                "expression": did,
                "caption": d.caption,
                "name_zh": d.name_zh,
                "category": d.category,
                "layout": d.text_layout,
                "mode": "static",
                "priority": "P1-duo-showcase",
                "prompt": prompt,
            })

    # P3: Remaining 72 new single-person expressions (133..220 not in P1_NEW_SINGLE_PICKS)
    p3_single = []
    for eid, e in exprs.items():
        num = int(eid.split("_")[0]) if eid.split("_")[0].isdigit() else 0
        if num < 133 or eid in p1_single_ids:
            continue
        style_id = DEFAULT_CAT_STYLE.get(e.category, "real-cutout")
        st = styles[style_id]
        lang = infer_language_for_style(style_id)
        bible = CharacterBible(
            character_id="real-gallery",
            source_sha256="user-reference",
            subject_type="human-portrait",
            identity_facts=IDENTITY_FACTS,
            locked_attributes=IDENTITY_FACTS,
            master_anchor="original portrait reference",
            reference_image="original portrait reference",
            render_style=RenderStyle(style_id=style_id),
        )
        prompt = build_static_prompt(bible, e, style=style_id, text_layout=e.text_layout)
        key = f"{style_id}__{eid}"
        target = f"output/real-gallery-20261106/raw/{key}.png"
        if not (ROOT / target).exists():
            p3_single.append({
                "key": key,
                "target_file": target,
                "style": style_id,
                "name": st.display_name,
                "region": st.region,
                "language": lang,
                "expression": eid,
                "caption": e.caption,
                "category": e.category,
                "layout": e.text_layout,
                "mode": "static",
                "priority": "P3-single-remaining",
                "prompt": prompt,
            })

    # P3: Remaining 152 duo presets
    p3_duo = []
    for did, d in duos.items():
        if did in p1_duo_ids:
            continue
        style_id = DEFAULT_CAT_STYLE.get(d.category, "real-cutout")
        st = styles[style_id]
        lang = infer_language_for_style(style_id)
        bible = CharacterBible(
            character_id="real-gallery-duo",
            source_sha256="user-reference",
            subject_type="human-portrait",
            identity_facts=IDENTITY_FACTS,
            locked_attributes=IDENTITY_FACTS,
            master_anchor="original portrait reference",
            reference_image="original portrait reference",
            render_style=RenderStyle(style_id=style_id),
        )
        prompt = build_duo_static_prompt(
            bible, d, partner_facts=PARTNER_FACTS_BY_CAT.get(d.category), style=style_id, text_layout=d.text_layout
        )
        key = f"{style_id}__{did}"
        target = f"output/real-gallery-20261106/raw/{key}.png"
        if not (ROOT / target).exists():
            p3_duo.append({
                "key": key,
                "target_file": target,
                "style": style_id,
                "name": st.display_name,
                "region": st.region,
                "language": lang,
                "expression": did,
                "caption": d.caption,
                "name_zh": d.name_zh,
                "category": d.category,
                "layout": d.text_layout,
                "mode": "static",
                "priority": "P3-duo-remaining",
                "prompt": prompt,
            })

    # Save P1+P2 queue to plan_remaining_after_limit.json (and full P1+P2+P3 to plan_codex_all_missing.json)
    core_queue = p1_rep + p1_anim + p1_new_single + p1_duo + p2_hello
    full_queue = core_queue + p3_single + p3_duo

    (W / "plan_remaining_after_limit.json").write_text(
        json.dumps(core_queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (W / "plan_codex_all_missing.json").write_text(
        json.dumps(full_queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # Build Markdown checklist
    md = []
    md.append("# 待 Codex 继续生成的真人表情包底图总清单（含新扩展分类与双人互动）\n")
    md.append("## 1. 整体完成度与待跑汇总\n")
    md.append("- **✅ 已完成入库（无需重复生成）**：")
    md.append("  - **单人风格底图**：已完成 **46 款风格 / 72 张真人静态贴纸**（通用 18/18 款 100% 完成、韩系 15/30 款、日系 6/30 款、中式 7/30 款）")
    md.append("  - **真动作 GIF**：已完成 **10 款**（4 张 `2×2` 风格动作表 + 6 张通用动作 GIF）")
    md.append("  - **真人梗图模板（60 / 60 款，100% 已全部完成！）**：刚刚已由本地 Python 复用现有真人四格底图将全部 **60 款梗图（含新增 `m39`–`m60` 22 款）** 100% 渲染入库至 `docs/gallery/memes/`，**0 Token 消耗，无需 Codex 生图**！\n")

    md.append("- **⏳ 待 Codex 继续生成的图片（已按优先级写入 JSON 队列）**：")
    md.append("  - **核心队列文件**：[`output/real-gallery-20261106/plan_remaining_after_limit.json`](plan_remaining_after_limit.json)（共 **184 张**：P1 必跑 **102 张** + P2 对比图 **82 张**）")
    md.append("  - **全量队列文件**：[`output/real-gallery-20261106/plan_codex_all_missing.json`](plan_codex_all_missing.json)（含 P3 全曲库扩展共 **408 张**）\n")

    md.append("| 优先级 (`priority`) | 类型说明 | 数量 | 目标目录 | 是否必跑 |")
    md.append("|---|---|---:|---|---|")
    md.append(f"| **`P1-representative`** | 108 款摄影风格中剩余未生成的独立表情底图（韩 15 + 日 24 + 中 23） | **{len(p1_rep)} 张** | `output/real-gallery-20261106/raw/` | ⭐ **必跑 (P1)** |")
    md.append(f"| **`P1-animated-sheet`** | 4 大系列新增代表真动图 `2×2` 四格动作连拍图 | **{len(p1_anim)} 张** | `output/real-gallery-20261106/sheets/` | ⭐ **必跑 (P1)** |")
    md.append(f"| **`P1-new-single-category`** | 新增 8 大单人分类代表图（电竞/追星/搞钱/干饭/考研/茶艺/发疯/萌宠，每类 2 张） | **{len(p1_new_single)} 张** | `output/real-gallery-20261106/raw/` | ⭐ **必跑 (P1)** |")
    md.append(f"| **`P1-duo-showcase`** | 6 大双人互动关系代表图（闺蜜 3 / 情侣 3 / 百合 4 / 双男主 2 / 冤家 2 / 亲子 2） | **{len(p1_duo)} 张** | `output/real-gallery-20261106/raw/` | ⭐ **必跑 (P1)** |")
    md.append(f"| **`P2-hello-comparison`** | 82 款新增风格的统一 `01_hello`（你好）同动作光影对比图 | **{len(p2_hello)} 张** | `output/real-gallery-20261106/raw/` | 选跑 (P2) |")
    md.append(f"| **`P3-single-remaining`** | 新增 8 大单人分类其余 72 款动作全量底图 (`133`–`220`) | **{len(p3_single)} 张** | `output/real-gallery-20261106/raw/` | 选跑 (P3) |")
    md.append(f"| **`P3-duo-remaining`** | 168 套双人互动其余 152 款动作全量底图 (`d01`–`d168`) | **{len(p3_duo)} 张** | `output/real-gallery-20261106/raw/` | 选跑 (P3) |")
    md.append(f"| **合计（P1 核心必跑）** | **补齐全部 108 风格 + 22 单人分类展板 + 6 双人分类展板 + 18 真动图** | **102 张** | — | — |\n")

    md.append("---\n")
    md.append("## 2. 直接复制给 Codex 的续跑指令\n")
    md.append("```text")
    md.append("请读取 output/real-gallery-20261106/plan_remaining_after_limit.json：")
    md.append("1. 按顺序优先生成以下 P1 核心必跑任务（共 102 张），每张直接保存到该项的 target_file 路径（已存在的文件自动跳过）：")
    md.append("   - priority == 'P1-representative'（62 张：韩系 15 + 日系 24 + 中式 23 剩余风格静态底图）")
    md.append("   - priority == 'P1-animated-sheet'（8 张：2x2 四格真动作连拍底图）")
    md.append("   - priority == 'P1-new-single-category'（16 张：电竞/追星/搞钱/干饭/考研/茶艺/发疯/萌宠 8 大新分类代表图）")
    md.append("   - priority == 'P1-duo-showcase'（16 张：闺蜜/情侣/百合/双男主/欢喜冤家/亲子 6 大双人关系代表图）")
    md.append("2. 若额度充足，再继续生成 priority == 'P2-hello-comparison' 的 82 张统一问候对比图（或读取 plan_codex_all_missing.json 继续生成 P3）。")
    md.append("3. 铁律：全部使用同一真人参考照（白衬衫+黑V领针织马甲+酒红藏蓝斜纹领带+黑长卷发），100% 保留真实五官骨相与自然肤质，绝不卡通化，不在图片内画任何文字或气泡。")
    md.append("```\n")

    md.append("---\n")
    md.append("## 3. P1 必跑清单明细（共 102 张）\n")

    md.append("### 3.1 `P1-representative`：108 款风格剩余静态底图（62 张）\n")
    md.append("| # | 系列 | 风格 ID (`style`) | 风格名称 | 表情 ID | 台词 (`language`) | 保存路径 (`target_file`) |")
    md.append("|---:|---|---|---|---|---|---|")
    for idx, x in enumerate(p1_rep, 1):
        md.append(f"| {idx} | {x['region']} | `{x['style']}` | **{x['name']}** | `{x['expression']}` | {x['caption']} (`{x['language']}`) | `{x['target_file']}` |")

    md.append("\n### 3.2 `P1-animated-sheet`：真动图 `2×2` 四格动作连拍图（8 张）\n")
    md.append("| # | 系列 | 风格 ID (`style`) | 风格名称 | 动作表情 ID | 台词 (`language`) | 保存路径 (`target_file`) |")
    md.append("|---:|---|---|---|---|---|---|")
    for idx, x in enumerate(p1_anim, 1):
        md.append(f"| {idx} | {x['region']} | `{x['style']}` | **{x['name']}** | `{x['expression']}` | {x['caption']} (`{x['language']}`) | `{x['target_file']}` |")

    md.append("\n### 3.3 `P1-new-single-category`：新增 8 大单人分类代表图（16 张，每类 2 张）\n")
    md.append("| # | 分类 (`category`) | 风格 ID (`style`) | 风格名称 | 表情 ID | 台词 (`language`) | 保存路径 (`target_file`) |")
    md.append("|---:|---|---|---|---|---|---|")
    for idx, x in enumerate(p1_new_single, 1):
        cat_zh = CATEGORY_LABELS.get(x["category"], {}).get("zh", x["category"])
        md.append(f"| {idx} | **{cat_zh}** (`{x['category']}`) | `{x['style']}` | {x['name']} | `{x['expression']}` | {x['caption']} (`{x['language']}`) | `{x['target_file']}` |")

    md.append("\n### 3.4 `P1-duo-showcase`：6 大双人互动关系代表图（16 张）\n")
    md.append("| # | 关系分类 (`category`) | 风格 ID (`style`) | 互动名称 | 预设 ID | 台词 (`language`) | 保存路径 (`target_file`) |")
    md.append("|---:|---|---|---|---|---|---|")
    for idx, x in enumerate(p1_duo, 1):
        md.append(f"| {idx} | `{x['category']}` | `{x['style']}` | **{x.get('name_zh', x['caption'])}** | `{x['expression']}` | {x['caption']} (`{x['language']}`) | `{x['target_file']}` |")

    md.append("\n---\n")
    md.append("## 4. P2 选跑清单：`P2-hello-comparison` 统一 `01_hello` 问候对比图（82 张）\n")
    md.append("| # | 系列 | 风格 ID (`style`) | 风格名称 | 表情 ID | 语种 | 保存路径 (`target_file`) |")
    md.append("|---:|---|---|---|---|---|---|")
    for idx, x in enumerate(p2_hello, 1):
        md.append(f"| {idx} | {x['region']} | `{x['style']}` | **{x['name']}** | `01_hello` | `{x['language']}` | `{x['target_file']}` |")

    (W / "MISSING_CHECKLIST.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote {W / 'MISSING_CHECKLIST.md'}")
    print(f"Core queue (plan_remaining_after_limit.json): {len(core_queue)} items (P1={len(p1_rep)+len(p1_anim)+len(p1_new_single)+len(p1_duo)}, P2={len(p2_hello)})")
    print(f"Full queue (plan_codex_all_missing.json): {len(full_queue)} items (+P3_single={len(p3_single)}, +P3_duo={len(p3_duo)})")


if __name__ == "__main__":
    main()
