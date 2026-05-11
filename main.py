import argparse
import ctypes
import json
import os
import platform
import sys
from datetime import datetime, timedelta

import pandas as pd
from openpyxl import load_workbook

from excel.updater import (
    MasterExcelArrayFormulaError,
    append_dataframe_to_excel,
    ensure_sheet_exists_with_headers,
    estirar_formulas,
)
from utils.converter import normalizar_y_validar_dataset
from utils.dates import dividir_en_bloques
from utils.logger import setup_logger
from utils.reader import leer_archivo_descargado, mover_y_renombrar, esperar_descarga_completa
from web.downloader import (
    AuthenticationError,
    DownloadBlockedError,
    SiteUnavailableError,
    exportar_dataset,
    iniciar_driver,
    login,
    logout,
)


def cargar_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def obtener_ultima_fecha(maestro_path, hoja_1, columna_fecha):
    try:
        df = pd.read_excel(
            maestro_path,
            sheet_name=hoja_1,
            engine="openpyxl",
        )
    except FileNotFoundError as exc:
        raise Exception(f"No se encontró el archivo: {maestro_path}") from exc
    except ValueError as exc:
        if "Worksheet named" in str(exc) and "not found" in str(exc):
            return None
        raise

    if columna_fecha not in df.columns:
        raise Exception(f"La columna '{columna_fecha}' no existe en la hoja '{hoja_1}'")

    df[columna_fecha] = pd.to_datetime(
        df[columna_fecha],
        dayfirst=True,
        errors="coerce",
    )

    df_valid = df[df[columna_fecha].notna()]

    if df_valid.empty:
        return None

    return df_valid[columna_fecha].max()


def hoja_existe_en_maestro(maestro_path, hoja):
    try:
        wb = load_workbook(maestro_path, read_only=True)
    except FileNotFoundError as exc:
        raise Exception(f"No se encontrÃ³ el archivo: {maestro_path}") from exc

    return hoja in wb.sheetnames


def procesar_dataset(
    maestro_path,
    dataset_config,
    fecha_inicial_config,
    logger,
):
    nombre = dataset_config["nombre"]
    hoja_destino = dataset_config["hoja_destino"]
    columna_fecha = dataset_config["columna_fecha"]

    logger.info("Procesando dataset: %s", nombre)
    hoja_existia = hoja_existe_en_maestro(maestro_path, hoja_destino)

    ultima_fecha = obtener_ultima_fecha(
        maestro_path,
        hoja_destino,
        columna_fecha,
    )

    if ultima_fecha is None:
        if not hoja_existia:
            logger.warning(
                "La hoja '%s' no existe en el maestro. Se usará fecha_inicial_si_vacio.",
                hoja_destino,
            )
        else:
            logger.warning("Archivo vacío o sin fechas válidas.")
        fecha_desde = fecha_inicial_config
    else:
        logger.info("Última fecha encontrada: %s", ultima_fecha.date())
        fecha_desde = (ultima_fecha + timedelta(days=1)).date()

    hoy = datetime.today().date()
    fecha_hasta = hoy - timedelta(days=1)

    logger.info("Fecha desde: %s", fecha_desde)
    logger.info("Fecha hasta: %s", fecha_hasta)

    if fecha_desde > fecha_hasta:
        logger.warning(
            "Rango inválido: fecha_desde (%s) es mayor que fecha_hasta (%s). No se procesará ningún dataset.",
            fecha_desde,
            fecha_hasta,
        )
        return None

    logger.info("Hay fechas nuevas para procesar.")
    return fecha_desde, fecha_hasta


def descargar_y_leer_dataset(
    driver,
    dataset,
    fecha_desde,
    fecha_hasta,
    ruta_descargas,
    procesados_dir,
    logger,
):
    bloques = dividir_en_bloques(fecha_desde, fecha_hasta)

    dfs = []
    usuario_detectado = None

    for sub_desde, sub_hasta in bloques:
        logger.info("Descargando bloque %s -> %s", sub_desde, sub_hasta)

        archivos_antes = set(os.listdir(ruta_descargas))

        exportar_dataset(
            driver,
            dataset["url"],
            sub_desde,
            sub_hasta,
        )

        ultimo_archivo = esperar_descarga_completa(ruta_descargas, archivos_antes)

        logger.info("Archivo detectado: %s", ultimo_archivo)

        usuario_archivo, df_nuevo = leer_archivo_descargado(ultimo_archivo)

        logger.info("Filas de esta porción del dataset: %s", len(df_nuevo))

        if usuario_detectado is None:
            usuario_detectado = usuario_archivo

        if usuario_archivo != usuario_detectado:
            raise Exception("Inconsistencia en usuario detectado")

        dfs.append(df_nuevo)

        nuevo_path = mover_y_renombrar(
            ultimo_archivo,
            procesados_dir,
            dataset["nombre"],
            usuario_archivo,
            sub_desde,
            sub_hasta,
        )

        logger.info("Movido a: %s", nuevo_path)

    df_final = pd.concat(dfs, ignore_index=True)

    return usuario_detectado, df_final


def limpiar_download_temp(download_dir):
    for archivo in os.listdir(download_dir):
        ruta = os.path.join(download_dir, archivo)
        if os.path.isfile(ruta):
            os.remove(ruta)


def resolver_headless(mode):
    sistema = platform.system()

    if sistema == "Darwin":
        return mode == "auto"

    return False


