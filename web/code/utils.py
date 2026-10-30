import logging

from constants import N_MAXIMO_OBJETOS_POR_PAGINA
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db.models import QuerySet
from django.http import HttpRequest

logger = logging.getLogger(__name__)


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
    except Exception:
        logger.exception("Hubo un error al procesar tu página: %s, mostrando la última página", numero_pagina)
        pag_objetos = paginador.page(paginador.num_pages)

    return pag_objetos
