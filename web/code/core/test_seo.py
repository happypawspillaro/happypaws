import re
import shutil
import tempfile
from datetime import date
from decimal import Decimal
from io import BytesIO

from animals.models import Animal, AnimalPhoto, EstadoAnimal
from core.seo import ubicacion_seo
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from medical_cases.models import CasePhoto, CaseUpdate, MedicalCase
from PIL import Image
from reports.models import Report, ReportPhoto, TipoReporte


def foto_de_celular(nombre="foto.jpg", tamano=(2400, 3200)):
    """Foto vertical grande, como las que sube la fundación desde el celular."""
    buffer = BytesIO()
    Image.new("RGB", tamano, "orange").save(buffer, format="JPEG")
    return SimpleUploadedFile(nombre, buffer.getvalue(), content_type="image/jpeg")


class DatosSEO(TestCase):
    """Un animal, un caso médico y un reporte con fotos, en un MEDIA_ROOT temporal."""

    def setUp(self):
        self.media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=self.media)
        override.enable()
        self.addCleanup(override.disable)

        self.animal = Animal.objects.create(
            nombre="Luna",
            especie="perro",
            sexo="hembra",
            tamano="mediano",
            descripcion="Luna es juguetona y se lleva bien con otros perros.",
            estado=EstadoAnimal.EN_ADOPCION,
            parroquia="La Matriz",
            fecha_ingreso=date(2026, 1, 10),
            foto_principal=foto_de_celular("luna.jpg"),
        )
        self.foto_galeria = AnimalPhoto.objects.create(animal=self.animal, imagen=foto_de_celular("luna-2.jpg"))

        self.caso = MedicalCase.objects.create(
            animal=self.animal,
            titulo="Cirugía de cadera",
            descripcion="Luna necesita una cirugía de cadera.",
            meta_monto=Decimal("300.00"),
        )
        self.foto_caso = CasePhoto.objects.create(caso=self.caso, imagen=foto_de_celular("caso.jpg"))
        self.avance = CaseUpdate.objects.create(
            caso=self.caso,
            fecha=date(2026, 2, 1),
            texto="Ya salió de la operación.",
            foto=foto_de_celular("avance.jpg"),
        )

        self.reporte = Report.objects.create(
            tipo=TipoReporte.PERDIDO,
            titulo="Perrito café cerca del parque",
            descripcion="Se perdió el domingo en la tarde.",
            canton="PI",
            parroquia="LM",
            barrio="Parque central",
            fecha_avistamiento=date(2026, 3, 1),
            aprobado=True,
        )
        self.foto_reporte = ReportPhoto.objects.create(reporte=self.reporte, imagen=foto_de_celular("reporte.jpg"))


class ImagenesDetalleTests(DatosSEO):
    """Las vistas de detalle usan derivados livianos, no la foto original (#72)."""

    def test_detalle_de_animal(self):
        resp = self.client.get(self.animal.get_absolute_url())
        self.assertNotContains(resp, f'src="{self.animal.foto_principal.url}"')
        self.assertNotContains(resp, f'src="{self.foto_galeria.imagen.url}"')
        # 2400x3200 achicada para entrar en 1200x1200, sin recortar.
        self.assertContains(resp, 'width="900"')
        self.assertContains(resp, 'height="1200"')

    def test_detalle_de_caso_medico(self):
        resp = self.client.get(self.caso.get_absolute_url())
        self.assertNotContains(resp, f'src="{self.foto_caso.imagen.url}"')
        self.assertNotContains(resp, f'src="{self.avance.foto.url}"')
        self.assertContains(resp, 'width="900"')

    def test_detalle_de_reporte(self):
        resp = self.client.get(self.reporte.get_absolute_url())
        self.assertNotContains(resp, f'src="{self.foto_reporte.imagen.url}"')
        self.assertContains(resp, 'width="900"')

    def test_png_con_transparencia_se_sirve_como_jpg(self):
        buffer = BytesIO()
        Image.new("RGBA", (960, 1280), (255, 165, 0, 255)).save(buffer, format="PNG")
        self.animal.foto_principal = SimpleUploadedFile("bruce.jpg", buffer.getvalue(), content_type="image/png")
        self.animal.save()
        resp = self.client.get(self.animal.get_absolute_url())
        self.assertRegex(resp.content.decode(), r'src="[^"]*bruce\.jpg\.1200x1200_q80[^"]*\.jpg"')

    def test_no_agranda_fotos_pequenas(self):
        self.animal.foto_principal = foto_de_celular("chiquita.jpg", (600, 400))
        self.animal.save()
        resp = self.client.get(self.animal.get_absolute_url())
        self.assertContains(resp, 'width="600"')
        self.assertContains(resp, 'height="400"')


