#!/usr/bin/env python3
"""Build the interactive 4-language GitHub Pages Web Studio (docs/index.html)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "references"
OUT = ROOT / "docs" / "index.html"


def build() -> None:
    styles = json.loads((REF / "style-presets.json").read_text(encoding="utf-8"))
    duos = json.loads((REF / "duo-presets.json").read_text(encoding="utf-8"))
    exprs = json.loads((REF / "expression-presets.json").read_text(encoding="utf-8"))
    memes = json.loads((REF / "meme-templates.json").read_text(encoding="utf-8"))

    # Compact payloads for fast page load
    styles_compact = [
        {
            "id": s["id"],
            "name": s["display_name"],
            "region": s["region"],
            "desc": s["description"],
            "prompt": s["prompt_lock"],
            "lighting": s["lighting"],
            "palette": s.get("default_palette", []),
            "border": s.get("die_cut_border_px", 4),
        }
        for s in styles
    ]
    duos_compact = [
        {
            "id": d["id"],
            "cat": d["category"],
            "name_zh": d.get("name_zh", d["caption"]),
            "captions": d.get("captions", {}),
            "bubbles": (d.get("bubble") or {}).get("texts", {}),
            "shape": (d.get("bubble") or {}).get("shape", "heart"),
            "layout": d.get("text_layout", "caption"),
            "pose": d["static_pose"],
            "keyframes": (d.get("motion") or {}).get("keyframe_poses", []),
        }
        for d in duos
    ]
    exprs_compact = [
        {
            "id": e["id"],
            "cat": e["category"],
            "captions": e.get("captions", {"zh-CN": e["caption"]}),
            "bubbles": (e.get("bubble") or {}).get("texts", {}),
            "shape": (e.get("bubble") or {}).get("shape", "round"),
            "layout": e.get("text_layout", "caption"),
            "pose": e["static_pose"],
        }
        for e in exprs
    ]
    memes_compact = [
        {
            "id": m["id"],
            "cat": m["category"],
            "name_zh": m.get("name_zh", m["caption"]),
            "captions": m.get("captions", {"zh-CN": m["caption"]}),
            "pose": m["static_pose"],
        }
        for m in memes
    ]

    catalog_js = (
        f"const STYLES = {json.dumps(styles_compact, ensure_ascii=False)};\n"
        f"const DUOS = {json.dumps(duos_compact, ensure_ascii=False)};\n"
        f"const EXPRS = {json.dumps(exprs_compact, ensure_ascii=False)};\n"
        f"const MEMES = {json.dumps(memes_compact, ensure_ascii=False)};\n"
    )

    html = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>WeChat Real-Person Sticker Maker Studio · 真人表情包工作台 (108风格 + 108双人互动)</title>
<style>
  :root {
    --bg: #F5F5F7;
    --card: #FFFFFF;
    --text: #1D1D1F;
    --muted: #6E6E73;
    --accent: #07C160;
    --accent-dark: #059B4C;
    --pink: #FF2D55;
    --purple: #AF52DE;
    --blue: #007AFF;
    --border: rgba(0,0,0,0.08);
    --shadow: 0 8px 28px rgba(0,0,0,0.06);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #000000;
      --card: #1C1C1E;
      --text: #F5F5F7;
      --muted: #98989D;
      --border: rgba(255,255,255,0.12);
      --shadow: 0 8px 28px rgba(0,0,0,0.35);
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Hiragino Sans", "Apple SD Gothic Neo", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.5;
  }
  .wrap { max-width: 1240px; margin: 0 auto; padding: 28px 20px 80px; }
  header {
    display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center;
    gap: 16px; padding-bottom: 22px; border-bottom: 1px solid var(--border); margin-bottom: 26px;
  }
  .brand h1 { margin: 0; font-size: 26px; letter-spacing: -0.02em; }
  .brand p { margin: 6px 0 0; color: var(--muted); font-size: 14px; }
  .badges { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
  .badge {
    font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 999px;
    background: rgba(7,193,96,0.12); color: var(--accent);
  }
  .badge.pink { background: rgba(255,45,85,0.12); color: var(--pink); }
  .badge.purple { background: rgba(175,82,222,0.12); color: var(--purple); }
  .badge.blue { background: rgba(0,122,255,0.12); color: var(--blue); }

  .tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 22px; }
  .tab {
    border: 1px solid var(--border); background: var(--card); color: var(--text);
    padding: 9px 16px; border-radius: 999px; cursor: pointer; font-weight: 600; font-size: 14px;
    transition: all .15s ease;
  }
  .tab.active { background: var(--accent); color: #fff; border-color: var(--accent); }

  .panel { display: none; }
  .panel.active { display: block; }

  .filter-bar {
    display: flex; gap: 10px; flex-wrap: wrap; align-items: center;
    background: var(--card); padding: 14px 16px; border-radius: 16px;
    border: 1px solid var(--border); margin-bottom: 18px; box-shadow: var(--shadow);
  }
  input[type="search"], select, input[type="text"] {
    padding: 8px 12px; border-radius: 10px; border: 1px solid var(--border);
    background: var(--bg); color: var(--text); font-size: 14px;
  }
  input[type="search"] { min-width: 240px; flex: 1; }
  .pill-btn {
    border: 1px solid var(--border); background: var(--bg); color: var(--text);
    padding: 6px 12px; border-radius: 999px; cursor: pointer; font-size: 13px;
  }
  .pill-btn.active { background: var(--text); color: var(--card); }

  .grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px;
  }
  .card {
    background: var(--card); border: 1px solid var(--border); border-radius: 16px;
    padding: 16px; box-shadow: var(--shadow); display: flex; flex-direction: column; justify-content: space-between;
  }
  .card-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
  .card-title { font-weight: 700; font-size: 16px; margin: 0; }
  .card-id { font-family: ui-monospace, SFMono-Regular, monospace; font-size: 12px; color: var(--muted); }
  .card-desc { font-size: 13px; color: var(--muted); margin: 8px 0 12px; }
  .swatches { display: flex; gap: 6px; align-items: center; margin-bottom: 10px; }
  .swatch { width: 16px; height: 16px; border-radius: 50%; border: 1px solid rgba(0,0,0,0.15); }
  .lang-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
  .lang-tag {
    font-size: 12px; padding: 3px 8px; border-radius: 6px;
    background: var(--bg); border: 1px solid var(--border);
  }
  .btn-row { display: flex; gap: 8px; flex-wrap: wrap; }
  .btn {
    border: none; background: var(--accent); color: #fff; padding: 7px 12px;
    border-radius: 8px; cursor: pointer; font-size: 12px; font-weight: 600;
  }
  .btn.secondary { background: var(--bg); color: var(--text); border: 1px solid var(--border); }

  .composer-layout {
    display: grid; grid-template-columns: 380px 1fr; gap: 22px; align-items: start;
  }
  @media (max-width: 860px) { .composer-layout { grid-template-columns: 1fr; } }
  .box {
    background: var(--card); border: 1px solid var(--border); border-radius: 18px;
    padding: 20px; box-shadow: var(--shadow);
  }
  .form-group { margin-bottom: 14px; }
  .form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
  .canvas-stage {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 24px; border-radius: 16px; background: #EDEDED; transition: background .2s;
  }
  .canvas-stage.dark { background: #111111; }
  canvas { border-radius: 12px; max-width: 100%; height: auto; box-shadow: 0 4px 20px rgba(0,0,0,0.12); }
  .gallery-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 18px; }
  .gallery-card img { width: 100%; border-radius: 12px; display: block; }
  pre {
    background: var(--bg); padding: 12px; border-radius: 10px; overflow-x: auto;
    font-size: 12px; border: 1px solid var(--border); white-space: pre-wrap;
  }
  .toast {
    position: fixed; bottom: 24px; right: 24px; background: #111; color: #fff;
    padding: 10px 18px; border-radius: 999px; font-size: 13px; font-weight: 600;
    opacity: 0; pointer-events: none; transition: opacity .2s ease; z-index: 999;
  }
  .toast.show { opacity: 1; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="brand">
      <h1>WeChat Real-Person Sticker Studio · 真人表情包工作台</h1>
      <p>100% 真人五官锁死（拒绝卡通化）· 单张严格单语 · 一次生图直出中/英/日/韩 4 套分语言表情包 + 26 平台规范</p>
      <div class="badges">
        <span class="badge">108 款真人实拍风格 (通用18/韩30/日30/中30)</span>
        <span class="badge pink">108 套双人互动 (闺蜜36 / 情侣36 / 百合36)</span>
        <span class="badge purple">132 个高频动作 + 38 梗图模板</span>
        <span class="badge blue">26 个国内外社交平台一键打包</span>
      </div>
    </div>
    <div>
      <a class="btn" href="https://github.com/noahvisualsx/wechat-sticker-maker" target="_blank" style="text-decoration:none;padding:10px 16px;font-size:14px">GitHub Repo ★</a>
    </div>
  </header>

  <div class="tabs">
    <button class="tab active" onclick="switchTab('duo')">👩‍❤️‍👩 108 双人互动 (闺蜜/情侣/百合)</button>
    <button class="tab" onclick="switchTab('styles')">📸 108 单人实拍风格库</button>
    <button class="tab" onclick="switchTab('prompt')">⚡ AI 提示词 & CLI 生成器</button>
    <button class="tab" onclick="switchTab('composer')">🎨 在线白边+气泡合成器 (Canvas)</button>
    <button class="tab" onclick="switchTab('gallery')">🖼️ 实拍效果画廊</button>
  </div>

  <!-- TAB 1: 108 DUO INTERACTIONS -->
  <section id="tab-duo" class="panel active">
    <div class="filter-bar">
      <button class="pill-btn active" onclick="setDuoCat('all', this)">全部 (108)</button>
      <button class="pill-btn" onclick="setDuoCat('besties', this)">👯‍♀️ 闺蜜互动 (36)</button>
      <button class="pill-btn" onclick="setDuoCat('couple', this)">👩‍❤️‍👨 情侣互动 (36)</button>
      <button class="pill-btn" onclick="setDuoCat('yuri', this)">🌸 百合双女主 (36)</button>
      <select id="duo-lang" onchange="renderDuos()">
        <option value="zh-CN">字幕语言: 简体中文 (zh-CN)</option>
        <option value="ko">字幕语言: 한국어 (ko)</option>
        <option value="ja">字幕语言: 日本語 (ja)</option>
        <option value="en">字幕语言: English (en)</option>
        <option value="zh-TW">字幕语言: 繁體中文 (zh-TW)</option>
      </select>
      <input type="search" id="duo-search" placeholder="搜索双人动作 / 台词 (如: 壁咚, 挑下巴, 贴贴, 奶茶, yuri)..." oninput="renderDuos()" />
    </div>
    <div id="duo-grid" class="grid"></div>
  </section>

  <!-- TAB 2: 108 STYLES -->
  <section id="tab-styles" class="panel">
    <div class="filter-bar">
      <button class="pill-btn active" onclick="setStyleRegion('all', this)">全部 (108)</button>
      <button class="pill-btn" onclick="setStyleRegion('通用', this)">🌍 通用 (18 · English)</button>
      <button class="pill-btn" onclick="setStyleRegion('韩系', this)">🇰🇷 韩系 (30 · 한국어)</button>
      <button class="pill-btn" onclick="setStyleRegion('日系', this)">🇯🇵 日系 (30 · 日本語)</button>
      <button class="pill-btn" onclick="setStyleRegion('中式', this)">🇨🇳 中式 (30 · 中文)</button>
      <input type="search" id="style-search" placeholder="搜索风格 ID / 名称 / 光影描述..." oninput="renderStyles()" />
    </div>
    <div id="style-grid" class="grid"></div>
  </section>

  <!-- TAB 3: PROMPT & CLI BUILDER -->
  <section id="tab-prompt" class="panel">
    <div class="composer-layout">
      <div class="box">
        <h3 style="margin-top:0">1. 选择模式与预设</h3>
        <div class="form-group">
          <label>模式 (Pack Mode)</label>
          <select id="pb-mode" onchange="updatePromptBuilder()" style="width:100%">
            <option value="duo">👩‍❤️‍👩 双人真人互动 (闺蜜 / 情侣 / 百合 108套)</option>
            <option value="single">🙋‍♀️ 单人真人日常表情 (132个高频动作)</option>
            <option value="meme">🔥 单人热梗/抽象模板 (38款)</option>
          </select>
        </div>
        <div class="form-group">
          <label>实拍风格 (108 Styles)</label>
          <select id="pb-style" onchange="updatePromptBuilder()" style="width:100%"></select>
        </div>
        <div class="form-group">
          <label>动作 / 互动预设</label>
          <select id="pb-item" onchange="updatePromptBuilder()" style="width:100%"></select>
        </div>
        <div class="form-group">
          <label>出图种类 (Static / 2x2 GIF 动作精灵表)</label>
          <select id="pb-kind" onchange="updatePromptBuilder()" style="width:100%">
            <option value="static">静态透明贴纸 (Static Cutout PNG)</option>
            <option value="sheet">2x2 四格连续动作图 (用于合成微信真动作 GIF)</option>
          </select>
        </div>
        <div class="form-group">
          <label>文字语言 (严格单语)</label>
          <select id="pb-lang" onchange="updatePromptBuilder()" style="width:100%">
            <option value="auto">auto (按风格自动匹配: 韩→韩 / 日→日 / 中→中 / 通用→英)</option>
            <option value="zh-CN">简体中文 (zh-CN)</option>
            <option value="ko">한국어 (ko)</option>
            <option value="ja">日本語 (ja)</option>
            <option value="en">English (en)</option>
          </select>
        </div>
      </div>
      <div class="box">
        <h3 style="margin-top:0">2. 一键复制 AI 提示词 (ChatGPT / Gemini / Seedream) 与 CLI 命令</h3>
        <div class="form-group">
          <label>AI 生图提示词 (直接连同人物参考照发给 ChatGPT / Gemini Nano Banana)</label>
          <pre id="pb-prompt-out"></pre>
          <button class="btn" onclick="copyText('pb-prompt-out')">复制 AI 提示词</button>
        </div>
        <div class="form-group" style="margin-top:18px">
          <label>本地 CLI 一键生成 + 一次生图直出 4 国语言分包命令</label>
          <pre id="pb-cli-out"></pre>
          <button class="btn secondary" onclick="copyText('pb-cli-out')">复制 CLI 命令</button>
        </div>
      </div>
    </div>
  </section>

  <!-- TAB 4: BROWSER CANVAS STICKER COMPOSER -->
  <section id="tab-composer" class="panel">
    <div class="composer-layout">
      <div class="box">
        <h3 style="margin-top:0">在线真人贴纸排版器 (免安装浏览器直出)</h3>
        <div class="form-group">
          <label>上传真人透明 PNG 或白底照片</label>
          <input type="file" id="comp-file" accept="image/*" onchange="loadComposerImage(event)" />
        </div>
        <div class="form-group">
          <label><input type="checkbox" id="comp-keywhite" checked onchange="drawComposer()" /> 自动去除外围纯白/浅灰背景 (Flood-Fill 抠图)</label>
        </div>
        <div class="form-group">
          <label>模切白边宽度 (Die-Cut White Border): <span id="comp-border-val">6</span>px</label>
          <input type="range" id="comp-border" min="0" max="14" value="6" oninput="document.getElementById('comp-border-val').textContent=this.value;drawComposer()" style="width:100%" />
        </div>
        <div class="form-group">
          <label>上方对话气泡形状</label>
          <select id="comp-bubble-shape" onchange="drawComposer()" style="width:100%">
            <option value="heart">💗 爱心气泡 (Heart)</option>
            <option value="round">💬 圆角气泡 (Round)</option>
            <option value="shout">💥 爆炸呐喊 (Shout)</option>
            <option value="thought">💭 云朵思考 (Thought)</option>
            <option value="none">无气泡 (仅底部字幕)</option>
          </select>
        </div>
        <div class="form-group">
          <label>气泡文字 (留空则不画气泡)</label>
          <input type="text" id="comp-bubble-text" value="언니, 나만 봐요" oninput="drawComposer()" style="width:100%" />
        </div>
        <div class="form-group">
          <label>底部粗描边主字幕 (留空则不画底部字)</label>
          <input type="text" id="comp-caption" value="" placeholder="例如: 贴贴 / 收到 / OK!" oninput="drawComposer()" style="width:100%" />
        </div>
        <div class="btn-row">
          <button class="btn" onclick="downloadComposed(240)">下载微信 240×240 PNG</button>
          <button class="btn secondary" onclick="downloadComposed(720)">下载高清 720×720 PNG</button>
        </div>
      </div>
      <div class="box">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
          <strong>微信聊天背景实时预览</strong>
          <div>
            <button class="pill-btn" onclick="document.getElementById('comp-stage').classList.remove('dark')">微信浅色 (#EDEDED)</button>
            <button class="pill-btn" onclick="document.getElementById('comp-stage').classList.add('dark')">微信深色 (#111111)</button>
          </div>
        </div>
        <div id="comp-stage" class="canvas-stage">
          <canvas id="comp-canvas" width="480" height="480"></canvas>
        </div>
      </div>
    </div>
  </section>

  <!-- TAB 5: GALLERY -->
  <section id="tab-gallery" class="panel">
    <div class="gallery-grid">
      <div class="box gallery-card">
        <h3 style="margin-top:0">通用 18 款真人风格 (100% English)</h3>
        <img src="gallery/images/styles-general.jpg" alt="General Styles" loading="lazy" />
      </div>
      <div class="box gallery-card">
        <h3 style="margin-top:0">韩系真人风格 (100% 한국어)</h3>
        <img src="gallery/images/styles-kr.jpg" alt="Korean Styles" loading="lazy" />
      </div>
      <div class="box gallery-card">
        <h3 style="margin-top:0">日系真人风格 (100% 日本語)</h3>
        <img src="gallery/images/styles-jp.jpg" alt="Japanese Styles" loading="lazy" />
      </div>
      <div class="box gallery-card">
        <h3 style="margin-top:0">中式真人风格 (100% 简体中文)</h3>
        <img src="gallery/images/styles-cn.jpg" alt="Chinese Styles" loading="lazy" />
      </div>
      <div class="box gallery-card">
        <h3 style="margin-top:0">全中文 12 张成套表情包 (zh-CN)</h3>
        <img src="gallery/images/pack-zh-CN.jpg" alt="Chinese Pack" loading="lazy" />
      </div>
      <div class="box gallery-card">
        <h3 style="margin-top:0">全韩文 12 张成套表情包 (한국어)</h3>
        <img src="gallery/images/pack-ko.jpg" alt="Korean Pack" loading="lazy" />
      </div>
      <div class="box gallery-card">
        <h3 style="margin-top:0">全日文 12 张成套表情包 (日本語)</h3>
        <img src="gallery/images/pack-ja.jpg" alt="Japanese Pack" loading="lazy" />
      </div>
      <div class="box gallery-card">
        <h3 style="margin-top:0">全英文 12 张成套表情包 (English)</h3>
        <img src="gallery/images/pack-en.jpg" alt="English Pack" loading="lazy" />
      </div>
    </div>
  </section>
</div>

<div id="toast" class="toast">已复制到剪贴板！</div>

<script>
__CATALOG_JS__

let currentDuoCat = 'all';
let currentStyleRegion = 'all';
let composerImg = null;

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 1800);
}

function switchTab(id) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  event.target.classList.add('active');
}

function setDuoCat(cat, btn) {
  currentDuoCat = cat;
  btn.parentElement.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderDuos();
}

function setStyleRegion(reg, btn) {
  currentStyleRegion = reg;
  btn.parentElement.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderStyles();
}

const CAT_BADGE = {
  besties: { label: '👯‍♀️ 闺蜜互动', cls: 'badge' },
  couple:  { label: '👩‍❤️‍👨 情侣互动', cls: 'badge pink' },
  yuri:    { label: '🌸 百合双女主', cls: 'badge purple' }
};

function renderDuos() {
  const q = (document.getElementById('duo-search').value || '').toLowerCase();
  const lang = document.getElementById('duo-lang').value;
  const grid = document.getElementById('duo-grid');
  const filtered = DUOS.filter(d => {
    if (currentDuoCat !== 'all' && d.cat !== currentDuoCat) return false;
    if (!q) return true;
    const hay = [d.id, d.name_zh, d.pose, Object.values(d.captions).join(' '), Object.values(d.bubbles).join(' ')].join(' ').toLowerCase();
    return hay.includes(q);
  });
  grid.innerHTML = filtered.map(d => {
    const b = CAT_BADGE[d.cat] || { label: d.cat, cls: 'badge' };
    const cap = d.captions[lang] || d.captions['zh-CN'] || '';
    const bub = d.bubbles[lang] || d.bubbles['zh-CN'] || '';
    return `
      <div class="card">
        <div>
          <div class="card-head">
            <h4 class="card-title">${d.name_zh}</h4>
            <span class="${b.cls}">${b.label}</span>
          </div>
          <div class="card-id">${d.id} · layout=${d.layout} · bubble=${d.shape}</div>
          <div class="card-desc">${d.pose}</div>
          <div class="lang-tags">
            <span class="lang-tag">🏷️ 字幕 (${lang}): <strong>${cap}</strong></span>
            <span class="lang-tag">💬 气泡 (${lang}): <strong>${bub}</strong></span>
          </div>
        </div>
        <div class="btn-row">
          <button class="btn" onclick="selectInPromptBuilder('duo', '${d.id}')">生成 AI 提示词 / CLI</button>
          <button class="btn secondary" onclick="useInComposer('${bub.replace(/'/g, "\\'")}', '${cap.replace(/'/g, "\\'")}', '${d.shape}')">送入在线排版器</button>
        </div>
      </div>
    `;
  }).join('');
}

function renderStyles() {
  const q = (document.getElementById('style-search').value || '').toLowerCase();
  const grid = document.getElementById('style-grid');
  const filtered = STYLES.filter(s => {
    if (currentStyleRegion !== 'all' && s.region !== currentStyleRegion) return false;
    if (!q) return true;
    return (s.id + ' ' + s.name + ' ' + s.desc + ' ' + s.prompt).toLowerCase().includes(q);
  });
  grid.innerHTML = filtered.map(s => {
    const sw = (s.palette || []).map(c => `<span class="swatch" style="background:${c}" title="${c}"></span>`).join('');
    return `
      <div class="card">
        <div>
          <div class="card-head">
            <h4 class="card-title">${s.name}</h4>
            <span class="badge blue">${s.region}</span>
          </div>
          <div class="card-id">${s.id} · lighting=${s.lighting} · border=${s.border}px</div>
          <div class="card-desc">${s.desc}</div>
          <div class="swatches">${sw}</div>
        </div>
        <div class="btn-row">
          <button class="btn" onclick="selectStyleInBuilder('${s.id}')">用此风格生成提示词</button>
        </div>
      </div>
    `;
  }).join('');
}

function initPromptBuilder() {
  const sSel = document.getElementById('pb-style');
  sSel.innerHTML = STYLES.map(s => `<option value="${s.id}">[${s.region}] ${s.id} — ${s.name}</option>`).join('');
  populateBuilderItems();
}

function populateBuilderItems() {
  const mode = document.getElementById('pb-mode').value;
  const iSel = document.getElementById('pb-item');
  if (mode === 'duo') {
    iSel.innerHTML = DUOS.map(d => `<option value="${d.id}">[${d.cat}] ${d.id} — ${d.name_zh} (${d.captions['zh-CN']})</option>`).join('');
  } else if (mode === 'single') {
    iSel.innerHTML = EXPRS.map(e => `<option value="${e.id}">[${e.cat}] ${e.id} — ${e.captions['zh-CN']}</option>`).join('');
  } else {
    iSel.innerHTML = MEMES.map(m => `<option value="${m.id}">[${m.cat}] ${m.id} — ${m.name_zh}</option>`).join('');
  }
  updatePromptBuilder();
}

document.getElementById('pb-mode').addEventListener('change', populateBuilderItems);

function updatePromptBuilder() {
  const mode = document.getElementById('pb-mode').value;
  const styleId = document.getElementById('pb-style').value;
  const itemId = document.getElementById('pb-item').value;
  const kind = document.getElementById('pb-kind').value;
  const lang = document.getElementById('pb-lang').value;
  const style = STYLES.find(s => s.id === styleId) || STYLES[0];

  let item = null;
  if (mode === 'duo') item = DUOS.find(d => d.id === itemId) || DUOS[0];
  else if (mode === 'single') item = EXPRS.find(e => e.id === itemId) || EXPRS[0];
  else item = MEMES.find(m => m.id === itemId) || MEMES[0];

  const hardLock = "CRITICAL REAL-PERSON RULE: Keep the subject(s) as photorealistic real human portrait cutout(s) of the exact same person(s) from the reference photo(s) (authentic facial bone structure, real eyes/nose/lips, real skin texture, exact hairstyle, and outfit). NEVER cartoonize, NEVER turn into 2D anime, chibi, flat illustration, or 3D doll.";
  let prompt = "";
  if (mode === 'duo') {
    if (kind === 'sheet') {
      const kfs = item.keyframes && item.keyframes.length >= 4 ? item.keyframes : [item.pose, item.pose, item.pose, item.pose];
      prompt = `[TWO-PERSON REAL-PORTRAIT 2x2 ANIMATION SPRITE SHEET]\\n${hardLock}\\nStyle: ${style.id} (${style.name}) — ${style.prompt}\\nInteraction (${item.name_zh}):\\n- Frame 1 (Top-Left): ${kfs[0]}\\n- Frame 2 (Top-Right): ${kfs[1]}\\n- Frame 3 (Bottom-Left): ${kfs[2]}\\n- Frame 4 (Bottom-Right): ${kfs[3]}\\nClean solid white or transparent background, no grid lines, no text or speech bubbles in the image.`;
    } else {
      prompt = `[TWO-PERSON REAL-PORTRAIT STICKER CUTOUT]\\n${hardLock}\\nStyle: ${style.id} (${style.name}) — ${style.prompt}\\nInteraction (${item.name_zh}): ${item.pose}\\nBoth real people framed waist-up/chest-up together on a clean transparent or solid white background. Do NOT draw any text or speech bubbles in the raster image.`;
    }
  } else {
    prompt = `[SINGLE REAL-PERSON STICKER CUTOUT (${kind.toUpperCase()})]\\n${hardLock}\\nStyle: ${style.id} (${style.name}) — ${style.prompt}\\nAction: ${item.pose}\\nClean transparent or solid white background. Do NOT draw any text or speech bubbles in the raster image.`;
  }

  document.getElementById('pb-prompt-out').textContent = prompt;

  let cli = "";
  if (mode === 'duo') {
    cli = `wechat-sticker-maker plan -i personA.jpg -p personB.jpg --pack-type duo --duo-ids ${item.id} --style ${style.id} --language ${lang} --languages zh-CN,en,ja,ko -o ./output/${item.id}\\nwechat-sticker-maker generate -j ./output/${item.id}/job.json`;
  } else if (mode === 'single') {
    cli = `wechat-sticker-maker plan -i photo.jpg --expressions ${item.id} --style ${style.id} --language ${lang} --languages zh-CN,en,ja,ko -o ./output/${item.id}\\nwechat-sticker-maker generate -j ./output/${item.id}/job.json`;
  } else {
    cli = `wechat-sticker-maker meme -t ${item.id} -i photo.jpg --style ${style.id} --language ${lang === 'auto' ? 'zh-CN' : lang} -o ./output/${item.id}.gif`;
  }
  document.getElementById('pb-cli-out').textContent = cli;
}

function selectInPromptBuilder(mode, itemId) {
  document.getElementById('pb-mode').value = mode;
  populateBuilderItems();
  document.getElementById('pb-item').value = itemId;
  updatePromptBuilder();
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-prompt').classList.add('active');
  document.querySelectorAll('.tab')[2].classList.add('active');
}

function selectStyleInBuilder(styleId) {
  document.getElementById('pb-style').value = styleId;
  updatePromptBuilder();
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-prompt').classList.add('active');
  document.querySelectorAll('.tab')[2].classList.add('active');
}

function copyText(elId) {
  const txt = document.getElementById(elId).textContent;
  navigator.clipboard.writeText(txt);
  showToast('已复制到剪贴板！');
}

function useInComposer(bubble, caption, shape) {
  document.getElementById('comp-bubble-text').value = bubble;
  document.getElementById('comp-caption').value = caption;
  document.getElementById('comp-bubble-shape').value = shape || 'heart';
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-composer').classList.add('active');
  document.querySelectorAll('.tab')[3].classList.add('active');
  drawComposer();
}

function loadComposerImage(ev) {
  const file = ev.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    const img = new Image();
    img.onload = () => { composerImg = img; drawComposer(); };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

function drawComposer(targetCanvas) {
  const canvas = targetCanvas || document.getElementById('comp-canvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  const borderPx = parseInt(document.getElementById('comp-border').value || '6', 10) * (W / 240);
  const bubbleShape = document.getElementById('comp-bubble-shape').value;
  const bubbleText = document.getElementById('comp-bubble-text').value.trim();
  const captionText = document.getElementById('comp-caption').value.trim();

  if (composerImg) {
    const off = document.createElement('canvas');
    off.width = W; off.height = H;
    const octx = off.getContext('2d');
    const maxW = W * 0.80, maxH = H * (captionText ? 0.72 : 0.84);
    const scale = Math.min(maxW / composerImg.width, maxH / composerImg.height);
    const dw = composerImg.width * scale, dh = composerImg.height * scale;
    const dx = (W - dw) / 2, dy = H * (captionText ? 0.84 : 0.94) - dh;
    octx.drawImage(composerImg, dx, dy, dw, dh);

    if (document.getElementById('comp-keywhite').checked) {
      const imgData = octx.getImageData(0, 0, W, H);
      const d = imgData.data;
      for (let i = 0; i < d.length; i += 4) {
        if (d[i] > 242 && d[i+1] > 242 && d[i+2] > 242) d[i+3] = 0;
      }
      octx.putImageData(imgData, 0, 0);
    }

    if (borderPx > 0) {
      ctx.save();
      const steps = 16;
      for (let a = 0; a < steps; a++) {
        const ang = (a / steps) * Math.PI * 2;
        ctx.drawImage(off, Math.cos(ang) * borderPx, Math.sin(ang) * borderPx);
      }
      ctx.globalCompositeOperation = 'source-in';
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, W, H);
      ctx.restore();
    }
    ctx.drawImage(off, 0, 0);
  } else {
    ctx.save();
    ctx.fillStyle = 'rgba(7,193,96,0.12)';
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = Math.max(4, borderPx);
    ctx.beginPath();
    ctx.arc(W * 0.5, H * 0.56, W * 0.26, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = '#666';
    ctx.font = `600 ${Math.round(W * 0.045)}px -apple-system, sans-serif`;
    ctx.textAlign = 'center';
    ctx.fillText('点击左侧上传真人照片预览', W * 0.5, H * 0.57);
    ctx.restore();
  }

  // Draw speech bubble
  if (bubbleShape !== 'none' && bubbleText) {
    ctx.save();
    const bx = W * 0.08, by = H * 0.05, bw = W * 0.56, bh = H * 0.19;
    ctx.fillStyle = '#FFFDF9';
    ctx.strokeStyle = bubbleShape === 'heart' ? '#E84A7F' : '#222222';
    ctx.lineWidth = Math.max(2.5, W * 0.012);
    ctx.beginPath();
    ctx.roundRect(bx, by, bw, bh, bh * 0.45);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = bubbleShape === 'heart' ? '#C92A62' : '#1D1D1F';
    ctx.font = `700 ${Math.round(W * 0.052)}px -apple-system, "PingFang SC", "Apple SD Gothic Neo", sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const prefix = bubbleShape === 'heart' ? '♥ ' : '';
    ctx.fillText(prefix + bubbleText, bx + bw / 2, by + bh / 2);
    ctx.restore();
  }

  // Draw bottom caption
  if (captionText) {
    ctx.save();
    ctx.font = `900 ${Math.round(W * 0.105)}px -apple-system, "PingFang SC", "Apple SD Gothic Neo", sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.lineJoin = 'round';
    ctx.lineWidth = Math.max(6, W * 0.032);
    ctx.strokeStyle = '#1D1D1F';
    ctx.strokeText(captionText, W * 0.5, H * 0.96);
    ctx.fillStyle = '#FFFFFF';
    ctx.fillText(captionText, W * 0.5, H * 0.96);
    ctx.restore();
  }
}

function downloadComposed(size) {
  const out = document.createElement('canvas');
  out.width = size; out.height = size;
  drawComposer(out);
  const a = document.createElement('a');
  a.download = `sticker_${size}x${size}.png`;
  a.href = out.toDataURL('image/png');
  a.click();
}

initPromptBuilder();
renderDuos();
renderStyles();
drawComposer();
</script>
</body>
</html>
""".replace("__CATALOG_JS__", catalog_js)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"Built {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build()
