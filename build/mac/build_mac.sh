#!/usr/bin/env bash
set -e

# Debe ejecutarse con: chmod +x build/mac/build_mac.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${PROJECT_ROOT}"

pyinstaller --onefile --clean --name Grupo2000 main.py

if [ -f "config.json" ]; then
    cp -f "config.json" "dist/config.json"
    echo "config.json copiado en dist/"
elif [ -f "config_example.json" ]; then
    cp -f "config_example.json" "dist/config_example.json"
    echo "AVISO: no se encontró config.json. Se copió config_example.json en dist/"
else
    echo "AVISO: no se encontró ni config.json ni config_example.json para copiar en dist/"
fi

echo "Build finalizado. Binario generado en dist/Grupo2000"