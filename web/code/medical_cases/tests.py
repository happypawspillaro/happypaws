from datetime import date
from decimal import Decimal

from django.test import TestCase

from .models import Donation, MedicalCase


class MedicalCaseTests(TestCase):
    def setUp(self):
        self.caso = MedicalCase.objects.create(
            titulo="Caso de prueba",
            descripcion="Descripción",
            meta_monto=Decimal("100.00"),
        )

    def test_monto_recaudado_solo_cuenta_verificadas(self):
        Donation.objects.create(
            caso=self.caso, nombre_donante="A", monto=Decimal("40"),
            fecha=date.today(), verificado=True,
        )
        Donation.objects.create(
            caso=self.caso, nombre_donante="B", monto=Decimal("30"),
            fecha=date.today(), verificado=False,
        )
        self.assertEqual(self.caso.monto_recaudado, Decimal("40"))

    def test_progreso_se_acota_a_100(self):
        Donation.objects.create(
            caso=self.caso, nombre_donante="C", monto=Decimal("250"),
            fecha=date.today(), verificado=True,
        )
        self.assertEqual(self.caso.progreso, 100)
        self.assertTrue(self.caso.meta_alcanzada)
