from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.urls import reverse


class EstadoCaso(models.TextChoices):
    ACTIVO = "activo", "Activo"
    CERRADO = "cerrado", "Cerrado"


class CategoriaEgreso(models.TextChoices):
    FACTURA = "factura", "Factura veterinaria"
    RAYOS_X = "rayos_x", "Rayos X"
    MEDICINA = "medicina", "Medicina"
    OTRO = "otro", "Otro"


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

    @property
    def total_egresos(self):
        total = self.egresos.aggregate(s=Sum("monto"))["s"]
        return total or Decimal("0")

    @property
    def egresos_por_categoria(self):
        """Agrupa los egresos por categoría para mostrarlos en el accordion.

        Devuelve una lista de dicts: etiqueta, total y los egresos de cada
        categoría que tenga al menos un registro, en el orden de CategoriaEgreso.
        """
        grupos = []
        for valor, etiqueta in CategoriaEgreso.choices:
            items = [e for e in self.egresos.all() if e.categoria == valor]
            if items:
                grupos.append(
                    {
                        "valor": valor,
                        "etiqueta": etiqueta,
                        "total": sum((e.monto for e in items), Decimal("0")),
                        "egresos": items,
                    }
                )
        return grupos

    @property
    def donantes_verificados(self):
        """Donaciones verificadas, para mostrar los agradecimientos públicos."""
        return self.donaciones.filter(verificado=True)


class Donation(models.Model):
    caso = models.ForeignKey(
        MedicalCase, on_delete=models.CASCADE, related_name="donaciones"
    )
    nombre_donante = models.CharField(
        "nombre del donante",
        max_length=200,
        blank=True,
        help_text="Déjalo en blanco para aparecer como donante anónimo.",
    )
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

    @property
    def nombre_publico(self):
        return self.nombre_donante.strip() or "Anónimo"

    def __str__(self):
        return f"{self.nombre_publico} · ${self.monto}"


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


class CasePhoto(models.Model):
    caso = models.ForeignKey(
        MedicalCase, on_delete=models.CASCADE, related_name="fotos"
    )
    imagen = models.ImageField(upload_to="casos/galeria/")
    descripcion = models.CharField("descripción", max_length=200, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["creado"]
        verbose_name = "foto del caso"
        verbose_name_plural = "fotos del caso"

    def __str__(self):
        return f"Foto · {self.caso.titulo}"


class Expense(models.Model):
    caso = models.ForeignKey(
        MedicalCase, on_delete=models.CASCADE, related_name="egresos"
    )
    categoria = models.CharField(
        max_length=20, choices=CategoriaEgreso.choices, default=CategoriaEgreso.OTRO
    )
    descripcion = models.CharField("descripción", max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    comprobante = models.ImageField(upload_to="casos/egresos/", blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-creado"]
        verbose_name = "egreso"
        verbose_name_plural = "egresos"

    def __str__(self):
        return f"{self.get_categoria_display()} · ${self.monto}"
