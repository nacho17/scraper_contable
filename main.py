import json
import pandas as pd
import sys
from datetime import datetime, timedelta


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
        raise Exception(f"No se encontró el archivo: {maestro_path}")

    if columna_fecha not in df.columns:
        raise Exception(f"La columna '{columna_fecha}' no existe en la hoja '{hoja_1}'")

    # Convertir a datetime de forma segura
    df[columna_fecha] = pd.to_datetime(
        df[columna_fecha],
        format="%d/%m/%Y",
        errors="coerce"
    )


    # Eliminar fechas inválidas o vacías
    df_valid = df[df[columna_fecha].notna()]

    if df_valid.empty:
        return None

    # Tomar la fecha máxima
    ultima_fecha = df_valid[columna_fecha].max()

    return ultima_fecha

def procesar_dataset(
    maestro_path,
    dataset_config,
    fecha_inicial_config
):
    nombre = dataset_config["nombre"]
    hoja_destino = dataset_config["hoja_destino"]
    columna_fecha = dataset_config["columna_fecha"]

    print(f"\n🔎 Procesando dataset: {nombre}")

    ultima_fecha = obtener_ultima_fecha(
        maestro_path,
        hoja_destino,
        columna_fecha
    )

    if ultima_fecha is None:
        print("⚠️ Archivo vacío o sin fechas válidas.")
        fecha_desde = fecha_inicial_config
    else:
        print(f"✅ Última fecha encontrada: {ultima_fecha.date()}")
        fecha_desde = (ultima_fecha + timedelta(days=1)).date()

    hoy = datetime.today().date()
    fecha_hasta = hoy - timedelta(days=1)

    print(f"📅 Fecha desde: {fecha_desde}")
    print(f"📅 Fecha hasta: {fecha_hasta}")

    if fecha_desde > fecha_hasta:
        print("ℹ️ No hay nuevas fechas para procesar.")
        return None

    print("🚀 Hay fechas nuevas para procesar.")
    return fecha_desde, fecha_hasta


def main():
    config = cargar_config()

    maestro_path = config["excel"]["maestro_path"]
    fecha_inicial_str = config["procesamiento"]["fecha_inicial_si_vacio"]

    fecha_inicial_config = datetime.strptime(
        fecha_inicial_str,
        "%Y-%m-%d"
    ).date()

    datasets = config["datasets"]

    for dataset in datasets:
        rango = procesar_dataset(
            maestro_path=maestro_path,
            dataset_config=dataset,
            fecha_inicial_config=fecha_inicial_config
        )

        # Más adelante acá va:
        # - scraping
        # - borrar rango
        # - insertar datos
        # - extender formulas si corresponde

    print("\n🏁 Proceso finalizado.")


if __name__ == "__main__":
    main()
