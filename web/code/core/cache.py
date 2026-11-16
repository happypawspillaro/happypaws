import json
import logging
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders

logger = logging.getLogger(__name__)


def obtener_ruta_json(ruta_archivo: str) -> Path:
    ruta = finders.find(ruta_archivo)

    if ruta:
        return Path(ruta)

    return settings.DATA_DIR / ruta_archivo


@lru_cache(maxsize=4)
def _cargar_archivo_cached(
    ruta_locaciones: Path,
    mtime_ns: int,
) -> dict:
    logger.info("Cargando locaciones desde %s con mtime: %ld", ruta_locaciones, mtime_ns)

    with ruta_locaciones.open("r", encoding="utf-8") as f:
        return json.load(f)


def obtener_diccionario_json(ruta_archivo: str) -> dict:
    ruta_json = obtener_ruta_json(ruta_archivo)
    try:
        stat = ruta_json.stat()

        return _cargar_archivo_cached(
            ruta_json,
            stat.st_mtime_ns,
        )

    except (FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        logger.error(
            "Error al cargar el archivo desde %s: %s",
            ruta_json,
            exc,
        )
        return {}
