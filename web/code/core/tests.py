from datetime import date

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from animals.models import Animal, Especie, EstadoAnimal, Sexo, Tamano
from medical_cases.models import MedicalCase
from reports.models import Report, TipoReporte


class HomeViewTests(TestCase):
    def test_home_responde_ok(self):
        resp = self.client.get(reverse("core:home"))
        self.assertEqual(resp.status_code, 200)


class ResponsiveBaseTests(TestCase):
    """Smoke test del diseño responsivo: viewport y páginas públicas clave."""

    def test_base_incluye_viewport_responsivo(self):
        resp = self.client.get(reverse("core:home"))
        self.assertContains(resp, 'name="viewport"')
        self.assertContains(resp, "width=device-width")

    def test_paginas_publicas_responden_ok(self):
        for nombre in [
            "core:home", "animals:catalog",
            "medical_cases:list", "reports:list",
        ]:
            with self.subTest(pagina=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)


class DashboardAccessTests(TestCase):
    def test_dashboard_redirige_a_anonimos(self):
        resp = self.client.get(reverse("core:dashboard"))
        self.assertEqual(resp.status_code, 302)

    def test_dashboard_visible_para_staff(self):
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")
        resp = self.client.get(reverse("core:dashboard"))
        self.assertEqual(resp.status_code, 200)

    def test_dashboard_bloquea_usuario_normal(self):
        User.objects.create_user(username="user", password="x")
        self.client.login(username="user", password="x")
        resp = self.client.get(reverse("core:dashboard"))
        self.assertEqual(resp.status_code, 302)


class SitemapTests(TestCase):
    """Issue #53: el sitemap debe listar solo contenido público."""

    def test_sitemap_responde_ok_y_es_xml(self):
        resp = self.client.get("/sitemap.xml")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/xml")

    def test_sitemap_incluye_animal_publicado(self):
        animal = Animal.objects.create(
            nombre="Firulais",
            especie=Especie.PERRO,
            sexo=Sexo.MACHO,
            tamano=Tamano.MEDIANO,
            descripcion="Perro de prueba",
            estado=EstadoAnimal.EN_ADOPCION,
            fecha_ingreso=date.today(),
        )
        resp = self.client.get("/sitemap.xml")
        self.assertContains(resp, animal.get_absolute_url())

    def test_sitemap_incluye_caso_medico(self):
        caso = MedicalCase.objects.create(titulo="Cirugía de Firulais", descripcion="...", meta_monto="100.00")
        resp = self.client.get("/sitemap.xml")
        self.assertContains(resp, caso.get_absolute_url())

    def test_sitemap_no_incluye_reporte_sin_aprobar(self):
        pendiente = Report.objects.create(
            tipo=TipoReporte.PERDIDO,
            titulo="Reporte sin aprobar",
            descripcion="...",
            ubicacion="Centro",
            fecha_avistamiento=date.today(),
            aprobado=False,
        )
        aprobado = Report.objects.create(
            tipo=TipoReporte.PERDIDO,
            titulo="Reporte aprobado",
            descripcion="...",
            ubicacion="Centro",
            fecha_avistamiento=date.today(),
            aprobado=True,
        )
        resp = self.client.get("/sitemap.xml")
        self.assertContains(resp, aprobado.get_absolute_url())
        self.assertNotContains(resp, pendiente.get_absolute_url())
