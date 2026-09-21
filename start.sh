#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

BACKEND_PORT="${BACKEND_PORT:-8100}"
FRONTEND_PORT="${FRONTEND_PORT:-5180}"

if [ ! -x "backend/.venv/bin/uvicorn" ]; then
  echo "Python environment is missing. Running ./setup.sh first..."
  ./setup.sh
fi

if [ ! -d "frontend/node_modules" ]; then
  echo "frontend/node_modules is missing. Running ./setup.sh first..."
  ./setup.sh
fi

if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
fi

cleanup() {
  echo
  echo "Stopping SANGAM..."
  kill "$API_PID" "$UI_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting SANGAM backend on :${BACKEND_PORT} ..."
(
  cd "$ROOT/backend"
  # shellcheck disable=SC1091
  source .venv/bin/activate
  exec uvicorn app.main:app --reload --host 127.0.0.1 --port "$BACKEND_PORT"
) &
API_PID=$!

sleep 2

echo "Starting SANGAM frontend on :${FRONTEND_PORT} ..."
(
  cd "$ROOT/frontend"
  exec npm run dev -- --host 127.0.0.1 --port "$FRONTEND_PORT"
) &
UI_PID=$!

echo
echo "SANGAM App:   http://localhost:${FRONTEND_PORT}"
echo "SANGAM Login: http://localhost:${FRONTEND_PORT}/#/login"
echo "SANGAM API:   http://localhost:${BACKEND_PORT}/docs"
echo "Health:       http://localhost:${BACKEND_PORT}/api/health"
echo
echo "Press Ctrl+C to stop both servers."
wait
