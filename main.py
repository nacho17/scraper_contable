import json
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from excel.updater import append_dataframe_to_excel, estirar_formulas
from utils.logger import setup_logger
from utils.converter import normalizar_y_validar_dataset
from utils.dates import dividir_en_bloques
from web.downloader import (
    AuthenticationError,
    iniciar_driver,
    login,
    logout,
    exportar_dataset,
)
from utils.reader import leer_archivo_descargado, mover_y_renombrar, esperar_descarga_completa


def cargar_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def obtener_ultima_fecha(maestro_path, hoja_1, columna_fecha):
    try:
        df = pd.read_excel(
            maestro_path,
            sheet_name=hoja_1,
            engine="openpyxl"
        )
    except FileNotFoundError:
        raise Exception(f"No se encontr? el archivo: {maestro_path}")

    if columna_fecha not in df.columns:
        raise Exception(f"La columna '{columna_fecha}' no existe en la hoja '{hoja_1}'")

    # Convertir a datetime de forma segura
    df[columna_fecha] = pd.to_datetime(
        df[columna_fecha],
        dayfirst=True,
        errors="coerce"
    )

    # Eliminar fechas inv?lidas o vac?as
    df_valid = df[df[columna_fecha].notna()]

    if df_valid.empty:
        return None

    # Tomar la fecha m?xima
    ultima_fecha = df_valid[columna_fecha].max()

    return ultima_fecha


def procesar_dataset(
    maestro_path,
    dataset_config,
    fecha_inicial_config,
    logger
):
    nombre = dataset_config["nombre"]
    hoja_destino = dataset_config["hoja_destino"]
    columna_fecha = dataset_config["columna_fecha"]

    logger.info("Procesando dataset: %s", nombre)

    ultima_fecha = obtener_ultima_fecha(
        maestro_path,
        hoja_destino,
        columna_fecha
    )

    if ultima_fecha is None:
        logger.warning("Archivo vac?o o sin fechas v?lidas.")
        fecha_desde = fecha_inicial_config
    else:
        logger.info("?ltima fecha encontrada: %s", ultima_fecha.date())
        fecha_desde = (ultima_fecha + timedelta(days=1)).date()

    hoy = datetime.today().date()
    fecha_hasta = hoy - timedelta(days=1)

    logger.info("Fecha desde: %s", fecha_desde)
    logger.info("Fecha hasta: %s", fecha_hasta)

    if fecha_desde == fecha_hasta:
        logger.info("No hay nuevas fechas para procesar.")
        return None

    if fecha_desde > fecha_hasta:
        logger.warning(
            "Rango inv?lido: fecha_desde (%s) es mayor que fecha_hasta (%s). No se procesar? ning?n dataset.",
            fecha_desde,
            fecha_hasta
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
    logger
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
            sub_hasta
        )

        ultimo_archivo = esperar_descarga_completa(ruta_descargas, archivos_antes)

        logger.info("Archivo detectado: %s", ultimo_archivo)

        usuario_archivo, df_nuevo = leer_archivo_descargado(ultimo_archivo)

        logger.info("Filas de esta porci?n del dataset: %s", len(df_nuevo))

        if usuario_detectado is None:
            usuario_detectado = usuario_archivo

        # Validaci?n de coherencia
        if usuario_archivo != usuario_detectado:
            raise Exception("Inconsistencia en usuario detectado")

        dfs.append(df_nuevo)

        # Guardar archivo para trazabilidad
        nuevo_path = mover_y_renombrar(
            ultimo_archivo,
            procesados_dir,
            dataset["nombre"],
            usuario_archivo,
            sub_desde,
            sub_hasta
        )

        logger.info("Movido a: %s", nuevo_path)

    df_final = pd.concat(dfs, ignore_index=True)

    return usuario_detectado, df_final


def limpiar_download_temp(download_dir):
    for archivo in os.listdir(download_dir):
        ruta = os.path.join(download_dir, archivo)
        if os.path.isfile(ruta):
            os.remove(ruta)


def main_proceso():
    config = cargar_config()
    logger = setup_logger()

    maestro_path = config["excel"]["maestro_path"]
    fecha_inicial_str = config["procesamiento"]["fecha_inicial_si_vacio"]

    fecha_inicial_config = datetime.strptime(
        fecha_inicial_str,
        "%Y-%m-%d"
    ).date()

    usuarios = config["usuarios"]
    datasets = config["datasets"]
    web_config = config["web"]

    download_dir = config["paths"]["download_dir"]
    driver = iniciar_driver(download_dir)

    for usuario in usuarios:
        logger.info("Procesando usuario: %s", usuario["nombre"])

        login(
            driver,
            web_config["login_url"],
            usuario["username"],
            usuario["password"]
        )

        for dataset in datasets:
            rango = procesar_dataset(
                maestro_path,
                dataset,
                fecha_inicial_config,
                logger
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
                logger
            )

            if df_final is None or df_final.empty:
                logger.info(
                    "%s -> No hay fechas nuevas para procesar.",
                    dataset["nombre"]
                )
                continue

            # Validar usuario
            if usuario_archivo != usuario["nombre"]:
                raise Exception(
                    f"El archivo pertenece a {usuario_archivo} "
                    f"pero se esperaba {usuario['nombre']}"
                )

            df_final, resumen = normalizar_y_validar_dataset(
                df_final,
                dataset["columna_fecha"],
                dataset["columnas_importe"],
                logger=logger
            )

            logger.info("Archivo v?lido para usuario %s", usuario_archivo)
            logger.info("Total filas unificadas: %s", len(df_final))
            logger.info("Resumen de validaciones:")
            logger.info("%s", resumen)

            resultado_insert = append_dataframe_to_excel(
                maestro_path=config["excel"]["maestro_path"],
                hoja_destino=dataset["hoja_destino"],
                df=df_final,
                columna_inicio=dataset["columna_inicio"]
            )

            if dataset["tiene_formulas"]:
                estirar_formulas(
                    maestro_path=config["excel"]["maestro_path"],
                    hoja_destino=dataset["hoja_destino"],
                    fila_inicio=resultado_insert["fila_inicio"],
                    filas_insertadas=resultado_insert["filas_insertadas"]
                )

            # Log interno
            logger.info(
                "%s -> %s filas insertadas desde fila %s",
                dataset["nombre"],
                resultado_insert["filas_insertadas"],
                resultado_insert["fila_inicio"]
            )

        logout(driver, web_config["logout_url"])

    driver.quit()

    return download_dir


if __name__ == "__main__":
    logger = setup_logger()
    try:
        download_dir = main_proceso()
        limpiar_download_temp(download_dir)
        logger.info("Proceso finalizado correctamente.")
    except AuthenticationError:
        logger.error("Error de autenticación: verifique usuario y contraseña en config.json")
        print("ERROR: Problema de autenticación. Revise usuario/contraseña en config.json.")
        sys.exit(1)
    except Exception:
        logger.exception("Error inesperado durante la ejecución.")
        print("ERROR: Ocurrió un error inesperado. Revise el archivo de log para más detalles.")
        sys.exit(1)
