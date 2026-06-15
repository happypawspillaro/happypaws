from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class StaffRequiredTests(TestCase):
    """El panel administrativo solo es accesible para el staff."""

    panel_url_name = "reports:manage_list"

    def test_anonimo_es_redirigido_al_login(self):
        resp = self.client.get(reverse(self.panel_url_name))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp["Location"].startswith(reverse("accounts:login")))

    def test_usuario_normal_no_accede(self):
        User.objects.create_user(username="normal", password="x", is_staff=False)
        self.client.login(username="normal", password="x")
        resp = self.client.get(reverse(self.panel_url_name))
        self.assertEqual(resp.status_code, 302)  # rebota al login

    def test_staff_accede(self):
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")
        resp = self.client.get(reverse(self.panel_url_name))
        self.assertEqual(resp.status_code, 200)
