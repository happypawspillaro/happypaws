from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from animals.models import Animal
from medical_cases.models import MedicalCase
from reports.models import Report


class StaticViewSitemap(Sitemap):
    """Páginas públicas sin modelo detrás (listados y portada)."""

    changefreq = "daily"
    priority = 0.6

    def items(self):
        return ["core:home", "animals:catalog", "medical_cases:list", "reports:list"]

    def location(self, item):
        return reverse(item)


class AnimalSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Animal.objects.all()

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
