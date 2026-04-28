#!/usr/bin/env bash
set -euo pipefail

# === CONFIG ===
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$BASE_DIR/logs"
LOG_FILE="$LOG_DIR/last_run.log"
DEBUG_FILE="$LOG_DIR/debug.log"
VOICEOVER_ESTABA_ACTIVO=0

mkdir -p "$LOG_DIR"

echo "==== RUN $(date) ====" >> "$DEBUG_FILE"

# === ASEGURAR REACTIVACION DE VOICEOVER ===
reactivar_voiceover() {
  if [ "$VOICEOVER_ESTABA_ACTIVO" -eq 1 ]; then
    open -a VoiceOver || true
  fi
}
trap reactivar_voiceover EXIT

# === DESACTIVAR VOICEOVER TEMPORALMENTE ===
if osascript -e 'tell application "System Events" to return exists process "VoiceOver"' | grep -q "true"; then
  VOICEOVER_ESTABA_ACTIVO=1
  osascript -e 'tell application "VoiceOver" to quit' || true
fi

# === EJECUCION ===
cd "$BASE_DIR" || exit 1

set +e
"$BASE_DIR/.venv/bin/python" main.py --mode auto >> "$LOG_FILE" 2>&1
EXIT_CODE=$?
set -e

echo "EXIT CODE: $EXIT_CODE" >> "$DEBUG_FILE"

exit "$EXIT_CODE"
