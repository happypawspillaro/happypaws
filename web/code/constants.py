from django.db import models

# Un animal comunitario esterilizado dentro de esta ventana se destaca automáticamente.
MESES_FEATURED_COMUNITARIO = 6

# Días que el contacto del reportante queda visible al público antes de
# ocultarse, para que bots no sigan extrayendo teléfonos/correos de
# reportes viejos (issue #34).
DIAS_CONTACTO_VISIBLE = 30


class Especie(models.TextChoices):
    PERRO = "perro", "Perro"
    GATO = "gato", "Gato"
    OTRO = "otro", "Otro"


class Sexo(models.TextChoices):
    MACHO = "macho", "Macho"
    HEMBRA = "hembra", "Hembra"
    DESCONOCIDO = "desconocido", "Desconocido"


# Implementación original de esterilizaya
# https://github.com/happypawspillaro/esterilizaya-pillaro/blob/main/app/esterilizaya/constantes.py

# Máxima longitud de caracteres para la BD
MAX_LONG_CANTONES = 5
MAX_LONG_BARRIOS = 75
MAX_LONG_PARROQUIAS = 5

# Cantones cercanos a las campañas de esterilización
CANTONES = [("PI", "Píllaro"), ("AM", "Ambato"), ("PE", "Pelileo"), ("PA", "Patate"), ("SA", "Salcedo")]

PARROQUIAS = [
    # Píllaro Rurales
    ("BM", "Baquerizo Moreno"),
    ("EMT", "Emilio Maria Terán"),
    ("ME", "Marcos Espinel"),
    ("PU", "Presidente Urbina"),
    ("SA", "San Andrés"),
    ("SJP", "San José de Poaló"),
    ("SM", "San Miguelito"),
    # Píllaro Urbanas
    ("LM", "La Matriz"),
    ("CN", "Ciudad Nueva"),
    # Ambato Rurales
    ("AMB", "Ambatillo"),
    ("AT", "Atahualpa"),
    ("ANM", "Augusto Nicolás Martínez"),
    ("CF", "Constantino Fernández"),
    ("CUN", "Cunchibamba"),
    ("HG", "Huachi Grande"),
    ("IZA", "Izamba"),
    ("JBV", "Juan Benigno Vela"),
    ("MON", "Montalvo"),
    ("PAS", "Pasa"),
    ("PIC", "Picaihua"),
    ("PIL", "Pilahuín"),
    ("QUI", "Quisapincha"),
    ("SBP", "San Bartolomé de Pinllo"),
    ("SF", "San Fernando"),
    ("SR", "Santa Rosa"),
    ("TOT", "Totoras"),
    ("UNA", "Unamuncho"),
    # Ambato Urbanas
    ("ATF", "Atocha - Ficoa"),
    ("CEL", "Celiano Monge"),
    ("HCH", "Huachi Chico"),
    ("HLO", "Huachi Loreto"),
    ("MER", "La Merced"),
    ("LPE", "La Península"),
    ("MAT", "La Matriz"),
    ("PIS", "Pishilata"),
    ("SFR", "San Francisco"),
    # Pelileo Rurales
    ("BEN", "Benítez"),
    ("BOL", "Bolívar"),
    ("COT", "Cotaló"),
    ("CHI", "Chiquicha"),
    ("ER", "El Rosario"),
    ("GM", "García Moreno"),
    ("HUA", "Huambaló"),
    ("SAL", "Salasaca"),
    # Pelileo Urbanas
    ("PEL", "Pelileo"),
    ("PGR", "Pelileo Grande"),
    # Patate Rurales
    ("ET", "El Triunfo"),
    ("LA", "Los Andes"),
    ("SUC", "Sucre"),
    # Patate Urbanas
    ("PAT", "Patate"),
    # Salcedo Rurales
    ("AJH", "Antonio José Holguín"),
    ("CUS", "Cusubamba"),
    ("MUO", "Mulalillo"),
    ("MUL", "Mulliquindil"),
    ("PAN", "Panzaleo"),
    # Salcedo Urbanas
    ("SMl", "San Miguel"),
]

PARROQUIAS_CANTON = {
    "PI": PARROQUIAS[0:9],
    "AM": PARROQUIAS[9:36],
    "PE": PARROQUIAS[36:46],
    "PA": PARROQUIAS[46:50],
    "SA": PARROQUIAS[50:56],
}
