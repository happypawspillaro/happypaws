from core.seo import MARCA
from django import template

register = template.Library()


@register.filter
def con_marca(texto: str) -> str:
    """'Adopta a Luna de La Matriz/Píllaro | Happy Paws Píllaro' (#66)."""
    return f"{texto} | {MARCA}"
