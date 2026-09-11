import calendar
from datetime import date

from constants import MESES_FEATURED_COMUNITARIO, Especie, Sexo
from django.db import models
from django.urls import reverse
from django.utils import timezone


def restar_meses(fecha, meses):
    """Devuelve la fecha resultante de restar ``meses`` meses, ajustando el día."""
    # Trabajamos con un índice de mes absoluto (base 0) para restar sin bucles.
    indice = (fecha.year * 12 + fecha.month - 1) - meses
    anio, mes = divmod(indice, 12)
    mes += 1
    dia = min(fecha.day, calendar.monthrange(anio, mes)[1])
    return date(anio, mes, dia)


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


class Origen(models.TextChoices):
    DOMESTICO = "domestico", "Doméstico (nació en una casa)"
    RESCATADO = "rescatado", "Rescatado (nació en la calle)"
    COMUNITARIO = "comunitario", "Comunitario (vive en la calle)"


class Animal(models.Model):
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=10, choices=Especie.choices)
    sexo = models.CharField(max_length=11, choices=Sexo.choices)
    tamano = models.CharField("tamaño", max_length=10, choices=Tamano.choices)
    edad_aprox = models.CharField("edad aproximada", max_length=50, blank=True)
    descripcion = models.TextField("descripción")
    estado = models.CharField(max_length=20, choices=EstadoAnimal.choices, default=EstadoAnimal.RESCATADO)
    origen = models.CharField(
        "origen del animal",
        max_length=15,
        choices=Origen.choices,
        default=Origen.RESCATADO,
    )
    # Ubicación del animal. La parroquia es texto libre por ahora; cuando llegue
    # el locaciones.json de la fundación se podrá convertir en lista desplegable.
    barrio = models.CharField("barrio / sector", max_length=120, blank=True, help_text="Ej. 24 de Mayo")
    parroquia = models.CharField("parroquia", max_length=120, blank=True)
    # Datos del tutor / responsable (para animales domésticos o con cuidador).
    tutor_nombre = models.CharField("nombre del tutor / responsable", max_length=200, blank=True)
    tutor_contacto = models.CharField(
        "contacto del tutor (teléfono o correo)",
        max_length=200,
        blank=True,
        help_text="Opcional. Teléfono o correo del tutor o cuidador.",
    )
    esterilizado = models.BooleanField(default=False)
    fecha_esterilizacion = models.DateField("fecha de esterilización", null=True, blank=True)
    destacado = models.BooleanField(
        "destacar como vulnerable",
        default=False,
        help_text="Muéstralo al inicio del catálogo (perro en situación vulnerable).",
    )
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

    @property
    def tiene_tutor(self):
        return bool(self.tutor_nombre.strip())

    @property
    def ubicacion_completa(self):
        """Barrio y parroquia combinados, omitiendo lo que esté vacío."""
        partes = [p.strip() for p in (self.barrio, self.parroquia) if p.strip()]
        return ", ".join(partes)

    @property
    def es_comunitario_reciente(self):
        """Comunitario esterilizado hace menos de 6 meses."""
        if self.origen != Origen.COMUNITARIO or not self.esterilizado or not self.fecha_esterilizacion:
            return False
        limite = restar_meses(timezone.now().date(), MESES_FEATURED_COMUNITARIO)
        return self.fecha_esterilizacion >= limite

    @property
    def es_destacado(self):
        """Se muestra como destacado: marcado por el staff o comunitario reciente."""
        return self.destacado or self.es_comunitario_reciente


class AnimalPhoto(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="fotos")
    imagen = models.ImageField(upload_to="animales/galeria/")
    descripcion = models.CharField("descripción", max_length=200, blank=True)

    def __str__(self):
        return f"Foto de {self.animal.nombre}"


class MedicalRecord(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="historial_medico")
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
