import shutil
import os
import platform
import subprocess
import pandas as pd


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

def normalizar_y_validar_dataset(df, col_fecha, columnas_importe, logger=None):

    resumen = {
        "fechas_invalidas": 0,
        "importes_invalidos": {}
    }

    # -------------------
    # FECHAS
    # -------------------
    if col_fecha in df.columns:

        fechas_originales = df[col_fecha].copy()

        df[col_fecha] = pd.to_datetime(
            df[col_fecha],
            dayfirst=True,
            errors="coerce"
        )        

        invalidas = df[col_fecha].isna().sum()
        resumen["fechas_invalidas"] = int(invalidas)

        if invalidas > 0 and logger:
            logger.warning(
                f"{invalidas} fechas inválidas detectadas en columna '{col_fecha}'."
            )

        df = df.sort_values(by=col_fecha)

    else:
        if logger:
            logger.warning(f"La columna fecha '{col_fecha}' no existe en el dataset.")

    # -------------------
    # IMPORTES
    # -------------------
    for col in columnas_importe:

        if col not in df.columns:
            if logger:
                logger.warning(f"La columna importe '{col}' no existe en el dataset.")
            continue

        df[col] = (
            df[col]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )

        df[col] = pd.to_numeric(df[col], errors="coerce")

        invalidos = df[col].isna().sum()
        resumen["importes_invalidos"][col] = int(invalidos)

        if invalidos > 0 and logger:
            logger.warning(
                f"{invalidos} valores inválidos detectados en columna '{col}'."
            )

    return df, resumen


