"""Sugiere qué reportes de mascotas perdidas y encontradas podrían ser el mismo animal.

Es una ayuda para que las personas comparen, no una identificación: cada sugerencia
lleva los motivos que la explican y nunca cambia el estado de un reporte.
"""

import re
import unicodedata
from dataclasses import dataclass
from datetime import timedelta

from constants import Sexo

from .models import EstadoReporte, Report, TipoReporte

TIPO_OPUESTO = {
    TipoReporte.PERDIDO: TipoReporte.ENCONTRADO,
    TipoReporte.ENCONTRADO: TipoReporte.PERDIDO,
}

# Una mascota no puede encontrarse antes de perderse, pero las fechas que pone
# la gente son aproximadas.
DIAS_TOLERANCIA = 2
DIAS_MAXIMOS = 90

# Mismo sexo y parroquia no bastan (55): hace falta cercanía en fecha o algún rasgo.
PUNTAJE_MINIMO = 60
MAXIMO_SUGERENCIAS = 3

PUNTOS_ESPECIE = 15
PUNTOS_SEXO = 15
PUNTOS_CANTON = 10
PUNTOS_PARROQUIA = 25
PUNTOS_BARRIO = 10
PUNTOS_POR_RASGO = 15
MAXIMO_RASGOS = 3
# (días de diferencia, puntos)
PUNTOS_FECHA = ((7, 20), (30, 10), (DIAS_MAXIMOS, 0))

# Solo palabras que describen al animal. Con una lista cerrada, los nombres de
# lugares, los saludos o los teléfonos de la descripción no suman puntos.
# Cada palabra apunta a la forma que se muestra en los motivos.
_RASGOS = {
    "negro": ("negro", "negra", "negrito", "negrita"),
    "blanco": ("blanco", "blanca", "blanquito", "blanquita"),
    "café": ("cafe", "marron", "chocolate"),
    "gris": ("gris", "plomo", "ploma"),
    "crema": ("crema", "beige"),
    "amarillo": ("amarillo", "amarilla", "dorado", "dorada"),
    "naranja": ("naranja", "anaranjado", "anaranjada"),
    "atigrado": ("atigrado", "atigrada"),
    "cálico": ("calico", "tricolor"),
    "manchas": ("mancha", "manchas", "manchado", "manchada", "moteado", "moteada"),
    "collar": ("collar",),
    "saco": ("saco", "chompa", "chaleco"),
    "cicatriz": ("cicatriz", "cicatrices"),
    "cojea": ("cojea", "coja", "cojo"),
    "husky": ("husky", "huskey", "huski"),
    "bulldog": ("bulldog", "buldog"),
    "pug": ("pug",),
    "pequinés": ("pequines", "pekines"),
    "golden": ("golden",),
    "labrador": ("labrador", "labradora"),
    "pastor": ("pastor",),
    "pitbull": ("pitbull",),
    "rottweiler": ("rottweiler", "rotweiler"),
    "schnauzer": ("schnauzer",),
    "french poodle": ("poodle", "puddle"),
    "shih tzu": ("shih", "shitzu"),
    "chihuahua": ("chihuahua",),
    "mestizo": ("mestizo", "mestiza"),
    "siamés": ("siames", "siamesa"),
}
_RASGO_POR_PALABRA = {palabra: rasgo for rasgo, palabras in _RASGOS.items() for palabra in palabras}


@dataclass(frozen=True)
class Coincidencia:
    reporte: Report
    puntaje: int
    motivos: tuple[str, ...]


def _normalizar(texto: str | None) -> str:
    """Minúsculas, sin tildes y con las letras decorativas de redes sociales hechas normales."""
    texto = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in texto if not unicodedata.combining(c)).casefold().strip()


def obtener_rasgos(reporte: Report) -> set[str]:
    texto = _normalizar(f"{reporte.titulo} {reporte.senales_distinguibles} {reporte.descripcion}")
    palabras = re.findall(r"[a-z]+", texto)
    return {_RASGO_POR_PALABRA[p] for p in palabras if p in _RASGO_POR_PALABRA}


