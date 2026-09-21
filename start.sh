#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/backend"
source .venv/bin/activate 2>/dev/null || true
uvicorn app.main:app --reload --host 127.0.0.1 --port 8100 &
API_PID=$!
cd "$ROOT/frontend"
npm run dev -- --host 127.0.0.1 --port 5180 &
UI_PID=$!
echo "SANGAM API :8100 (pid $API_PID) | UI :5180 (pid $UI_PID)"
echo "Open http://localhost:5180"
wait
