#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYTHON="${HUMAN_PYTHON:-python}"
export HUMAN_API_HOST="${HUMAN_API_HOST:-127.0.0.1}"
export HUMAN_API_PORT="${HUMAN_API_PORT:-8001}"
exec "$PYTHON" -m service.http_api
