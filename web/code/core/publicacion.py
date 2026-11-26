"""Arma el texto de una publicación para Facebook e Instagram (#39).

Esas redes no aceptan negrillas con formato, así que se usan las letras en
negrita de Unicode (𝗮𝘀𝗶́). Solo van en las etiquetas cortas: los lectores de
pantalla las leen mal y no conviene usarlas en párrafos enteros.
"""

import unicodedata

from django.utils.dateformat import format as formatear_fecha

# Hashtags que lleva toda publicación; luego se suman los del tipo.
HASHTAGS_BASE = ("#HappyPawsPíllaro", "#Píllaro", "#Tungurahua", "#Ecuador")

_DESPLAZAMIENTOS = (
    ("A", "Z", 0x1D5D4),  # 𝗔
    ("a", "z", 0x1D5EE),  # 𝗮
    ("0", "9", 0x1D7EC),  # 𝟬
)


def _letra_negrita(caracter: str) -> str:
    for inicio, fin, base in _DESPLAZAMIENTOS:
        if inicio <= caracter <= fin:
            return chr(base + ord(caracter) - ord(inicio))
    return caracter


def negrita(texto: str) -> str:
    """Pasa el texto a negrita de Unicode. Las tildes y la ñ se conservan como marcas combinadas."""
    descompuesto = unicodedata.normalize("NFD", texto)
    return "".join(_letra_negrita(c) for c in descompuesto)


def _fecha(valor) -> str:
    return formatear_fecha(valor, r"j \d\e F \d\e Y")


def _dato(emoji: str, etiqueta: str, valor: str) -> str | None:
    valor = (valor or "").strip()
    return f"{emoji} {negrita(etiqueta + ':')} {valor}" if valor else None


def _unir(*bloques) -> str:
    """Une bloques con una línea en blanco; cada bloque puede ser texto o lista de líneas."""
    partes = []
    for bloque in bloques:
        if isinstance(bloque, (list, tuple)):
            bloque = "\n".join(linea for linea in bloque if linea)
        bloque = (bloque or "").strip()
        if bloque:
            partes.append(bloque)
    return "\n\n".join(partes)


def _hashtags(*extra: str) -> str:
    return " ".join(dict.fromkeys(extra + HASHTAGS_BASE))


def texto_reporte(reporte, url: str) -> str:
    from reports.models import TipoReporte

    encabezados = {
        TipoReporte.PERDIDO: ("🚨", "MASCOTA PERDIDA", "Si la has visto, avísanos. ¡Compartir también ayuda! 🙏"),
        TipoReporte.ENCONTRADO: ("🏠", "MASCOTA ENCONTRADA", "¿Es tu mascota o sabes de quién es? Escríbenos 🙏"),
        TipoReporte.MALTRATO: (
            "⚠️",
            "MALTRATO O ABANDONO",
            "Si tienes información, escríbenos. Tu reporte es confidencial.",
        ),
    }
    hashtags = {
        TipoReporte.PERDIDO: ("#MascotaPerdida", "#AyúdaloAVolverACasa"),
        TipoReporte.ENCONTRADO: ("#MascotaEncontrada", "#BuscamosASuFamilia"),
        TipoReporte.MALTRATO: ("#NoAlMaltratoAnimal",),
    }
    emoji, titulo, llamado = encabezados.get(reporte.tipo, ("🐾", reporte.get_tipo_display().upper(), ""))

    fecha = _fecha(reporte.fecha_avistamiento)
    if reporte.hora_aproximada:
        fecha += f", {reporte.hora_aproximada:%H:%M} aprox."
    animal = " · ".join(
        valor
        for valor in (reporte.get_especie_display(), reporte.get_sexo_display())
        if valor and valor != "Desconocido"
    )

    return _unir(
        f"{emoji} {negrita(titulo)} {emoji}",
        reporte.titulo,
        [
            _dato("📍", "Ubicación", reporte.ubicacion_completa),
            _dato("📅", "Fecha", fecha),
            _dato("🐾", "Animal", animal),
            _dato("🔎", "Señales", reporte.senales_distinguibles),
        ],
        reporte.descripcion,
        llamado,
        f"🔗 Más información: {url}",
        _hashtags(*hashtags.get(reporte.tipo, ())),
    )


def texto_animal(animal, url: str) -> str:
    hembra = animal.sexo == "hembra"
    if animal.en_adopcion:
        encabezado = f"🏡 {negrita('EN ADOPCIÓN')} 🏡"
        presentacion = f"{negrita(animal.nombre)} busca un hogar que {'la' if hembra else 'lo'} quiera para siempre 💛"
        llamado = f"📝 Llena la solicitud de adopción aquí: {url}"
        extra = ("#AdoptaNoCompres", "#Adopción")
    else:
        encabezado = f"🐾 {negrita('CONOCE A ' + animal.nombre.upper())} 🐾"
        presentacion = f"Estado: {animal.get_estado_display().lower()}."
        llamado = f"🔗 Conoce su historia: {url}"
        extra = ()

    perfil = " · ".join(
        valor
        for valor in (
            animal.get_especie_display(),
            animal.get_sexo_display() if animal.sexo != "desconocido" else "",
            animal.get_tamano_display(),
            animal.edad_aprox,
        )
        if valor
    )
    return _unir(
        encabezado,
        presentacion,
        [
            _dato("🐾", "Perfil", perfil),
            _dato("💉", "Esterilizada" if hembra else "Esterilizado", "Sí ✅" if animal.esterilizado else ""),
            _dato("📍", "Ubicación", animal.ubicacion_completa),
        ],
        animal.descripcion,
        llamado,
        _hashtags(*extra),
    )
