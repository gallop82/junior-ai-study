#!/usr/bin/env bash
set -euo pipefail

BACKEND_NAME="junior-backend"
FRONTEND_NAME="junior-frontend"

if ! command -v pm2 >/dev/null 2>&1; then
  echo "pm2 is not installed or not in PATH."
  exit 1
fi

pm2 stop "$BACKEND_NAME" "$FRONTEND_NAME" || true
pm2 delete "$BACKEND_NAME" "$FRONTEND_NAME" || true
pm2 status
