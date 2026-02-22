from datetime import date

from utils.dates import dividir_en_bloques


def test_dividir_en_bloques_rango_largo():
    bloques = dividir_en_bloques(
        date(2026, 1, 1),
        date(2026, 3, 5),
        max_dias=30,
    )

    assert bloques == [
        (date(2026, 1, 1), date(2026, 1, 30)),
        (date(2026, 1, 31), date(2026, 3, 1)),
        (date(2026, 3, 2), date(2026, 3, 5)),
    ]


def test_dividir_en_bloques_rango_invalido_devuelve_vacio():
    bloques = dividir_en_bloques(date(2026, 2, 1), date(2026, 1, 1))
    assert bloques == []
