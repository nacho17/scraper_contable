#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

mkdir -p logs

source ".venv/bin/activate"

python main.py >> "logs/last_run.log" 2>&1
