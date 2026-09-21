#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "========================================"
echo " SANGAM setup (first-time install)"
echo "========================================"
echo

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "ERROR: Python 3.10+ was not found."
  echo "Install Python, then re-run ./setup.sh"
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  echo "ERROR: Node.js was not found."
  echo "Install Node.js 18+, then re-run ./setup.sh"
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm was not found."
  exit 1
fi

echo "[1/5] Backend virtual environment..."
if [ ! -x "backend/.venv/bin/python" ]; then
  echo "Creating backend/.venv ..."
  "$PYTHON" -m venv backend/.venv
else
  echo "backend/.venv already exists."
fi

echo "[2/5] Installing Python dependencies..."
backend/.venv/bin/python -m pip install --upgrade pip
backend/.venv/bin/pip install -r backend/requirements.txt

echo "[3/5] Backend environment file..."
if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  echo "Created backend/.env from .env.example"
else
  echo "backend/.env already exists."
fi

echo "[4/5] Frontend dependencies..."
if [ ! -d frontend/node_modules ]; then
  echo "Running npm install in frontend..."
  (cd frontend && npm install)
else
  echo "frontend/node_modules already exists."
fi

if [ ! -f frontend/.env ] && [ -f frontend/.env.example ]; then
  cp frontend/.env.example frontend/.env
  echo "Created frontend/.env from .env.example"
fi

echo "[5/5] Initializing database (SQLite + demo seed)..."
backend/.venv/bin/python backend/scripts/init_db.py

echo
echo "========================================"
echo " Setup complete."
echo " Next: ./start.sh"
echo "========================================"
