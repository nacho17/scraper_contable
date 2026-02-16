import os
import time
import shutil
import pandas as pd
import platform
from datetime import datetime
from utils.converter import convertir_xls_a_xlsx


def leer_archivo_descargado(path):
    print("Leyendo archivo:", path)

    extension = os.path.splitext(path)[1].lower()

    # Si es .xls lo convertimos
    if extension == ".xls":
        path = convertir_xls_a_xlsx(path)

    # Siempre leer como xlsx
    df_raw = pd.read_excel(path, header=None, engine="openpyxl")

    # Usuario en A1
    celda_a1 = df_raw.iloc[0, 0]
    usuario = str(celda_a1).replace("Cliente:", "").strip()

    # Header en fila 4
    df = df_raw.iloc[3:].copy()
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)

    return usuario, df


def mover_y_renombrar(path_original, carpeta_destino,
                      dataset_nombre, usuario,
                      fecha_desde, fecha_hasta):

    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    nuevo_nombre = (
        f"{dataset_nombre}_"
        f"{usuario}_"
        f"{fecha_desde}_"
        f"{fecha_hasta}.xls"
    )

    nuevo_path = os.path.join(carpeta_destino, nuevo_nombre)

    shutil.move(path_original, nuevo_path)

    return nuevo_path

def esperar_descarga_completa(download_dir, timeout=30):
    segundos = 0

    while segundos < timeout:
        archivos = os.listdir(download_dir)

        # Si hay archivo temporal, seguimos esperando
        if any(a.endswith(".crdownload") for a in archivos):
            time.sleep(1)
            segundos += 1
            continue

        # Tomamos el último archivo
        if archivos:
            ruta = max(
                [os.path.join(download_dir, f) for f in archivos],
                key=os.path.getctime
            )

            # Verificamos que no esté creciendo
            size1 = os.path.getsize(ruta)
            time.sleep(1)
            size2 = os.path.getsize(ruta)

            if size1 == size2:
                return ruta

        time.sleep(1)
        segundos += 1

    raise TimeoutError("La descarga no se completó en el tiempo esperado.")
