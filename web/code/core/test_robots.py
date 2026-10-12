from django.test import TestCase
from django.urls import Resolver404, resolve


class RobotsTxtTests(TestCase):
    """El robots.txt se sirve en la raíz y bloquea las páginas del staff (#65)."""

    def setUp(self):
        self.resp = self.client.get("/robots.txt")
        self.lineas = self.resp.content.decode().splitlines()

    def test_se_sirve_como_texto_plano(self):
        self.assertEqual(self.resp.status_code, 200)
        self.assertEqual(self.resp["Content-Type"], "text/plain")

    def test_bloquea_las_paginas_de_gestion(self):
        for ruta in (
            "/admin/",
            "/panel/",
            "/adopciones/gestion/",
            "/animales/gestion/",
            "/casos/gestion/",
            "/reportes/gestion/",
        ):
            with self.subTest(ruta=ruta):
                self.assertIn(f"Disallow: {ruta}", self.lineas)

    def test_las_rutas_bloqueadas_existen(self):
        """Si alguien renombra una URL, el Disallow quedaría apuntando a nada."""
        for linea in self.lineas:
            if not linea.startswith("Disallow: "):
                continue
            prefijo = linea.removeprefix("Disallow: ")
            with self.subTest(prefijo=prefijo):
                try:
                    resolve(prefijo)
                except Resolver404:
                    # Prefijos como /reportes/comentario/ solo existen con un id detrás.
                    resolve(f"{prefijo}1/ocultar/")

    def test_apunta_al_sitemap_con_url_absoluta(self):
        self.assertIn("Sitemap: http://testserver/sitemap.xml", self.lineas)
