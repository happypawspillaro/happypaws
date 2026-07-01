from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.urls import reverse


class EstadoCaso(models.TextChoices):
    ACTIVO = "activo", "Activo"
    CERRADO = "cerrado", "Cerrado"


class MedicalCase(models.Model):
    animal = models.ForeignKey(
        "animals.Animal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="casos_medicos",
    )
    titulo = models.CharField("título", max_length=200)
    descripcion = models.TextField("descripción")
    meta_monto = models.DecimalField("meta de recaudación", max_digits=10, decimal_places=2)
    estado = models.CharField(
        max_length=10, choices=EstadoCaso.choices, default=EstadoCaso.ACTIVO
    )
    foto = models.ImageField(upload_to="casos/", blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "caso médico"
        verbose_name_plural = "casos médicos"

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse("medical_cases:detail", args=[self.pk])

    @property
    def monto_recaudado(self):
        total = self.donaciones.filter(verificado=True).aggregate(s=Sum("monto"))["s"]
        return total or Decimal("0")

    @property
    def progreso(self):
        """Porcentaje recaudado (0-100), acotado para la barra de progreso."""
        if not self.meta_monto:
            return 0
        pct = (self.monto_recaudado / self.meta_monto) * 100
        return min(round(pct), 100)

    @property
    def meta_alcanzada(self):
        return self.monto_recaudado >= self.meta_monto


class Donation(models.Model):
    caso = models.ForeignKey(
        MedicalCase, on_delete=models.CASCADE, related_name="donaciones"
    )
    nombre_donante = models.CharField("nombre del donante", max_length=200)
    email = models.EmailField("correo", blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    comprobante = models.ImageField(upload_to="casos/comprobantes/", blank=True)
    verificado = models.BooleanField(
        default=False,
        help_text="Marca la donación como verificada para sumarla al total recaudado.",
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-creado"]
        verbose_name = "donación"
        verbose_name_plural = "donaciones"

    def __str__(self):
        return f"{self.nombre_donante} · ${self.monto}"


class CaseUpdate(models.Model):
    caso = models.ForeignKey(
        MedicalCase, on_delete=models.CASCADE, related_name="avances"
    )
    fecha = models.DateField()
    texto = models.TextField()
    foto = models.ImageField(upload_to="casos/avances/", blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-creado"]
        verbose_name = "avance del caso"
        verbose_name_plural = "avances del caso"

    def __str__(self):
        return f"Avance {self.fecha} · {self.caso.titulo}"
