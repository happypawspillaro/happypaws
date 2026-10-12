"""Textos para buscadores y redes sociales: <title>, <h1>, alt y OpenGraph.

Cada modelo público (Animal, MedicalCase, Report) expone un `titulo_seo` con
el formato que acordamos en el #66/#68: qué se busca + quién + dónde. Las
plantillas le agregan la marca con el filtro `con_marca` (core/templatetags/seo.py).
"""

MARCA = "Happy Paws Píllaro"
# Por ahora todos los registros son del cantón Píllaro.
CANTON_POR_DEFECTO = "Píllaro"


def ubicacion_seo(parroquia: str = "", canton: str = CANTON_POR_DEFECTO) -> str:
    """'Parroquia/Cantón', o solo el cantón si no hay parroquia.

    Cuando entre el #62 (cantón y parroquia como listas), los modelos
    solo tienen que pasar aquí sus get_parroquia_display()/get_canton_display().
    """
    parroquia = (parroquia or "").strip()
    return f"{parroquia}/{canton}" if parroquia else canton
