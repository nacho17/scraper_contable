from datetime import timedelta


def dividir_en_bloques(fecha_desde, fecha_hasta, max_dias=60):
    bloques = []

    inicio = fecha_desde

    while inicio <= fecha_hasta:
        fin = min(inicio + timedelta(days=max_dias - 1), fecha_hasta)
        bloques.append((inicio, fin))
        inicio = fin + timedelta(days=1)

    return bloques
