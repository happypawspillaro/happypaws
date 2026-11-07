import logging

from constants import CANTONES, N_MAXIMO_OBJETOS_POR_PAGINA, PARROQUIAS_CANTON
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db.models import Model, QuerySet
from django.http import HttpRequest

logger = logging.getLogger(__name__)


def componer_ubicacion_display(
    instancia: Model,
    campo_canton: str = "canton",
    campo_parroquia: str = "parroquia",
) -> str:
    """Genera una cadena formateada con los nombres legibles (display values) de la ubicación.

    Args:
        instancia (Model): Instancia del modelo Django que contiene los campos de ubicación.
        campo_canton (str, optional): Nombre del campo 'cantón' en el modelo. Defaults to "canton".
        campo_parroquia (str, optional): Nombre del campo 'parroquia' en el modelo.
            Defaults to "parroquia".

    Returns:
        str: Ubicación formateada como 'Cantón / Parroquia' o 'Cantón / Parroquia
        / Barrio'.
    """
    # Obtiene el valor legible usando getattr de forma dinámica
    canton = getattr(instancia, f"get_{campo_canton}_display")()
    parroquia = getattr(instancia, f"get_{campo_parroquia}_display")()

    ubicacion = f"{canton} / {parroquia}"

    if instancia.barrio:  # Verifica que el barrio no esté vacío en la base de datos
        ubicacion += f" / {instancia.barrio}"

    return ubicacion


def obtener_diccionario_de_choices(choices: list[tuple[str, str]]) -> dict:
    """Convierte un iterable de Django Model Choices a un diccionario
    donde la clave es el nombre en formato humano y el valor el que requiere el modelo.

    Args:
        choices (list[tuple[str, str]]): Tu lista de tuplas que ingresas como `choices` en `djago.models`

    Returns:
        dict: Tupla termino humano y el de db
    """
    return {db: humano for humano, db in choices}


def obtener_parroquias_choices_dict_por_canton() -> dict:
    """Debido a que hay parroquias con los mismos nombres, usar `PARROQUIAS_CANTON`
    para returnar los valores por cantón.

    Returns:
        dict: Obtener los choices en formato humano: db
    """

    return {canton_db: obtener_diccionario_de_choices(PARROQUIAS_CANTON[canton_db]) for canton_db, _ in CANTONES}


def obtener_paginador(request: HttpRequest, lista_objetos: QuerySet) -> Page:
    """Función robusta para generar un paginador robusto

    Args:
        request (HttpRequest): El `request` de tu vista, donde tienes el query string.
        lista_objetos (QuerySet): Tu lista de objetos que deseas paginar.

    Returns:
        Page: Tu página de acuerdo al query o la primera o última si hay un error.
    """
    paginador = Paginator(lista_objetos, N_MAXIMO_OBJETOS_POR_PAGINA)
    numero_pagina = request.GET.get("page", 1)
    try:
        pag_objetos = paginador.page(numero_pagina)
    except PageNotAnInteger:
        logger.warning("El número de página: %s no es un valor válido, mostrando la primera página", numero_pagina)
        pag_objetos = paginador.page(1)
    except EmptyPage:
        pag_objetos = paginador.page(paginador.num_pages)
        logger.warning(
            "Página: %s esta sobre el máximo número de página: %d, mostrando la última página",
            numero_pagina,
            paginador.num_pages,
        )

    return pag_objetos
