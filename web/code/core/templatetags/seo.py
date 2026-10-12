from core.seo import MARCA
from django import template

register = template.Library()


@register.filter
def con_marca(texto: str) -> str:
    """'Adopta a Luna de La Matriz/Píllaro | Happy Paws Píllaro' (#66)."""
    return f"{texto} | {MARCA}"


@register.simple_tag(takes_context=True)
def url_absoluta(context, url: str) -> str:
    """URL con esquema y dominio para og:url, og:image y canonical.

    Los crawlers de WhatsApp, Facebook y Telegram no resuelven rutas relativas
    (#68). Se arma con el dominio de la petición, igual que el sitemap.xml.
    """
    return context["request"].build_absolute_uri(url)
