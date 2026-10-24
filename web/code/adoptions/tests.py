from datetime import date

from accounts.models import User
from animals.models import Animal, Especie, EstadoAnimal, Sexo, Tamano
from animals.tests import crear_animal
from core.tests_common.mixins import UbicacionCompletaTestMixin
from django.test import TestCase
from django.urls import reverse

from .models import (
    AdoptionApplication,
    EstadoSolicitud,
    PropositoTenencia,
    TipoVivienda,
)


class AdoptionFlowTests(UbicacionCompletaTestMixin, TestCase):
    def setUp(self):
        self.animal = Animal.objects.create(
            nombre="Canela",
            especie=Especie.PERRO,
            sexo=Sexo.HEMBRA,
            tamano=Tamano.MEDIANO,
            descripcion="x",
            estado=EstadoAnimal.EN_ADOPCION,
            fecha_ingreso=date.today(),
        )

    def _datos_solicitud(self):
        return {
            "nombre_solicitante": "María Pérez",
            "cedula": "1804567890",
            "telefono": "0991234567",
            "email": "maria@example.com",
            "barrio": "Av. Siempre Viva 123",
            "parroquia": "HCH",
            "canton": "AM",
            "tipo_vivienda": TipoVivienda.CASA,
            "tiene_patio": True,
            "experiencia": "He tenido perros.",
            "proposito": PropositoTenencia.COMPANIA,
        }

    def test_solicitud_publica_crea_registro(self):
        resp = self.client.post(
            reverse("adoptions:apply", args=[self.animal.pk]), {**self._datos_solicitud(), "acepta_privacidad": True}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(AdoptionApplication.objects.count(), 1)

    def test_aprobar_solicitud_marca_animal_adoptado(self):
        solicitud = AdoptionApplication.objects.create(animal=self.animal, **self._datos_solicitud())
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")
        self.client.post(
            reverse("adoptions:update_status", args=[solicitud.pk]),
            {"estado": EstadoSolicitud.APROBADA, "notas_internas": ""},
        )
        self.animal.refresh_from_db()
        self.assertEqual(self.animal.estado, EstadoAnimal.ADOPTADO)

    def crear_instancia(self, canton, parroquia, barrio) -> AdoptionApplication:
        animal = crear_animal(barrio=barrio, parroquia=parroquia, canton=canton)
        data_solicitud = self._datos_solicitud()
        data_solicitud.update({"barrio": barrio, "parroquia": parroquia, "canton": canton})
        return AdoptionApplication.objects.create(animal=animal, **data_solicitud)
