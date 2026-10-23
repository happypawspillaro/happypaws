from accounts.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

ID_PRUEBA = "G-PRUEBA123"


class GoogleAnalyticsTests(TestCase):
    """GA4 solo con GA_MEASUREMENT_ID y cargado por JS tras el consentimiento (#58)."""

    def test_sin_measurement_id_no_se_incluye(self):
        with override_settings(GA_MEASUREMENT_ID=""):
            resp = self.client.get(reverse("core:home"))
        self.assertNotContains(resp, "js/analiticas.js")
        self.assertNotContains(resp, "data-ga-id")

    @override_settings(GA_MEASUREMENT_ID=ID_PRUEBA)
    def test_con_measurement_id_incluye_el_script_despues_del_consentimiento(self):
        html = self.client.get(reverse("core:home")).content.decode()
        self.assertIn(f'data-ga-id="{ID_PRUEBA}"', html)
        self.assertLess(html.index("js/consentimiento.js"), html.index("js/analiticas.js"))

    @override_settings(GA_MEASUREMENT_ID=ID_PRUEBA)
    def test_gtag_no_se_carga_desde_el_html(self):
        # gtag.js lo agrega analiticas.js solo si la persona acepta las cookies.
        self.assertNotContains(self.client.get(reverse("core:home")), "googletagmanager.com")

    @override_settings(GA_MEASUREMENT_ID=ID_PRUEBA)
    def test_no_mide_al_equipo_de_la_fundacion(self):
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")
        self.assertNotContains(self.client.get(reverse("core:home")), "data-ga-id")
