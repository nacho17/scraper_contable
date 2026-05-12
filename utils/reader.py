import logging
import os
import shutil
import time

import pandas as pd

from utils.converter import convertir_xls_a_xlsx
from web.downloader import DownloadBlockedError


logger = logging.getLogger("scraper_contable")


def leer_archivo_descargado(path):
    logger.info("Leyendo archivo: %s", path)

    extension = os.path.splitext(path)[1].lower()

    if extension == ".xls":
        path = convertir_xls_a_xlsx(path)

    df_raw = pd.read_excel(path, header=None, engine="openpyxl")

    celda_a1 = df_raw.iloc[0, 0]
    usuario = str(celda_a1).replace("Cliente:", "").strip()

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


def esperar_descarga_completa(download_dir, archivos_antes, timeout=480, startup_timeout=15):
    segundos = 0

    while segundos < timeout:
        actuales = set(os.listdir(download_dir))
        nuevos = actuales - archivos_antes

        if not nuevos:
            if segundos >= startup_timeout:
                raise TimeoutError("La descarga no comenzo en el tiempo esperado.")
            time.sleep(1)
            segundos += 1
            continue

        archivo = nuevos.pop()
        ruta = os.path.join(download_dir, archivo)

        if archivo.endswith(".crdownload"):
            time.sleep(1)
            segundos += 1
            continue

        size1 = os.path.getsize(ruta)
        time.sleep(1)
        size2 = os.path.getsize(ruta)

        if size1 == size2:
            return ruta

        segundos += 1

    archivos_actuales = set(os.listdir(download_dir)) - archivos_antes
    if _hay_indicio_descarga_bloqueada(archivos_actuales):
        raise DownloadBlockedError(
            "Chrome dejo una descarga incompleta o sin confirmar. Posible bloqueo de seguridad."
        )

    raise TimeoutError("La descarga no se completo en el tiempo esperado.")


def _hay_indicio_descarga_bloqueada(archivos):
    for archivo in archivos:
        nombre = archivo.lower()
        if nombre.endswith(".crdownload") and "unconfirmed" in nombre:
            return True
        if nombre.endswith(".crdownload") and "sin confirmar" in nombre:
            return True

    return False
