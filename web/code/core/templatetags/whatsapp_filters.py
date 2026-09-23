import re

from django import template

register = template.Library()

CODIGO_PAIS_EC = "593"


@register.filter
def whatsapp_link(contacto):
    """Genera un enlace de wa.me si `contacto` es un celular ecuatoriano.

    Los campos de contacto del sistema son de texto libre (teléfono o
    correo), así que este filtro solo reconoce números celulares y
    devuelve None para cualquier otro valor (p. ej. un correo), para que
    la plantilla pueda omitir el botón con `{% if %}`.

    Acepta formatos comunes: "0991234567", "991234567", "593991234567"
    o "+593991234567" (con o sin espacios/guiones).
    """
    if not contacto:
        return None
    digitos = re.sub(r"\D", "", str(contacto))
    if digitos.startswith(CODIGO_PAIS_EC) and len(digitos) == 12:
        digitos = digitos[len(CODIGO_PAIS_EC) :]
    elif digitos.startswith("0") and len(digitos) == 10:
        digitos = digitos[1:]
    if len(digitos) == 9 and digitos.startswith("9"):
        return f"https://wa.me/{CODIGO_PAIS_EC}{digitos}"
    return None
