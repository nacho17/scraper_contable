import shutil
import os
import platform
import subprocess


def obtener_comando_libreoffice():
    # Primero intentar si está en PATH
    if shutil.which("libreoffice"):
        return "libreoffice"

    if shutil.which("soffice"):
        return "soffice"

    # Ruta típica en Windows
    ruta_windows = r"C:\Program Files\LibreOffice\program\soffice.exe"
    if os.path.exists(ruta_windows):
        return ruta_windows

    # Ruta típica en Mac
    ruta_mac = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    if os.path.exists(ruta_mac):
        return ruta_mac

    return None

def convertir_xls_a_xlsx(path):
    comando = obtener_comando_libreoffice()

    if comando is None:
        raise EnvironmentError(
            "LibreOffice no está instalado o no está en el PATH."
        )

    nuevo_path = path + "x"

    subprocess.run([
        comando,
        "--headless",
        "--convert-to",
        "xlsx",
        path,
        "--outdir",
        os.path.dirname(path)
    ], check=True)

    return nuevo_path
