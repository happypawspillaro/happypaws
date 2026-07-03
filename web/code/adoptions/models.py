from django.conf import settings
from django.db import models
from django.urls import reverse


class TipoVivienda(models.TextChoices):
    CASA = "casa", "Casa"
    DEPARTAMENTO = "departamento", "Departamento"
    OTRO = "otro", "Otro"


class EstadoSolicitud(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    EN_REVISION = "en_revision", "En revisión"
    APROBADA = "aprobada", "Aprobada"
    RECHAZADA = "rechazada", "Rechazada"


class PropositoTenencia(models.TextChoices):
    COMPANIA = "compania", "Compañía"
    REPRODUCCION = "reproduccion", "Reproducción"
    GUARDIAN = "guardian", "Guardián"
    SERVICIO = "servicio", "Servicio"
    OTRO = "otro", "Otro"


class AdoptionApplication(models.Model):
    animal = models.ForeignKey(
        "animals.Animal", on_delete=models.CASCADE, related_name="solicitudes"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitudes_adopcion",
    )
    nombre_solicitante = models.CharField("nombre completo", max_length=200)
    cedula = models.CharField("cédula", max_length=20)
    telefono = models.CharField("teléfono", max_length=20)
    email = models.EmailField("correo")
    direccion = models.CharField("dirección", max_length=255)
    tipo_vivienda = models.CharField(
        "tipo de vivienda", max_length=15, choices=TipoVivienda.choices
    )
    tiene_patio = models.BooleanField("¿tiene patio o espacio exterior?", default=False)
    experiencia = models.TextField("experiencia previa con mascotas", blank=True)
    proposito = models.CharField(
        "¿para qué quieres a la mascota?",
        max_length=15,
        choices=PropositoTenencia.choices,
        default=PropositoTenencia.COMPANIA,
    )
    motivo = models.TextField("¿por qué quieres adoptar a este animal?")
    estado = models.CharField(
        max_length=15, choices=EstadoSolicitud.choices, default=EstadoSolicitud.PENDIENTE
    )
    notas_internas = models.TextField("notas internas", blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "solicitud de adopción"
        verbose_name_plural = "solicitudes de adopción"

    def __str__(self):
        return f"{self.nombre_solicitante} → {self.animal.nombre}"

    def get_absolute_url(self):
        return reverse("adoptions:manage_detail", args=[self.pk])


class AdoptionFollowUp(models.Model):
    solicitud = models.ForeignKey(
        AdoptionApplication, on_delete=models.CASCADE, related_name="seguimientos"
    )
    fecha = models.DateField()
    notas = models.TextField()
    foto = models.ImageField(upload_to="adopciones/seguimiento/", blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "seguimiento post-adopción"
        verbose_name_plural = "seguimientos post-adopción"

    def __str__(self):
        return f"Seguimiento {self.fecha} · {self.solicitud}"
