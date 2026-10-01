import re

from django import template

register = template.Library()

CODIGO_PAIS_EC = "593"
# Celular ecuatoriano (9 dígitos, empieza en 9), con o sin "0" inicial o "593".
PATRON_CELULAR_EC = re.compile(r"^(?:593|0)?(9\d{8})$")


@register.filter
def whatsapp_link(contacto: str | int | None) -> str | None:
    """Genera un enlace de wa.me si `contacto` es un celular ecuatoriano.

    Los campos de contacto del sistema son de texto libre (teléfono o
    correo), así que este filtro solo reconoce números celulares y
    devuelve None para cualquier otro valor (p. ej. un correo), para que
    la plantilla pueda omitir el botón con `{% if %}`.

    Acepta formatos comunes: "0991234567", "991234567", "593991234567"
    o "+593991234567" (con o sin espacios/guiones).
    """
    if contacto is None:
        return None
    if isinstance(contacto, int):
        contacto = str(contacto)
    digitos = re.sub(r"\D", "", contacto)
    coincidencia = PATRON_CELULAR_EC.match(digitos)
    if coincidencia:
        return f"https://wa.me/{CODIGO_PAIS_EC}{coincidencia.group(1)}"
    return None
