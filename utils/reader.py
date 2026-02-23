import os
import time
import shutil
import pandas as pd
import logging
from utils.converter import convertir_xls_a_xlsx


logger = logging.getLogger("scraper_contable")


def leer_archivo_descargado(path):
    logger.info("Leyendo archivo: %s", path)

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


def esperar_descarga_completa(download_dir, archivos_antes, timeout=180):
    segundos = 0

    while segundos < timeout:
        actuales = set(os.listdir(download_dir))
        nuevos = actuales - archivos_antes

        # Si todav?a no aparece nada nuevo
        if not nuevos:
            time.sleep(1)
            segundos += 1
            continue

        # Hay un archivo nuevo
        archivo = nuevos.pop()
        ruta = os.path.join(download_dir, archivo)

        # Si todav?a se est? descargando
        if archivo.endswith(".crdownload"):
            time.sleep(1)
            segundos += 1
            continue

        # Verificamos que el tama?o est? estable
        size1 = os.path.getsize(ruta)
        time.sleep(1)
        size2 = os.path.getsize(ruta)

        if size1 == size2:
            return ruta

        segundos += 1

    raise TimeoutError("La descarga no se complet? en el tiempo esperado.")
