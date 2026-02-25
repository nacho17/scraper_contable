#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "${SCRIPT_DIR}"

echo "==> Verificando requisitos para macOS..."

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: No se encontró python3 en el sistema."
    echo "Instale Python 3 y vuelva a ejecutar este script."
    exit 1
fi

if command -v libreoffice >/dev/null 2>&1; then
    LIBREOFFICE_OK="yes"
elif [ -x "/Applications/LibreOffice.app/Contents/MacOS/soffice" ]; then
    LIBREOFFICE_OK="yes"
else
    LIBREOFFICE_OK="no"
fi

if [ "${LIBREOFFICE_OK}" != "yes" ]; then
    echo "ERROR: LibreOffice no está disponible."
    echo "Instale LibreOffice y vuelva a ejecutar este script."
    echo "Descarga oficial: https://www.libreoffice.org/download/download-libreoffice/"
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "==> Creando entorno virtual .venv..."
    python3 -m venv .venv
else
    echo "==> Entorno .venv ya existe."
fi

echo "==> Instalando dependencias desde requirements.txt..."
"${SCRIPT_DIR}/.venv/bin/python" -m pip install --upgrade pip
"${SCRIPT_DIR}/.venv/bin/python" -m pip install -r requirements.txt

echo "==> Configurando permisos de ejecución..."
chmod +x "${SCRIPT_DIR}/run.command"
chmod +x "${SCRIPT_DIR}/run_auto.command"

DESKTOP_LINK="${HOME}/Desktop/Grupo2000.command"
TARGET="${SCRIPT_DIR}/run.command"

if [ -L "${DESKTOP_LINK}" ] || [ -e "${DESKTOP_LINK}" ]; then
    rm -f "${DESKTOP_LINK}"
fi

ln -s "${TARGET}" "${DESKTOP_LINK}"

echo "==> Instalación finalizada correctamente."
echo "Acceso directo creado en: ${DESKTOP_LINK}"
echo "Puede ejecutar el sistema haciendo doble clic en Grupo2000.command"