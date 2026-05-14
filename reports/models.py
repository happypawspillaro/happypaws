from django.db import models
from django.urls import reverse


class TipoReporte(models.TextChoices):
    PERDIDO = "perdido", "Mascota perdida"
    ENCONTRADO = "encontrado", "Mascota encontrada"
    MALTRATO = "maltrato", "Maltrato o abandono"


class EstadoReporte(models.TextChoices):
    ABIERTO = "abierto", "Abierto"
    RESUELTO = "resuelto", "Resuelto"


class Report(models.Model):
    tipo = models.CharField(max_length=12, choices=TipoReporte.choices)
    titulo = models.CharField("título", max_length=200)
    descripcion = models.TextField("descripción")
    ubicacion = models.CharField("ubicación / sector", max_length=255)
    fecha_avistamiento = models.DateField("fecha del avistamiento o hecho")
    nombre_reportante = models.CharField("tu nombre", max_length=200)
    contacto_reportante = models.CharField(
        "tu contacto (teléfono o correo)", max_length=200
    )
    estado = models.CharField(
        max_length=10, choices=EstadoReporte.choices, default=EstadoReporte.ABIERTO
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "reporte"
        verbose_name_plural = "reportes"

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.titulo}"

    def get_absolute_url(self):
        return reverse("reports:detail", args=[self.pk])


class ReportPhoto(models.Model):
    reporte = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name="fotos"
    )
    imagen = models.ImageField(upload_to="reportes/")

    def __str__(self):
        return f"Foto de {self.reporte}"