class UbicacionSEOTests(SimpleTestCase):
    def test_parroquia_y_canton(self):
        self.assertEqual(ubicacion_seo("La Matriz"), "La Matriz/Píllaro")

    def test_sin_parroquia_queda_solo_el_canton(self):
        self.assertEqual(ubicacion_seo("  "), "Píllaro")


class TituloSEOTests(DatosSEO):
    """Formato de texto para <title>, <h1> y alt (#66)."""

    def test_animal_en_adopcion(self):
        self.assertEqual(self.animal.titulo_seo, "Adopta a Luna de La Matriz/Píllaro")

    def test_animal_que_no_esta_en_adopcion(self):
        self.animal.estado = EstadoAnimal.RESCATADO
        self.assertEqual(self.animal.titulo_seo, "Conoce a Luna de La Matriz/Píllaro")

    def test_caso_medico_con_animal(self):
        self.assertEqual(self.caso.titulo_seo, "Ayuda a Luna de La Matriz/Píllaro: Cirugía de cadera")

    def test_caso_medico_sin_animal(self):
        self.caso.animal = None
        self.assertEqual(self.caso.titulo_seo, "Ayuda en Píllaro: Cirugía de cadera")

    def test_reporte(self):
        self.assertEqual(self.reporte.titulo_seo, "Mascota perdida en La Matriz/Píllaro: Perrito café cerca del parque")


class EncabezadosYAltTests(DatosSEO):
    """Un solo <h1> descriptivo por página y alt con la marca (#66, #73)."""

    def h1s(self, resp):
        return re.findall(r"<h1[^>]*>(.*?)</h1>", resp.content.decode(), re.S)

    def test_detalles_tienen_un_solo_h1_descriptivo(self):
        for obj in (self.animal, self.caso, self.reporte):
            with self.subTest(obj=obj):
                resp = self.client.get(obj.get_absolute_url())
                self.assertEqual([h.strip() for h in self.h1s(resp)], [obj.titulo_seo])
                self.assertContains(resp, f"<title>{obj.titulo_seo} | Happy Paws Píllaro</title>", html=False)

    def test_portada_tiene_un_solo_h1(self):
        resp = self.client.get(reverse("core:home"))
        self.assertEqual(len(self.h1s(resp)), 1)

    def test_las_fotos_llevan_la_marca_en_el_alt(self):
        for obj in (self.animal, self.caso, self.reporte):
            with self.subTest(obj=obj):
                resp = self.client.get(obj.get_absolute_url())
                alts = re.findall(r'<img[^>]*alt="([^"]*)"', resp.content.decode())
                fotos = [a for a in alts if "Icono" not in a]  # el logo del navbar
                self.assertTrue(fotos)
                for alt in fotos:
                    self.assertTrue(alt.endswith(" | Happy Paws Píllaro"), alt)

    def test_listados_usan_el_mismo_alt(self):
        for url, obj in (
            (reverse("animals:catalog"), self.animal),
            (reverse("medical_cases:list"), self.caso),
            (reverse("reports:list"), self.reporte),
        ):
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), f'alt="{obj.titulo_seo} | Happy Paws Píllaro"')