def _puntos_ubicacion(a: Report, b: Report) -> tuple[int, str | None]:
    # Los códigos de parroquia se repiten entre cantones, por eso van juntos.
    if a.canton != b.canton:
        return 0, None
    if a.parroquia != b.parroquia:
        return PUNTOS_CANTON, f"mismo cantón ({a.get_canton_display()})"
    barrio = _normalizar(a.barrio)
    if barrio and barrio == _normalizar(b.barrio):
        return PUNTOS_PARROQUIA + PUNTOS_BARRIO, f"mismo barrio ({a.barrio.strip()})"
    return PUNTOS_PARROQUIA, f"misma parroquia ({a.get_parroquia_display()})"


def _puntos_fecha(dias: int) -> tuple[int, str]:
    if dias == 0:
        motivo = "el mismo día"
    else:
        motivo = f"{dias} día{'' if dias == 1 else 's'} de diferencia"
    return next(puntos for limite, puntos in PUNTOS_FECHA if dias <= limite), motivo


def comparar(a: Report, b: Report) -> Coincidencia | None:
    """Compara el reporte ``a`` con el candidato ``b``. ``None`` si no se parecen lo suficiente."""
    if not a.especie or a.especie != b.especie:
        return None
    puntaje, motivos = PUNTOS_ESPECIE, [a.get_especie_display().lower()]

    sexos = {a.sexo, b.sexo}
    if not sexos & {"", Sexo.DESCONOCIDO}:
        if len(sexos) > 1:
            return None
        puntaje += PUNTOS_SEXO
        motivos.append(a.get_sexo_display().lower())

    puntos, motivo = _puntos_ubicacion(a, b)
    puntaje += puntos
    if motivo:
        motivos.append(motivo)

    puntos, motivo = _puntos_fecha(abs((a.fecha_avistamiento - b.fecha_avistamiento).days))
    puntaje += puntos
    motivos.append(motivo)

    rasgos = sorted(obtener_rasgos(a) & obtener_rasgos(b))[:MAXIMO_RASGOS]
    if rasgos:
        puntaje += PUNTOS_POR_RASGO * len(rasgos)
        motivos.append("en común: " + ", ".join(rasgos))

    if puntaje < PUNTAJE_MINIMO:
        return None
    return Coincidencia(reporte=b, puntaje=puntaje, motivos=tuple(motivos))


def buscar_coincidencias(reporte: Report, incluir_sin_aprobar: bool = False) -> list[Coincidencia]:
    """Devuelve los reportes del tipo opuesto que más se parecen, del más al menos parecido.

    Args:
        reporte (Report): Reporte que se está viendo.
        incluir_sin_aprobar (bool): Solo para el staff; el público no debe ver
            reportes que aún no pasan la moderación.
    """
    opuesto = TIPO_OPUESTO.get(reporte.tipo)
    if opuesto is None or reporte.estado != EstadoReporte.ABIERTO or not reporte.especie:
        return []

    fecha = reporte.fecha_avistamiento
    antes, despues = timedelta(days=DIAS_TOLERANCIA), timedelta(days=DIAS_MAXIMOS)
    if reporte.tipo == TipoReporte.PERDIDO:
        rango = (fecha - antes, fecha + despues)
    else:
        rango = (fecha - despues, fecha + antes)

    candidatos = Report.objects.filter(
        tipo=opuesto,
        estado=EstadoReporte.ABIERTO,
        especie=reporte.especie,
        fecha_avistamiento__range=rango,
    ).prefetch_related("fotos")
    if not incluir_sin_aprobar:
        candidatos = candidatos.filter(aprobado=True)

    coincidencias = [c for c in (comparar(reporte, candidato) for candidato in candidatos) if c]
    coincidencias.sort(key=lambda c: c.puntaje, reverse=True)
    return coincidencias[:MAXIMO_SUGERENCIAS]
