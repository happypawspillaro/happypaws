from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Usuario del sistema. El staff de la fundación tiene is_staff=True y accede
    al panel administrativo; el público registrado solo tiene una cuenta básica."""

    telefono = models.CharField("teléfono", max_length=20, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username
