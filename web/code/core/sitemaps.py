from animals.models import Animal, EstadoAnimal
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from medical_cases.models import MedicalCase
from reports.models import Report


class StaticViewSitemap(Sitemap):
    """Páginas públicas sin modelo detrás (listados y portada)."""

    changefreq = "daily"
    priority = 0.6

    def items(self):
        return [
            "core:home",
            "core:privacidad",
            # Sobre la Fundación
            "core:quienes_somos",
            "core:directiva",
            "core:reconocimientos",
            "core:impacto",
            # Proyectos e impacto TODO: Pensar en cambiarle el nombre de la categoría
            "core:fauna_urbana",
            "core:areas_trabajo",
            "core:software_libre",
            "core:media",
            # Transparencia y recursos TODO: Pensar en cambiarle el nombre de la categoría
            "core:fauna_urbana",
            "core:areas_trabajo",
            "core:software_libre",
            "core:media",
            # Contribuir
            "core:contribuir_home",
            "core:voluntariado",
            "animals:catalog",
            "medical_cases:list",
            "reports:list",
        ]

    def location(self, item):
        return reverse(item)


class AnimalSitemap(Sitemap):
    """Solo los animales en adopción: los adoptados no deben salir en Google."""

    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Animal.objects.filter(estado=EstadoAnimal.EN_ADOPCION)

    def lastmod(self, obj):
        return obj.actualizado


class MedicalCaseSitemap(Sitemap):
    """Todos los casos médicos son públicos (a diferencia de reportes y animales
    no hay un campo de aprobación/estado que los oculte)."""

    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return MedicalCase.objects.all()

    def lastmod(self, obj):
        return obj.creado


class ReportSitemap(Sitemap):
    """Solo los reportes aprobados por el staff son visibles al público."""

    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Report.objects.filter(aprobado=True)

    def lastmod(self, obj):
        return obj.creado
