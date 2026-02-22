import logging
import os
from datetime import datetime
from typing import Union


def _resolver_nivel(nivel: Union[int, str, None]) -> int:
    if isinstance(nivel, int):
        return nivel

    nivel_str = nivel or os.getenv("LOG_LEVEL", "INFO")
    if isinstance(nivel_str, str):
        resolved = getattr(logging, nivel_str.upper(), None)
        if isinstance(resolved, int):
            return resolved

    return logging.INFO


def setup_logger(
    nombre_logger: str = "scraper_contable",
    log_dir: str = "logs",
    nivel: Union[int, str, None] = None
) -> logging.Logger:
    """
    Configura y devuelve un logger reutilizable para el proyecto.

    - Nivel configurable por argumento o variable LOG_LEVEL
    - Log por consola
    - Log a archivo con fecha
    - Evita duplicar handlers si se llama m?s de una vez
    """

    nivel_resuelto = _resolver_nivel(nivel)

    logger = logging.getLogger(nombre_logger)
    logger.setLevel(nivel_resuelto)
    logger.propagate = False

    # Evitar agregar handlers m?ltiples veces
    if logger.handlers:
        for handler in logger.handlers:
            handler.setLevel(nivel_resuelto)
        return logger

    # Crear carpeta logs si no existe
    os.makedirs(log_dir, exist_ok=True)

    # Nombre archivo con fecha
    fecha_str = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{nombre_logger}_{fecha_str}.log")

    # Formatter com?n
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(nivel_resuelto)
    console_handler.setFormatter(formatter)

    # Handler archivo
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(nivel_resuelto)
    file_handler.setFormatter(formatter)

    # Agregar handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
