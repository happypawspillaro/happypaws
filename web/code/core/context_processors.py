from django.conf import settings


def analiticas(request):
    """Measurement ID de GA4 para base.html (#58).

    No se mide al equipo de la fundación para no inflar las visitas con su
    propio trabajo en el panel.
    """
    usuario = getattr(request, "user", None)
    if usuario is not None and usuario.is_staff:
        return {"ga_measurement_id": ""}
    return {"ga_measurement_id": settings.GA_MEASUREMENT_ID}
