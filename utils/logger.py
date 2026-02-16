import logging
import os
from datetime import datetime


def setup_logger(
    nombre_logger: str = "scraper_contable",
    log_dir: str = "logs",
    nivel: int = logging.INFO
) -> logging.Logger:
    """
    Configura y devuelve un logger reutilizable para el proyecto.

    - Log por consola
    - Log a archivo con fecha
    - Evita duplicar handlers si se llama más de una vez
    """

    logger = logging.getLogger(nombre_logger)
    logger.setLevel(nivel)

    # Evitar agregar handlers múltiples veces
    if logger.handlers:
        return logger

    # Crear carpeta logs si no existe
    os.makedirs(log_dir, exist_ok=True)

    # Nombre archivo con fecha
    fecha_str = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{nombre_logger}_{fecha_str}.log")

    # Formatter común
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Handler archivo
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Agregar handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
