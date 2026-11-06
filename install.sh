#!/usr/bin/env bash
# One-click installer for wechat-sticker-maker (CLI + Claude Code / Codex / OpenClaw Skill)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

echo "=== Installing wechat-sticker-maker ==="

# 1. Find Python >= 3.10
PYTHON_BIN=""
for cand in python3.12 python3.11 python3.10 python3; do
  if command -v "$cand" >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v "$cand")"
    break
  fi
done

if [[ -z "$PYTHON_BIN" ]]; then
  echo "Error: Python 3.10+ is required." >&2
  exit 1
fi

echo "-> Using Python: $PYTHON_BIN ($($PYTHON_BIN --version))"

# 2. Create virtualenv & install package
if [[ ! -d "$REPO_DIR/.venv" ]]; then
  "$PYTHON_BIN" -m venv "$REPO_DIR/.venv"
fi

"$REPO_DIR/.venv/bin/pip" install --upgrade pip -q
"$REPO_DIR/.venv/bin/pip" install -e "$REPO_DIR" -q
echo "-> Installed Python package into $REPO_DIR/.venv"

# 3. Symlink Skill into Claude Code & Codex skill directories
for SKILL_ROOT in "$HOME/.claude/skills" "$HOME/.codex/skills"; do
  mkdir -p "$SKILL_ROOT"
  TARGET="$SKILL_ROOT/wechat-sticker-maker"
  if [[ -L "$TARGET" || ! -e "$TARGET" ]]; then
    ln -sfn "$REPO_DIR" "$TARGET"
    echo "-> Linked skill: $TARGET -> $REPO_DIR"
  else
    echo "-> Skill path already exists (skipped symlink): $TARGET"
  fi
done

# 4. Run doctor check
echo ""
"$REPO_DIR/.venv/bin/wechat-sticker-maker" doctor || true

echo ""
echo "=== Installation Complete! ==="
echo "Try:"
echo "  $REPO_DIR/.venv/bin/wechat-sticker-maker styles"
echo "  $REPO_DIR/.venv/bin/wechat-sticker-maker duo --category 百合"
echo "  $REPO_DIR/.venv/bin/wechat-sticker-maker plan -i photo1.jpg -p photo2.jpg --duo-category 闺蜜 -o ./output/besties"
