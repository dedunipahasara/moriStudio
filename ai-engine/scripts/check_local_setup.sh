#!/usr/bin/env bash
set -u
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME="${PROJECT_ROOT}/../local-image-runtime/build/bin/sd-server"
MODEL="${PROJECT_ROOT}/models/stable-diffusion/v1-5-pruned_Q4_K.gguf"
echo "Cute3D local generation setup check"
echo "Project: ${PROJECT_ROOT}"
echo
if [[ -x "${RUNTIME}" ]]; then echo "[OK] Runtime executable found"; else echo "[MISSING] Runtime executable: ${RUNTIME}"; fi
if [[ -s "${MODEL}" ]]; then echo "[OK] Model file found"; ls -lh "${MODEL}"; else echo "[MISSING] Model file: ${MODEL}"; echo "       Run: ./scripts/download_model.sh"; fi
if [[ -d "${PROJECT_ROOT}/.venv" ]]; then echo "[OK] Python virtual environment found"; else echo "[MISSING] .venv"; fi
if [[ -f "${PROJECT_ROOT}/.env" ]]; then echo "[OK] .env found"; else echo "[INFO] .env not found; copy .env.example to .env"; fi
if command -v curl >/dev/null 2>&1; then
  if curl -fsS --max-time 3 http://127.0.0.1:8081/health >/dev/null 2>&1; then
    echo "[OK] Stable Diffusion server responds on port 8081"
  else
    echo "[INFO] No HTTP health response on port 8081 (server may be stopped or use another health route)"
  fi
fi
