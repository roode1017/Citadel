#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Roode Demo — 환경 설치 스크립트
# Usage: bash setup.sh
# ─────────────────────────────────────────────────────────────
set -e

echo ""
echo "🛡️  Roode Demo Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Python 버전 확인
PYTHON=$(command -v python3 || command -v python)
PY_VER=$($PYTHON --version 2>&1)
echo "Python: $PY_VER"

# pip 업그레이드
$PYTHON -m pip install --upgrade pip -q

# 의존성 설치
echo ""
echo "📦 패키지 설치 중..."
$PYTHON -m pip install -r requirements.txt

echo ""
echo "✅ 설치 완료!"
echo ""
echo "▶  실행 방법:"
echo "   streamlit run app.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
