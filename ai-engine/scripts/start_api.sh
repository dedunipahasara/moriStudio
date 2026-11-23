#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

if [[ ! -d ".venv" ]]; then
  echo "Python virtual environment .venv not found. Create it and install requirements first."
  exit 1
fi

source .venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
