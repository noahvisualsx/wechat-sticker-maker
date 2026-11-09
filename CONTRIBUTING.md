# Contributing to WeChat Sticker Maker / 贡献指南

Thank you for your interest in contributing to **WeChat Sticker Maker**!  
感谢你关注并参与 **WeChat Sticker Maker** 开源项目！

---

## Core Design Principles / 核心设计原则

1. **100% Real-Person & Real-Pet Fidelity (`human-portrait` / `pet-portrait`)**
   - Every photographic style preset in `references/style-presets.json` must preserve authentic facial bone structure, real eyes/skin texture, hairstyle, and outfit. Never introduce 2D anime, chibi, or cartoonizing prompts.
   - 所有新增摄影风格必须严格保留真人真实骨相五官、肤质与穿搭（或真宠真实毛发与品种特征），严禁二次元化或卡通假脸化。

2. **Strict Single-Language Isolation / 单语言严格隔离**
   - Every preset in `references/expression-presets.json`, `references/duo-presets.json`, `references/pet-presets.json`, and `references/meme-templates.json` must provide localized text for all 5 supported languages (`zh-CN`, `zh-TW`, `en`, `ja`, `ko`), never mixing scripts inside a single sticker.
   - 新增表情、双人互动、萌宠或梗图模板时，请补齐 `zh-CN`、`zh-TW`、`en`、`ja`、`ko` 五种独立单语种文案，确保单张贴纸内绝不混排多国语言。

3. **Zero-Token Deterministic Typography / 零误差代码端排版**
   - AI image prompts must forbid rasterized text or speech bubbles; all captions, 7 bubble shapes, and meme UI overlays are composited deterministically by Python (`src/sticker_maker/processing/`).
   - 生图 Prompt 中严禁让模型直接手写文字或画气泡；所有字幕、气泡与梗图组件均由 Python 确定性渲染。

---

## Local Development / 本地开发与测试

```bash
./install.sh
source .venv/bin/activate

# Verify environment & catalogs
wechat-sticker-maker doctor

# Run full test suite & smoke test
pytest -q
python scripts/smoke_test.py
```

---

## Pull Request Checklist / 提交检查清单

- [ ] `pytest -q` passes with zero failures.
- [ ] New styles in `references/style-presets.json` include `display_names` for `zh-CN`, `en`, `ko`, and `ja`.
- [ ] New presets include `captions` (and `bubble.texts` if applicable) for `zh-CN`, `zh-TW`, `en`, `ja`, and `ko`.
- [ ] No private portraits, API keys, or local machine paths are committed.
