#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Roode Demo — 실행 스크립트
# Usage: bash run.sh
# ─────────────────────────────────────────────────────────────

cd "$(dirname "$0")"

echo ""
echo "🛡️  Roode Demo 시작..."
echo "   http://localhost:8501"
echo "   (종료: Ctrl+C)"
echo ""

streamlit run app.py \
  --server.port 8501 \
  --server.headless false \
  --theme.base dark \
  --theme.primaryColor "#6366f1" \
  --theme.backgroundColor "#0d1117" \
  --theme.secondaryBackgroundColor "#0f172a" \
  --theme.textColor "#e2e8f0"
