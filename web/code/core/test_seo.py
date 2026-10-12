import shutil
import tempfile
from datetime import date
from decimal import Decimal
from io import BytesIO

from animals.models import Animal, AnimalPhoto, EstadoAnimal
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
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
            ubicacion="Parque central",
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
