from unittest.mock import patch

from accounts.models import User
from core.management.commands.seed_demo import normalizar_contacto
from core.views import listar_canton_parroquia, obtener_barrios
from django.test import RequestFactory, TestCase
from django.urls import reverse


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
            "core:home",
            "animals:catalog",
            "medical_cases:list",
            "reports:list",
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


class VistasLocacionesTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Simulamos la constante de parroquias importada en la vista
        self.mock_parroquias = {"PI": ["Matriz", "Ciudad Nueva", "San Miguelito"]}

        # Simulamos los datos del JSON de locaciones para Píllaro
        self.mock_locaciones = {
            "PI": {
                "CN": {
                    "Ciudad Nueva": [-1.173622, -78.550283],
                    "La Florida": [-1.184806, -78.56032],
                    "Robalinopamba": [-1.169154, -78.554462],
                }
            }
        }

    # ==========================================
    # TESTS PARA: listar_canton_parroquia
    # ==========================================

    @patch("core.views.render")
    @patch("core.views.PARROQUIAS_CANTON")
    def test_listar_canton_parroquia_con_datos(self, mock_constante, mock_render):
        """Verifica que se recuperen las parroquias correctas según el cantón."""
        mock_constante.get.side_effect = self.mock_parroquias.get

        request = self.factory.get("/", {"canton": "PI", "parroquia": "Ciudad Nueva"})
        listar_canton_parroquia(request)

        # Extraemos el contexto pasado a render()
        # render es llamado como: render(request, "template.html", contexto)
        contexto = mock_render.call_args[0][2]

        self.assertEqual(contexto["parroquias"], ["Matriz", "Ciudad Nueva", "San Miguelito"])
        self.assertEqual(contexto["selected_parroquia"], "Ciudad Nueva")

    @patch("core.views.render")
    def test_listar_canton_parroquia_parametros_vacios(self, mock_render):
        """Verifica el comportamiento cuando no se envía cantón ni parroquia."""
        request = self.factory.get("/")
        listar_canton_parroquia(request)

        contexto = mock_render.call_args[0][2]

        # Al no haber cantón, get("canton") devuelve None o "", por lo que parroquias debe ser []
        self.assertEqual(contexto["parroquias"], [])
        self.assertEqual(contexto["selected_parroquia"], "")

    # ==========================================
    # TESTS PARA: obtener_barrios
    # ==========================================

    @patch("core.views.obtener_locaciones")
    @patch("core.views.render")
    def test_obtener_barrios_filtrado_exitoso(self, mock_render, mock_obtener_locaciones):
        """Prueba que la vista filtra los barrios correctamente e ignora mayúsculas/minúsculas."""
        mock_obtener_locaciones.return_value = self.mock_locaciones

        # Enviamos "flor" para asegurar que coincida con "La Florida"
        request = self.factory.get("/", {"canton": "PI", "parroquia": "CN", "barrio": "flor"})
        obtener_barrios(request)

        contexto = mock_render.call_args[0][2]
        barrios = contexto["barrios"]

        self.assertEqual(len(barrios), 1)
        self.assertEqual(barrios[0], "La Florida")

    @patch("core.views.obtener_locaciones")
    @patch("core.views.render")
    def test_obtener_barrios_sin_coincidencias(self, mock_render, mock_obtener_locaciones):
        """Prueba el comportamiento cuando la búsqueda no coincide con ningún barrio."""
        mock_obtener_locaciones.return_value = self.mock_locaciones

        request = self.factory.get("/", {"canton": "PI", "parroquia": "CN", "barrio": "inexistente"})
        obtener_barrios(request)

        contexto = mock_render.call_args[0][2]

        self.assertEqual(contexto["barrios"], [])

    @patch("core.views.obtener_locaciones")
    @patch("core.views.render")
    def test_obtener_barrios_parametros_vacios(self, mock_render, mock_obtener_locaciones):
        """Prueba que al enviar la query vacía retorna todos los barrios ordenados alfabéticamente."""
        mock_obtener_locaciones.return_value = self.mock_locaciones

        request = self.factory.get("/", {"canton": "PI", "parroquia": "CN", "barrio": ""})
        obtener_barrios(request)

        contexto = mock_render.call_args[0][2]

        barrios_esperados = ["Ciudad Nueva", "La Florida", "Robalinopamba"]
        self.assertEqual(contexto["barrios"], barrios_esperados)
        self.assertEqual(mock_render.call_args[0][1], "core/partials/sugerencia_barrios.html")
