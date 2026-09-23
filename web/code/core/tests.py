from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from core.templatetags.whatsapp_filters import whatsapp_link


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


class WhatsappLinkFilterTests(TestCase):
    """El filtro solo debe reconocer celulares ecuatorianos (issue #46)."""

    def test_numero_de_9_digitos(self):
        self.assertEqual(whatsapp_link("991234567"), "https://wa.me/593991234567")

    def test_numero_con_cero_inicial(self):
        self.assertEqual(whatsapp_link("0991234567"), "https://wa.me/593991234567")

    def test_numero_con_codigo_de_pais(self):
        self.assertEqual(whatsapp_link("593991234567"), "https://wa.me/593991234567")

    def test_numero_con_formato_y_signo_mas(self):
        self.assertEqual(whatsapp_link("+593 99-123-4567"), "https://wa.me/593991234567")

    def test_correo_no_genera_enlace(self):
        self.assertIsNone(whatsapp_link("ana@example.com"))

    def test_numero_fijo_no_genera_enlace(self):
        self.assertIsNone(whatsapp_link("032345678"))

    def test_valor_vacio_no_genera_enlace(self):
        self.assertIsNone(whatsapp_link(""))
        self.assertIsNone(whatsapp_link(None))
