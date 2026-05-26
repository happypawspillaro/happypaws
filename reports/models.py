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

    @property
    def permite_avistamientos(self):
        """Los avistamientos solo aplican a mascotas perdidas o encontradas."""
        return self.tipo in (TipoReporte.PERDIDO, TipoReporte.ENCONTRADO)


class ReportPhoto(models.Model):
    reporte = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name="fotos"
    )
    imagen = models.ImageField(upload_to="reportes/")

    def __str__(self):
        return f"Foto de {self.reporte}"


class ReportComment(models.Model):
    """Comentario o pista que cualquier persona puede dejar en un aviso."""

    reporte = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name="comentarios"
    )
    nombre = models.CharField("tu nombre", max_length=120)
    contacto = models.CharField(
        "contacto (opcional)", max_length=200, blank=True,
        help_text="Teléfono o correo, por si quieren responderte.",
    )
    mensaje = models.TextField("mensaje")
    oculto = models.BooleanField("oculto por moderación", default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["creado"]
        verbose_name = "comentario"
        verbose_name_plural = "comentarios"

    def __str__(self):
        return f"Comentario de {self.nombre} en {self.reporte}"


class ReportSighting(models.Model):
    """Avistamiento reportado por la comunidad sobre una mascota perdida/encontrada."""

    reporte = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name="avistamientos"
    )
    nombre = models.CharField("tu nombre", max_length=120)
    contacto = models.CharField(
        "contacto (opcional)", max_length=200, blank=True,
        help_text="Teléfono o correo, por si el dueño necesita más detalles.",
    )
    ubicacion = models.CharField("¿dónde lo viste?", max_length=255)
    fecha = models.DateField("¿cuándo lo viste?")
    descripcion = models.TextField("detalles", blank=True)
    foto = models.ImageField(
        "foto (opcional)", upload_to="reportes/avistamientos/", blank=True
    )
    confirmado = models.BooleanField("confirmado por la fundación", default=False)
    oculto = models.BooleanField("oculto por moderación", default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "avistamiento"
        verbose_name_plural = "avistamientos"

    def __str__(self):
        return f"Avistamiento en {self.ubicacion} ({self.fecha})"
