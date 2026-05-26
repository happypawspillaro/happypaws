"""Avisos por correo cuando alguien interactúa con un reporte."""

from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def _es_email(valor):
    if not valor:
        return False
    try:
        validate_email(valor.strip())
    except ValidationError:
        return False
    return True


def _destinatarios(reporte):
    """Reportante (si dejó un correo) + correo de la fundación, sin repetir."""
    destinatarios = []
    contacto = (reporte.contacto_reportante or "").strip()
    if _es_email(contacto):
        destinatarios.append(contacto)
    fundacion = getattr(settings, "FOUNDATION_EMAIL", "")
    if fundacion and fundacion not in destinatarios:
        destinatarios.append(fundacion)
    return destinatarios


def notify_report_activity(reporte, tipo, objeto, request=None):
    """Notifica un nuevo comentario o avistamiento.

    ``tipo`` es ``"comentario"`` o ``"avistamiento"``. Falla en silencio: un
    problema de correo nunca debe romper el envío del usuario.
    """
    destinatarios = _destinatarios(reporte)
    if not destinatarios:
        return

    ruta = reporte.get_absolute_url()
    url = request.build_absolute_uri(ruta) if request is not None else ruta

    if tipo == "avistamiento":
        asunto = f"Nuevo avistamiento en «{reporte.titulo}»"
        detalle = f"{objeto.nombre} reportó haberlo visto en {objeto.ubicacion} ({objeto.fecha})."
    else:
        asunto = f"Nuevo comentario en «{reporte.titulo}»"
        detalle = f"{objeto.nombre} escribió:\n\n{objeto.mensaje}"

    cuerpo = (
        f"Hola,\n\nHay nueva actividad en tu reporte «{reporte.titulo}».\n\n"
        f"{detalle}\n\n"
        f"Puedes verlo aquí: {url}\n\n"
        "— Happy Paws Píllaro"
    )

    send_mail(
        asunto,
        cuerpo,
        settings.DEFAULT_FROM_EMAIL,
        destinatarios,
        fail_silently=True,
    )
