#!/bin/bash
# ── Jan Seva Portal — One-Command Startup ──────────────────────────────────
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║    🏛️  JAN SEVA PORTAL — AI Grievance System  🇮🇳     ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── 1. Install dependencies ─────────────────────────────────────────────────
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

# ── 2. Start FastAPI backend ─────────────────────────────────────────────────
echo ""
echo "🚀 Starting FastAPI backend on http://localhost:8000 ..."
(
  cd "$ROOT"
  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --log-level warning &
  BACKEND_PID=$!
  echo "   Backend PID: $BACKEND_PID"
)

# Give backend time to initialise DB
sleep 3

# ── 3. Start Streamlit frontend ──────────────────────────────────────────────
echo "🌐 Starting Streamlit frontend on http://localhost:8501 ..."
echo ""
echo "══════════════════════════════════════════════════════"
echo "  ✅  App running at  →  http://localhost:8501"
echo "  🔑  Admin login:  admin / admin123"
echo "  📋  API docs:      http://localhost:8000/docs"
echo "══════════════════════════════════════════════════════"
echo ""

streamlit run frontend/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --browser.gatherUsageStats false \
  --theme.base light
