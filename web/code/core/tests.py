from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.management.commands.seed_demo import normalizar_contacto


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


class NormalizarContactoTests(TestCase):
    """Un teléfono llegado como int/float del JSON de origen no debe quedar
    con un ".0" colgando al guardarse (issue #22)."""

    def test_float_entero_pierde_el_punto_cero(self):
        dato = {"contacto": 991234567.0}
        normalizar_contacto(dato)
        self.assertEqual(dato["contacto"], "991234567")

    def test_int_se_convierte_a_texto(self):
        dato = {"contacto": 991234567}
        normalizar_contacto(dato)
        self.assertEqual(dato["contacto"], "991234567")

    def test_texto_no_se_toca(self):
        dato = {"contacto": "ana@example.com"}
        normalizar_contacto(dato)
        self.assertEqual(dato["contacto"], "ana@example.com")

    def test_clave_ausente_no_falla(self):
        dato = {"otra_clave": "x"}
        normalizar_contacto(dato)
        self.assertNotIn("contacto", dato)

    def test_clave_personalizada(self):
        dato = {"telefono": 991234567.0}
        normalizar_contacto(dato, "telefono")
        self.assertEqual(dato["telefono"], "991234567")
