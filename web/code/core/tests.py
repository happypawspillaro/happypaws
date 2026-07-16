from django.test import TestCase
from django.urls import reverse

from accounts.models import User


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