def notificar_windows(success):
    if platform.system() != "Windows":
        return

    try:
        import winsound

        if success:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        else:
            winsound.MessageBeep(winsound.MB_ICONHAND)
    except Exception:
        pass

    try:
        if success:
            mensaje = "Proceso finalizado correctamente"
            estilo = 0x00000040
        else:
            mensaje = "Error en la ejecución. Revisar log."
            estilo = 0x00000010

        ctypes.windll.user32.MessageBoxW(0, mensaje, "Grupo2000", estilo)
    except Exception:
        pass


def main_proceso(mode="manual"):
    config = cargar_config()
    logger = setup_logger()

    fecha_inicial_str = config["procesamiento"]["fecha_inicial_si_vacio"]

    fecha_inicial_config = datetime.strptime(
        fecha_inicial_str,
        "%Y-%m-%d",
    ).date()

    usuarios = config["usuarios"]
    datasets = config["datasets"]
    web_config = config["web"]
    login_retries = web_config.get("login_retries", 3)

    download_dir = config["paths"]["download_dir"]
    headless = resolver_headless(mode)
    logger.info("Modo de ejecución: %s | Headless: %s", mode, headless)
    driver = iniciar_driver(download_dir, headless=headless)

    for usuario in usuarios:
        maestro_path = usuario["maestro_path"]
        logger.info("Procesando usuario: %s", usuario["nombre"])

        login(
            driver,
            web_config["login_url"],
            usuario["username"],
            usuario["password"],
            max_retries=login_retries,
        )

        for dataset in datasets:
            rango = procesar_dataset(
                maestro_path,
                dataset,
                fecha_inicial_config,
                logger,
            )

            if rango is None:
                continue

            fecha_desde, fecha_hasta = rango

            usuario_archivo, df_final = descargar_y_leer_dataset(
                driver,
                dataset,
                fecha_desde,
                fecha_hasta,
                download_dir,
                config["paths"]["procesados_dir"],
                logger,
            )

            if df_final is None or df_final.empty:
                logger.info(
                    "%s -> No hay fechas nuevas para procesar.",
                    dataset["nombre"],
                )
                continue

            if usuario_archivo != usuario["nombre"]:
                raise Exception(
                    f"El archivo pertenece a {usuario_archivo} pero se esperaba {usuario['nombre']}"
                )

            df_final, resumen = normalizar_y_validar_dataset(
                df_final,
                dataset["columna_fecha"],
                dataset["columnas_importe"],
                logger=logger,
            )

            logger.info("Archivo válido para usuario %s", usuario_archivo)
            logger.info("Total filas unificadas: %s", len(df_final))
            logger.info("Resumen de validaciones:")
            logger.info("%s", resumen)

            hoja_creada = ensure_sheet_exists_with_headers(
                maestro_path=maestro_path,
                hoja_destino=dataset["hoja_destino"],
                headers=list(df_final.columns),
                columna_inicio=dataset["columna_inicio"],
            )

            if hoja_creada:
                logger.info(
                    "Se creó la hoja '%s' con encabezados tomados del dataset.",
                    dataset["hoja_destino"],
                )

            resultado_insert = append_dataframe_to_excel(
                maestro_path=maestro_path,
                hoja_destino=dataset["hoja_destino"],
                df=df_final,
                columna_inicio=dataset["columna_inicio"],
            )

            if dataset["tiene_formulas"]:
                estirar_formulas(
                    maestro_path=maestro_path,
                    hoja_destino=dataset["hoja_destino"],
                    fila_inicio=resultado_insert["fila_inicio"],
                    filas_insertadas=resultado_insert["filas_insertadas"],
                )

            logger.info(
                "%s -> %s filas insertadas desde fila %s",
                dataset["nombre"],
                resultado_insert["filas_insertadas"],
                resultado_insert["fila_inicio"],
            )

        logout(driver, web_config["logout_url"])

    driver.quit()

    return download_dir


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["manual", "auto"], default="manual")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logger = setup_logger()
    try:
        download_dir = main_proceso(mode=args.mode)
        limpiar_download_temp(download_dir)
        logger.info("Proceso finalizado correctamente.")
        notificar_windows(success=True)
        sys.exit(0)
    except AuthenticationError:
        logger.error("Error de autenticación: verifique usuario y contraseña en config.json")
        print("ERROR: Problema de autenticación. Revise usuario/contraseña en config.json.")
        notificar_windows(success=False)
        sys.exit(1)
    except SiteUnavailableError as exc:
        logger.error("Error de disponibilidad del sitio: %s", exc)
        print("ERROR: La web no responde o está caída. Revise el archivo de log para más detalles.")
        notificar_windows(success=False)
        sys.exit(1)
    except DownloadBlockedError as exc:
        logger.error("Descarga bloqueada por Chrome: %s", exc)
        print("ERROR: Chrome bloqueó la descarga automática. Revise el archivo de log para más detalles.")
        notificar_windows(success=False)
        sys.exit(1)
    except MasterExcelArrayFormulaError as exc:
        logger.error(str(exc))
        print("ERROR: El Excel maestro tiene fórmulas array en la última fila. Revise y vuelva a ejecutar.")
        notificar_windows(success=False)
        sys.exit(1)
    except Exception:
        logger.exception("Error inesperado durante la ejecución.")
        print("ERROR: Ocurrió un error inesperado. Revise el archivo de log para más detalles.")
        notificar_windows(success=False)
        sys.exit(1)
