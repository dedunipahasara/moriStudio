#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL_DIR="${PROJECT_ROOT}/models/stable-diffusion"
MODEL_FILE="${MODEL_DIR}/v1-5-pruned_Q4_K.gguf"
MODEL_URL="https://huggingface.co/kostakoff/stable-diffusion-v1-5-GGUF/resolve/main/v1-5-pruned_Q4_K.gguf"
MIN_FREE_GB=5

mkdir -p "${MODEL_DIR}"

if [[ -s "${MODEL_FILE}" ]]; then
  echo "Model already exists:"
  ls -lh "${MODEL_FILE}"
  exit 0
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "ERROR: curl is required. Install it with: sudo apt install curl"
  exit 1
fi

available_kb="$(df -Pk "${MODEL_DIR}" | awk 'NR==2 {print $4}')"
required_kb=$((MIN_FREE_GB * 1024 * 1024))
if [[ "${available_kb}" -lt "${required_kb}" ]]; then
  echo "ERROR: At least ${MIN_FREE_GB} GB free disk space is recommended."
  df -h "${MODEL_DIR}"
  exit 1
fi

echo "Downloading Stable Diffusion 1.5 GGUF Q4_K (about 3.2 GB)."
echo "This is a one-time download; image generation runs locally afterward."
echo "Destination: ${MODEL_FILE}"
echo "Do not close this terminal until the download completes."

partial="${MODEL_FILE}.part"
rm -f "${partial}"
if ! curl -fL --retry 3 --retry-delay 2 --connect-timeout 30 \
  --output "${partial}" "${MODEL_URL}"; then
  rm -f "${partial}"
  echo "ERROR: Model download failed. Check your internet connection and try again."
  exit 1
fi

if [[ ! -s "${partial}" ]]; then
  rm -f "${partial}"
  echo "ERROR: Downloaded model file is empty."
  exit 1
fi

mv "${partial}" "${MODEL_FILE}"
echo "Model downloaded successfully:"
ls -lh "${MODEL_FILE}"
