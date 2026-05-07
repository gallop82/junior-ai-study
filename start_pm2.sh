#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BACKEND_NAME="junior-backend"
BACKEND_PORT="8001"

cd "$PROJECT_ROOT"

if ! command -v pm2 >/dev/null 2>&1; then
  echo "pm2 is not installed or not in PATH."
  exit 1
fi

if [ ! -x "backend/.venv/bin/python" ]; then
  echo "backend/.venv/bin/python not found. Please create the virtual environment and install dependencies first."
  exit 1
fi

if [ ! -d "frontend/dist" ]; then
  echo "frontend/dist not found. Please run 'cd frontend && npm run build' first."
  exit 1
fi

pm2 delete "$BACKEND_NAME" >/dev/null 2>&1 || true

pm2 start backend/.venv/bin/python \
  --name "$BACKEND_NAME" \
  --cwd backend \
  --interpreter none \
  -- -m uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT"

pm2 status
