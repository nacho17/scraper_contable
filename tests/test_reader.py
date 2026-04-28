from datetime import date

import pandas as pd
import pytest

from utils.reader import (
    _hay_indicio_descarga_bloqueada,
    esperar_descarga_completa,
    leer_archivo_descargado,
    mover_y_renombrar,
)
from web.downloader import DownloadBlockedError


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


def test_detecta_descarga_bloqueada_por_archivo_unconfirmed():
    assert _hay_indicio_descarga_bloqueada({"Unconfirmed 12345.crdownload"}) is True
    assert _hay_indicio_descarga_bloqueada({"archivo.xls"}) is False


def test_esperar_descarga_completa_identifica_bloqueo_de_chrome(tmp_path):
    archivo_bloqueado = tmp_path / "Unconfirmed 12345.crdownload"
    archivo_bloqueado.write_text("bloqueado", encoding="utf-8")

    with pytest.raises(DownloadBlockedError):
        esperar_descarga_completa(str(tmp_path), set(), timeout=0)
