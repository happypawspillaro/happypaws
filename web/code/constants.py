from django.db import models

# Un animal comunitario esterilizado dentro de esta ventana se destaca automáticamente.
MESES_FEATURED_COMUNITARIO = 6


class Especie(models.TextChoices):
    PERRO = "perro", "Perro"
    GATO = "gato", "Gato"
    OTRO = "otro", "Otro"


class Sexo(models.TextChoices):
    MACHO = "macho", "Macho"
    HEMBRA = "hembra", "Hembra"
    DESCONOCIDO = "desconocido", "Desconocido"
