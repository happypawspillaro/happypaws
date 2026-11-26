from datetime import date, time

from accounts.models import User
from animals.models import EstadoAnimal
from animals.tests import crear_animal
from core.publicacion import HASHTAGS_BASE, negrita, texto_animal, texto_reporte
from django.test import TestCase
from django.urls import reverse
from reports.models import TipoReporte
from reports.tests import crear_reporte

URL = "https://happypawspillaro.org/x/"


class NegritaTests(TestCase):
    def test_letras_y_numeros(self):
        self.assertEqual(negrita("Ab 9"), "𝗔𝗯 𝟵")

    def test_conserva_tildes_y_enie(self):
        # Se ve con tilde y, al quitar las marcas, queda la misma palabra.
        resultado = negrita("Señales: Ubicación")
        self.assertIn("̃", resultado)
        self.assertIn("́", resultado)
        self.assertNotIn("n", resultado)


class TextoReporteTests(TestCase):
    def test_perdido_lleva_encabezado_datos_y_hashtags(self):
        reporte = crear_reporte(
            fecha_avistamiento=date(2026, 10, 12),
            hora_aproximada=time(18, 30),
            especie="perro",
            sexo="macho",
            senales_distinguibles="Collar rojo",
        )
        texto = texto_reporte(reporte, URL)
        self.assertTrue(texto.startswith("🚨 " + negrita("MASCOTA PERDIDA")))
        self.assertIn("Se perdió Toby", texto)
        self.assertIn("12 de octubre de 2026, 18:30 aprox.", texto)
        self.assertIn("Perro · Macho", texto)
        self.assertIn("Collar rojo", texto)
        self.assertIn(URL, texto)
        self.assertIn("#MascotaPerdida", texto)
        for hashtag in HASHTAGS_BASE:
            self.assertIn(hashtag, texto)

    def test_no_incluye_datos_del_reportante(self):
        texto = texto_reporte(crear_reporte(), URL)
        self.assertNotIn("ana@example.com", texto)
        self.assertNotIn("Ana", texto)

    def test_omite_datos_vacios(self):
        texto = texto_reporte(crear_reporte(senales_distinguibles="", sexo="desconocido"), URL)
        self.assertNotIn(negrita("Señales:"), texto)
        self.assertNotIn("Desconocido", texto)
        self.assertNotIn("\n\n\n", texto)

    def test_cada_tipo_tiene_encabezado_propio(self):
        encabezados = {texto_reporte(crear_reporte(tipo=tipo), URL).split("\n")[0] for tipo in TipoReporte.values}
        self.assertEqual(len(encabezados), len(TipoReporte.values))


class TextoAnimalTests(TestCase):
    def test_en_adopcion(self):
        animal = crear_animal(nombre="Luna", esterilizado=True, edad_aprox="2 años")
        texto = texto_animal(animal, URL)
        self.assertIn(negrita("EN ADOPCIÓN"), texto)
        self.assertIn(negrita("Luna") + " busca un hogar", texto)
        self.assertIn("Perro · Macho · Mediano · 2 años", texto)
        self.assertIn("Sí ✅", texto)
        self.assertIn("#AdoptaNoCompres", texto)

    def test_concuerda_con_hembras(self):
        texto = texto_animal(crear_animal(nombre="Luna", sexo="hembra", esterilizado=True), URL)
        self.assertIn("que la quiera", texto)
        self.assertIn(negrita("Esterilizada:"), texto)

    def test_sin_esterilizar_no_muestra_la_linea(self):
        texto = texto_animal(crear_animal(esterilizado=False), URL)
        self.assertNotIn(negrita("Esterilizado:"), texto)

    def test_no_en_adopcion(self):
        texto = texto_animal(crear_animal(nombre="Bruce", estado=EstadoAnimal.EN_TRATAMIENTO), URL)
        self.assertIn(negrita("CONOCE A BRUCE"), texto)
        self.assertNotIn("#AdoptaNoCompres", texto)

    def test_no_incluye_datos_del_tutor(self):
        texto = texto_animal(crear_animal(tutor_nombre="Pedro", tutor_contacto="0991234567"), URL)
        self.assertNotIn("Pedro", texto)
        self.assertNotIn("0991234567", texto)


class PublicacionVistasTests(TestCase):
    def setUp(self):
        self.reporte = crear_reporte()
        self.animal = crear_animal()
        self.urls = [
            reverse("reports:publicacion", args=[self.reporte.pk]),
            reverse("animals:publicacion", args=[self.animal.pk]),
        ]

    def test_solo_staff(self):
        User.objects.create_user(username="user", password="x")
        self.client.login(username="user", password="x")
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 302)

    def test_staff_ve_el_texto(self):
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")
        resp = self.client.get(self.urls[0])
        self.assertContains(resp, "http://testserver" + self.reporte.get_absolute_url())
        self.assertContains(resp, 'name="robots" content="noindex')
        resp = self.client.get(self.urls[1])
        self.assertContains(resp, "http://testserver" + reverse("adoptions:apply", args=[self.animal.pk]))

    def test_boton_en_paginas_de_staff(self):
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")
        self.assertContains(self.client.get(self.reporte.get_absolute_url()), self.urls[0])
        self.assertContains(self.client.get(reverse("animals:manage_detail", args=[self.animal.pk])), self.urls[1])

    def test_boton_oculto_al_publico(self):
        self.assertNotContains(self.client.get(self.reporte.get_absolute_url()), self.urls[0])
