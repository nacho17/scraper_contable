#!/usr/bin/env bash
set -e

# Debe ejecutarse con: chmod +x build/mac/build_mac.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

pyinstaller --onefile --clean --name Grupo2000 main.py

echo "Build finalizado. Binario generado en dist/Grupo2000"
