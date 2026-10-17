import json
import logging
import os
import tempfile
import time
from datetime import date
from pathlib import Path
from unittest.mock import patch

from accounts.models import User
from animals.models import Animal, Especie, EstadoAnimal, Sexo, Tamano
from core.cache import _cargar_locaciones_cached, obtener_locaciones
from core.management.commands.seed_demo import normalizar_contacto
from core.templatetags.whatsapp_filters import whatsapp_link
from core.views import listar_canton_parroquia, obtener_barrios
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from medical_cases.models import MedicalCase
from reports.models import Report, TipoReporte

logger = logging.getLogger(__name__)


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

    def test_incluye_favicon_y_logo(self):
        resp = self.client.get(reverse("core:home"))
        self.assertContains(resp, "images/happypaws.ico")
        self.assertContains(resp, "images/happypaws_icono_blanco.png")

    def test_footer_incluye_redes_sociales(self):
        resp = self.client.get(reverse("core:home"))
        self.assertContains(resp, "instagram.com/happypaws.pillaro")
        self.assertContains(resp, "tiktok.com/@happypaws.pillaro")
        self.assertContains(resp, "youtube.com/@HappyPawsP")
        self.assertContains(resp, "facebook.com/profile.php")
        self.assertContains(resp, "github.com/happypawspillaro")

    def test_footer_incluye_contacto_y_datos_legales(self):
        resp = self.client.get(reverse("core:home"))
        self.assertContains(resp, "mailto:happypaws.pillaro@gmail.com")
        self.assertContains(resp, "<i>Código SUIOS:</i> 0000142256")
        self.assertContains(resp, "<i>Acuerdo Ministerial Nro.</i> 00012-2024")


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

    def test_numero_como_entero(self):
        self.assertEqual(whatsapp_link(991234567), "https://wa.me/593991234567")


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
            barrio="Parque Infantil",
            parroquia="CN",
            canton="PI",
            fecha_avistamiento=date.today(),
            aprobado=False,
        )
        aprobado = Report.objects.create(
            tipo=TipoReporte.PERDIDO,
            titulo="Reporte aprobado",
            descripcion="...",
            barrio="El Belén",
            parroquia="LM",
            canton="PI",
            fecha_avistamiento=date.today(),
            aprobado=True,
        )
        resp = self.client.get("/sitemap.xml")
        self.assertContains(resp, aprobado.get_absolute_url())
        self.assertNotContains(resp, pendiente.get_absolute_url())


class VistasLocacionesTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # --- Pruebas lectura de datos con cache
        # Limpieza de cache
        _cargar_locaciones_cached.cache_clear()

        # Crear un directorio temporal donde guardar los datos
        self.directorio_temporal = tempfile.TemporaryDirectory()
        self.ruta_temporal = Path(self.directorio_temporal.name)

        # Utiliza la misma estructura de ruta temp_dir/data/locaciones.json
        self.data_folder = self.ruta_temporal / "data"
        self.data_folder.mkdir(parents=True, exist_ok=True)
        # Simulamos la constante de parroquias importada en la vista
        self.mock_parroquias = {"PI": ["Matriz", "Ciudad Nueva", "San Miguelito"]}

        # Simulamos los datos del JSON de locaciones para Píllaro
        self.mock_locaciones = {
            "PI": {
                "CN": {
                    "Ciudad Nueva": [-1.173622, -78.550283],
                    "La Florida": [-1.184806, -78.56032],
                    "Robalinopamba": [-1.169154, -78.554462],
                },
                "SM": {
                    "San Pedro de Cruzñan": [-1.197059, -78.529297],
                    "Santa Ana": [-1.205981, -78.526497],
                    "Yacupamba": [-1.209416, -78.531354],
                },
            }
        }

        self.ruta_locaciones = self.data_folder / "locaciones.json"
        # Escribir datos temporaneos
        self.ruta_locaciones.write_text(json.dumps(self.mock_locaciones), encoding="utf-8")

    def tearDown(self):
        # Limpia el cache y el directorio temporal al finalizar las pruebas
        _cargar_locaciones_cached.cache_clear()
        self.directorio_temporal.cleanup()

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

    def test_obtener_locaciones_via_staticfiles(self):
        """Prueba para carga de locaciones.json desde los finders de los staticfiles"""
        """Test loading when found via staticfiles finders (primary path)."""
        # Sobrescribe el DATA_DIR y lo incluye en el STATICFILES_DIRS con el fin de localizarle con el `finders`
        with override_settings(DATA_DIR=self.ruta_temporal, STATICFILES_DIRS=[self.ruta_temporal]):
            data = obtener_locaciones()
            self.assertEqual(data, self.mock_locaciones)

    def test_obtener_locaciones_via_respaldo(self):
        """Testea la ruta de respaldo cuando `finders.find()` no lo enncuentra."""
        # Para forzar que `finders.find()` no encuentre el archivo, lo vaciamos para usar `settings.DATA_DIR`
        with override_settings(DATA_DIR=self.ruta_temporal, STATICFILES_DIRS=[]):
            data = obtener_locaciones()
            self.assertEqual(data, self.mock_locaciones)

    def _verificar_carga(self, datos_esperados, misses_esperados, hits_esperados, mensaje=""):
        """Método auxiliar para reusar la lógica de llamada y aserciones del caché."""
        if mensaje:
            logger.info(mensaje)

        resultado = obtener_locaciones()
        self.assertEqual(resultado, datos_esperados)
        # Deshabilito aquí el linter porque pylint no reconoce que cache_info() es un método de la función decorada
        info = _cargar_locaciones_cached.cache_info() # pylint: disable=no-value-for-parameter
        self.assertEqual(info.misses, misses_esperados)
        self.assertEqual(info.hits, hits_esperados)

    def test_cache_carga_nuevos_retorna_memoria(self):
        """Prueba el ciclo completo del caché: carga inicial, hit, invalidación por timestamp y nuevo hit."""
        with override_settings(DATA_DIR=self.ruta_temporal, STATICFILES_DIRS=[self.ruta_temporal]):

            # 1. Carga inicial (Cache Miss)
            self._verificar_carga(
                datos_esperados=self.mock_locaciones,
                misses_esperados=1,
                hits_esperados=0,
                mensaje="Primera carga de datos al caché",
            )

            # 2. Segunda lectura (Cache Hit)
            self._verificar_carga(
                datos_esperados=self.mock_locaciones,
                misses_esperados=1,
                hits_esperados=1,
                mensaje="Segunda carga de datos al caché (debe retornar desde memoria)",
            )

            # 3. Actualizar contenido del JSON y forzar un timestamp más nuevo (para invalidar el caché)
            new_data = self.mock_locaciones.copy()
            new_data["PA"] = {"LA": {"Crucero": [-1.241795, -78.509720]}}
            self.ruta_locaciones.write_text(json.dumps(new_data), encoding="utf-8")

            future_timestamp = time.time() + 3600
            os.utime(self.ruta_locaciones, (future_timestamp, future_timestamp))

            # 4. Tercera carga con los datos nuevos (Cache Miss debido al cambio de mtime_ns)
            self._verificar_carga(
                datos_esperados=new_data,
                misses_esperados=2,
                hits_esperados=1,
                mensaje="Carga tras actualizar el archivo y su timestamp (Miss por invalidación)",
            )

            # 5. Cuarta carga con los nuevos datos (Cache Hit de la nueva versión)
            self._verificar_carga(
                datos_esperados=new_data,
                misses_esperados=2,
                hits_esperados=2,
                mensaje="Segunda carga con los nuevos datos (debe retornar desde memoria)",
            )

    def test_retorna_vacio_cuando_locaciones_json_no_existe(self):
        """Prueba que si no hay el archivo locaciones.json se retorne un diccionario vacío,
        en vez de FileNotFoundError."""
        logger.info("Iniciando prueba de carga sin archivo existente")
        # Eliminar el archivo inicial
        if self.ruta_locaciones.exists():
            self.ruta_locaciones.unlink()

        with override_settings(DATA_DIR=self.ruta_temporal, STATICFILES_DIRS=[self.ruta_temporal]):
            data = obtener_locaciones()
            # Verificar que capturó la excepción y retornó un diccionarrio vacío
            self.assertEqual(data, {})

    def test_returna_vacio_cuando_el_json_tiene_errores(self):
        """Prueba que una sintaxis JSON corrupta regresa un diccionario vacío en vez de devolver un JSONDecodeError"""
        logger.info("Iniciando prueba con JSON malformado")
        # Escribimos un texto JSON inválido
        self.ruta_locaciones.write_text("{ 'PI': [sintaxis rota }", encoding="utf-8")

        with override_settings(DATA_DIR=self.ruta_temporal, STATICFILES_DIRS=[self.ruta_temporal]):
            data = obtener_locaciones()
            # Verifica que hay un dato vacío y sin generar excepciones
            self.assertEqual(data, {})
