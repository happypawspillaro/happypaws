from django.db import models
from django.urls import reverse


class Especie(models.TextChoices):
    PERRO = "perro", "Perro"
    GATO = "gato", "Gato"


class Sexo(models.TextChoices):
    MACHO = "macho", "Macho"
    HEMBRA = "hembra", "Hembra"


class Tamano(models.TextChoices):
    PEQUENO = "pequeno", "Pequeño"
    MEDIANO = "mediano", "Mediano"
    GRANDE = "grande", "Grande"


class EstadoAnimal(models.TextChoices):
    RESCATADO = "rescatado", "Rescatado"
    EN_TRATAMIENTO = "en_tratamiento", "En tratamiento"
    EN_ADOPCION = "en_adopcion", "En adopción"
    HOGAR_TEMPORAL = "hogar_temporal", "En hogar temporal"
    ADOPTADO = "adoptado", "Adoptado"


class Animal(models.Model):
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=10, choices=Especie.choices)
    sexo = models.CharField(max_length=10, choices=Sexo.choices)
    tamano = models.CharField("tamaño", max_length=10, choices=Tamano.choices)
    edad_aprox = models.CharField("edad aproximada", max_length=50, blank=True)
    descripcion = models.TextField("descripción")
    estado = models.CharField(
        max_length=20, choices=EstadoAnimal.choices, default=EstadoAnimal.RESCATADO
    )
    esterilizado = models.BooleanField(default=False)
    fecha_ingreso = models.DateField()
    foto_principal = models.ImageField(upload_to="animales/", blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_ingreso", "nombre"]
        verbose_name = "animal"
        verbose_name_plural = "animales"

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse("animals:detail", args=[self.pk])

    @property
    def en_adopcion(self):
        return self.estado == EstadoAnimal.EN_ADOPCION


class AnimalPhoto(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="fotos")
    imagen = models.ImageField(upload_to="animales/galeria/")
    descripcion = models.CharField("descripción", max_length=200, blank=True)

    def __str__(self):
        return f"Foto de {self.animal.nombre}"


class MedicalRecord(models.Model):
    animal = models.ForeignKey(
        Animal, on_delete=models.CASCADE, related_name="historial_medico"
    )
    fecha = models.DateField()
    descripcion = models.TextField("descripción")
    veterinario = models.CharField(max_length=150, blank=True)
    costo = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "registro médico"
        verbose_name_plural = "historial médico"

    def __str__(self):
        return f"{self.animal.nombre} · {self.fecha}"
