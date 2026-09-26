import json
import logging
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders

logger = logging.getLogger(__name__)


def obtener_ruta_locaciones() -> Path:
    ruta = finders.find("assets/locaciones.json")

    if ruta:
        return Path(ruta)

    return Path(settings.BASE_DIR) / "static" / "assets" / "locaciones.json"


@lru_cache(maxsize=4)
def _cargar_locaciones_cached(
    ruta: str,
    mtime_ns: int,
) -> dict:
    path = Path(ruta)

    logger.info("Cargando locaciones desde %s con mtime: %ld", path, mtime_ns)

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def obtener_locaciones() -> dict:
    path = obtener_ruta_locaciones()

    try:
        stat = path.stat()

        return _cargar_locaciones_cached(
            str(path),
            stat.st_mtime_ns,
        )

    except (FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        logger.error(
            "Error al cargar locaciones desde %s: %s",
            path,
            exc,
        )
        return {}
