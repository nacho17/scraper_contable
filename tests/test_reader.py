from datetime import date

import pandas as pd
import pytest

from utils.reader import leer_archivo_descargado, mover_y_renombrar, esperar_descarga_completa


def test_leer_archivo_descargado_desde_xlsx(tmp_path):
    archivo = tmp_path / "dataset.xlsx"

    filas = [
        ["Cliente: Juan Perez", None],
        [None, None],
        [None, None],
        ["Fecha", "Importe"],
        ["01/01/2026", "1.000,00"],
        ["02/01/2026", "500,50"],
    ]

    pd.DataFrame(filas).to_excel(archivo, index=False, header=False)

    usuario, df = leer_archivo_descargado(str(archivo))

    assert usuario == "Juan Perez"
    assert list(df.columns) == ["Fecha", "Importe"]
    assert len(df) == 2


def test_mover_y_renombrar_mueve_y_nombra_archivo(tmp_path):
    origen = tmp_path / "origen.xls"
    origen.write_text("contenido", encoding="utf-8")

    destino_dir = tmp_path / "procesados"
    nuevo_path = mover_y_renombrar(
        str(origen),
        str(destino_dir),
        "FACTURADOS",
        "JUAN",
        date(2026, 1, 1),
        date(2026, 1, 2),
    )

    assert (destino_dir / "FACTURADOS_JUAN_2026-01-01_2026-01-02.xls").exists()
    assert nuevo_path.endswith("FACTURADOS_JUAN_2026-01-01_2026-01-02.xls")
    assert not origen.exists()


def test_esperar_descarga_completa_timeout_en_directorio_vacio(tmp_path):
    with pytest.raises(TimeoutError):
        esperar_descarga_completa(str(tmp_path), set(), timeout=1)
