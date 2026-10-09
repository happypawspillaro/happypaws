from django.db.models import Model


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