class MetadatosTests(DatosSEO):
    """description, keywords, author y OpenGraph en cada página (#67, #68)."""

    def meta(self, resp, atributo, nombre):
        encontrado = re.search(rf'<meta {atributo}="{re.escape(nombre)}"\s+content="([^"]*)"', resp.content.decode())
        self.assertIsNotNone(encontrado, f"falta <meta {atributo}={nombre}>")
        return encontrado.group(1)

    def test_detalles_tienen_titulo_descripcion_y_foto_absoluta(self):
        for obj in (self.animal, self.caso, self.reporte):
            with self.subTest(obj=obj):
                resp = self.client.get(obj.get_absolute_url())
                self.assertEqual(self.meta(resp, "property", "og:title"), f"{obj.titulo_seo} | Happy Paws Píllaro")
                self.assertEqual(self.meta(resp, "property", "og:url"), f"http://testserver{obj.get_absolute_url()}")
                self.assertEqual(self.meta(resp, "name", "description"), obj.descripcion)
                imagen = self.meta(resp, "property", "og:image")
                self.assertTrue(imagen.startswith("http://testserver/media/"), imagen)
                self.assertIn("1200x1200", imagen)  # el derivado liviano, no el original

    def test_caso_sin_fotos_comparte_la_foto_del_animal(self):
        self.caso.fotos.all().delete()
        resp = self.client.get(self.caso.get_absolute_url())
        self.assertIn("/media/animales/luna.jpg.1200x1200", self.meta(resp, "property", "og:image"))

    def test_caso_sin_animal_ni_fotos_comparte_el_logo(self):
        self.caso.fotos.all().delete()
        self.caso.animal = None
        self.caso.save()
        resp = self.client.get(self.caso.get_absolute_url())
        self.assertEqual(resp.status_code, 200)
        self.assertIn("happypaws_cuadrado.png", self.meta(resp, "property", "og:image"))

    def test_sin_foto_se_comparte_el_logo(self):
        self.reporte.fotos.all().delete()
        resp = self.client.get(self.reporte.get_absolute_url())
        self.assertEqual(
            self.meta(resp, "property", "og:image"), "http://testserver/static/images/happypaws_cuadrado.png"
        )

    def test_descripcion_larga_se_recorta(self):
        self.animal.descripcion = "<p>Muy juguetona.</p> " * 30
        self.animal.save()
        descripcion = self.meta(self.client.get(self.animal.get_absolute_url()), "name", "description")
        self.assertLessEqual(len(descripcion), 160)
        self.assertNotIn("<p>", descripcion)

    def test_todas_las_paginas_publicas_tienen_metadatos(self):
        for url in (
            reverse("core:home"),
            reverse("animals:catalog"),
            reverse("medical_cases:list"),
            reverse("reports:list"),
            reverse("reports:create"),
        ):
            with self.subTest(url=url):
                resp = self.client.get(url)
                for atributo, nombre in (
                    ("name", "description"),
                    ("name", "keywords"),
                    ("name", "author"),
                    ("property", "og:title"),
                    ("property", "og:description"),
                    ("property", "og:image"),
                ):
                    self.assertTrue(self.meta(resp, atributo, nombre))
                self.assertEqual(self.meta(resp, "property", "og:url"), f"http://testserver{url}")


class IndexacionAnimalesTests(DatosSEO):
    """Los animales que ya no están en adopción no deben salir en Google."""

    def test_animal_en_adopcion_se_indexa(self):
        self.assertNotContains(self.client.get(self.animal.get_absolute_url()), 'name="robots"')

    def test_animal_que_no_esta_en_adopcion_no_se_indexa(self):
        for estado in EstadoAnimal.values:
            if estado == EstadoAnimal.EN_ADOPCION:
                continue
            with self.subTest(estado=estado):
                self.animal.estado = estado
                self.animal.save()
                resp = self.client.get(self.animal.get_absolute_url())
                self.assertEqual(resp.status_code, 200)
                self.assertContains(resp, '<meta name="robots" content="noindex, follow">')
