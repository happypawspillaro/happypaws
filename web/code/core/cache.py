import json
import logging
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders

logger = logging.getLogger(__name__)


def obtener_ruta_locaciones() -> Path:
    ruta = finders.find("data/locaciones.json")

    if ruta:
        return Path(ruta)

    return settings.DATA_DIR / "data" / "locaciones.json"


@lru_cache(maxsize=4)
def _cargar_locaciones_cached(
    ruta_locaciones: Path,
    mtime_ns: int,
) -> dict:
    logger.info("Cargando locaciones desde %s con mtime: %ld", ruta_locaciones, mtime_ns)

    with ruta_locaciones.open("r", encoding="utf-8") as f:
        return json.load(f)


def obtener_locaciones() -> dict:
    ruta_locaciones = obtener_ruta_locaciones()
    try:
        stat = ruta_locaciones.stat()

        return _cargar_locaciones_cached(
            ruta_locaciones,
            stat.st_mtime_ns,
        )

    except (FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        logger.error(
            "Error al cargar locaciones desde %s: %s",
            ruta_locaciones,
            exc,
        )
        return {}
