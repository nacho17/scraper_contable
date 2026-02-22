import logging
from datetime import date, datetime

import pandas as pd
import pytest
from openpyxl import Workbook, load_workbook

import main
from excel.updater import append_dataframe_to_excel
from utils.converter import normalizar_y_validar_dataset


def test_normalizar_y_validar_dataset_ordena_y_transforma_importes():
    df = pd.DataFrame(
        {
            "fecha": ["03/01/2026", "01/01/2026", "invalida"],
            "importe": ["1.234,50", "100,00", "abc"],
        }
    )

    normalizado, resumen = normalizar_y_validar_dataset(
        df,
        col_fecha="fecha",
        columnas_importe=["importe"],
        logger=logging.getLogger("test"),
    )

    fechas_validas = [f.date() for f in normalizado["fecha"].dropna()]
    assert fechas_validas == [date(2026, 1, 1), date(2026, 1, 3)]
    assert resumen["fechas_invalidas"] == 1
    assert resumen["importes_invalidos"]["importe"] == 1
    assert float(normalizado.iloc[0]["importe"]) == 100.00
    assert float(normalizado.iloc[1]["importe"]) == 1234.50


def test_normalizar_y_validar_dataset_columnas_faltantes_no_rompe_flujo():
    df = pd.DataFrame({"otra_columna": [1, 2]})

    normalizado, resumen = normalizar_y_validar_dataset(
        df,
        col_fecha="fecha",
        columnas_importe=["importe_inexistente"],
        logger=logging.getLogger("test"),
    )

    assert "otra_columna" in normalizado.columns
    assert resumen["fechas_invalidas"] == 0
    assert resumen["importes_invalidos"] == {}


def test_append_dataframe_to_excel_detecta_ultima_fila_real(tmp_path):
    archivo = tmp_path / "maestro.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Datos"
    ws["A1"] = "Fecha"
    ws["B1"] = "Importe"
    ws["A2"] = "2026-01-01"
    ws["B2"] = 10
    ws["C5"] = "ruido"
    wb.save(archivo)

    df_nuevo = pd.DataFrame(
        [
            ["2026-01-02", 20],
            ["2026-01-03", 30],
        ],
        columns=["Fecha", "Importe"],
    )

    resultado = append_dataframe_to_excel(
        maestro_path=str(archivo),
        hoja_destino="Datos",
        df=df_nuevo,
        columna_inicio=1,
    )

    assert resultado["fila_inicio"] == 3
    assert resultado["filas_insertadas"] == 2

    wb_check = load_workbook(archivo)
    ws_check = wb_check["Datos"]
    assert ws_check["A3"].value == "2026-01-02"
    assert ws_check["B4"].value == 30


def test_append_dataframe_to_excel_hoja_inexistente_lanza_error(tmp_path):
    archivo = tmp_path / "maestro.xlsx"
    wb = Workbook()
    wb.save(archivo)

    with pytest.raises(ValueError):
        append_dataframe_to_excel(
            maestro_path=str(archivo),
            hoja_destino="NoExiste",
            df=pd.DataFrame([[1]], columns=["A"]),
            columna_inicio=1,
        )


def test_procesar_dataset_rango_invalido_devuelve_none(monkeypatch):
    class FixedDateTime(datetime):
        @classmethod
        def today(cls):
            return cls(2026, 1, 10)

    monkeypatch.setattr(main, "datetime", FixedDateTime)
    monkeypatch.setattr(main, "obtener_ultima_fecha", lambda *args, **kwargs: datetime(2026, 1, 20))

    dataset = {
        "nombre": "FACTURADOS",
        "hoja_destino": "Datos",
        "columna_fecha": "fecha",
    }

    resultado = main.procesar_dataset(
        maestro_path="dummy.xlsx",
        dataset_config=dataset,
        fecha_inicial_config=date(2025, 1, 1),
        logger=logging.getLogger("test"),
    )

    assert resultado is None
