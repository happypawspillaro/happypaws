import shutil
import tempfile
from datetime import date
from decimal import Decimal
from io import BytesIO

from accounts.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import CasePhoto, CategoriaEgreso, Donation, Expense, MedicalCase


class MedicalCaseTests(TestCase):
    def setUp(self):
        self.caso = MedicalCase.objects.create(
            titulo="Caso de prueba",
            descripcion="Descripción",
            meta_monto=Decimal("100.00"),
        )

    def test_monto_recaudado_solo_cuenta_verificadas(self):
        Donation.objects.create(
            caso=self.caso,
            nombre_donante="A",
            monto=Decimal("40"),
            fecha=date.today(),
            verificado=True,
        )
        Donation.objects.create(
            caso=self.caso,
            nombre_donante="B",
            monto=Decimal("30"),
            fecha=date.today(),
            verificado=False,
        )
        self.assertEqual(self.caso.monto_recaudado, Decimal("40"))

    def test_progreso_se_acota_a_100(self):
        Donation.objects.create(
            caso=self.caso,
            nombre_donante="C",
            monto=Decimal("250"),
            fecha=date.today(),
            verificado=True,
        )
        self.assertEqual(self.caso.progreso, 100)
        self.assertTrue(self.caso.meta_alcanzada)

    def test_donacion_sin_nombre_es_anonima(self):
        d = Donation.objects.create(
            caso=self.caso,
            nombre_donante="",
            monto=Decimal("10"),
            fecha=date.today(),
            verificado=True,
        )
        self.assertEqual(d.nombre_publico, "Anónimo")

    def test_donantes_verificados_excluye_pendientes(self):
        Donation.objects.create(
            caso=self.caso,
            nombre_donante="Visible",
            monto=Decimal("10"),
            fecha=date.today(),
            verificado=True,
        )
        Donation.objects.create(
            caso=self.caso,
            nombre_donante="Oculta",
            monto=Decimal("10"),
            fecha=date.today(),
            verificado=False,
        )
        nombres = [d.nombre_donante for d in self.caso.donantes_verificados]
        self.assertEqual(nombres, ["Visible"])


class MiniaturaListaTests(TestCase):
    """La lista de casos usa la miniatura cuadrada, no la foto original (#71)."""

    def setUp(self):
        self.miniatura_px = 320
        self.media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=self.media)
        override.enable()
        self.addCleanup(override.disable)

        buffer = BytesIO()
        Image.new("RGB", (900, 1200), "orange").save(buffer, format="JPEG")
        self.caso = MedicalCase.objects.create(
            titulo="Caso con foto",
            descripcion="Descripción",
            meta_monto=Decimal("100.00"),
        )
        self.foto = CasePhoto.objects.create(
            caso=self.caso,
            imagen=SimpleUploadedFile("vertical.jpg", buffer.getvalue(), content_type="image/jpeg"),
        )

    def test_lista_usa_miniatura_cuadrada(self):
        resp = self.client.get(reverse("medical_cases:list"))
        self.assertContains(resp, f"{self.miniatura_px}x{self.miniatura_px}")
        self.assertNotContains(resp, f'src="{self.foto.imagen.url}"')


class ExpenseTests(TestCase):
    def setUp(self):
        self.caso = MedicalCase.objects.create(
            titulo="Caso con egresos",
            descripcion="x",
            meta_monto=Decimal("100"),
        )

    def test_total_egresos_suma_todo(self):
        Expense.objects.create(
            caso=self.caso,
            categoria=CategoriaEgreso.MEDICINA,
            descripcion="Antibiótico",
            monto=Decimal("12"),
            fecha=date.today(),
        )
        Expense.objects.create(
            caso=self.caso,
            categoria=CategoriaEgreso.RAYOS_X,
            descripcion="Placa",
            monto=Decimal("30"),
            fecha=date.today(),
        )
        self.assertEqual(self.caso.total_egresos, Decimal("42"))

    def test_egresos_agrupados_por_categoria(self):
        Expense.objects.create(
            caso=self.caso,
            categoria=CategoriaEgreso.MEDICINA,
            descripcion="A",
            monto=Decimal("5"),
            fecha=date.today(),
        )
        Expense.objects.create(
            caso=self.caso,
            categoria=CategoriaEgreso.MEDICINA,
            descripcion="B",
            monto=Decimal("7"),
            fecha=date.today(),
        )
        grupos = self.caso.egresos_por_categoria
        self.assertEqual(len(grupos), 1)
        self.assertEqual(grupos[0]["valor"], CategoriaEgreso.MEDICINA)
        self.assertEqual(grupos[0]["total"], Decimal("12"))
        self.assertEqual(len(grupos[0]["egresos"]), 2)


class StaffManagementTests(TestCase):
    def setUp(self):
        self.caso = MedicalCase.objects.create(
            titulo="Caso staff",
            descripcion="x",
            meta_monto=Decimal("100"),
        )
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")

    def test_staff_registra_egreso(self):
        self.client.post(
            reverse("medical_cases:add_expense", args=[self.caso.pk]),
            {
                "categoria": CategoriaEgreso.MEDICINA,
                "descripcion": "Vacuna",
                "monto": "15",
                "fecha": date.today().isoformat(),
            },
        )
        self.assertEqual(self.caso.egresos.count(), 1)

    def test_egreso_requiere_staff(self):
        self.client.logout()
        resp = self.client.post(
            reverse("medical_cases:add_expense", args=[self.caso.pk]),
            {
                "categoria": CategoriaEgreso.MEDICINA,
                "descripcion": "Vacuna",
                "monto": "15",
                "fecha": date.today().isoformat(),
            },
        )
        self.assertEqual(resp.status_code, 302)  # redirige al login
        self.assertEqual(self.caso.egresos.count(), 0)
