#!/usr/bin/env bash
set -uo pipefail

cd "$(dirname "$0")"

mkdir -p logs

.venv/bin/python main.py --mode auto > "logs/last_run.log" 2>&1
EXIT_CODE=$?

if [ "$EXIT_CODE" -eq 0 ]; then
  say "Grupo 2000 finalizado correctamente"
else
  say "Error en la ejecución. Revisar log."
fi

exit "$EXIT_CODE"