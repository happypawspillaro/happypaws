from datetime import date

from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Animal, EstadoAnimal, Especie, Sexo, Tamano


def crear_animal(**kwargs):
    defaults = dict(
        nombre="Firulais",
        especie=Especie.PERRO,
        sexo=Sexo.MACHO,
        tamano=Tamano.MEDIANO,
        descripcion="Perro de prueba",
        estado=EstadoAnimal.EN_ADOPCION,
        fecha_ingreso=date.today(),
    )
    defaults.update(kwargs)
    return Animal.objects.create(**defaults)


class AnimalModelTests(TestCase):
    def test_en_adopcion_property(self):
        a = crear_animal(estado=EstadoAnimal.EN_ADOPCION)
        b = crear_animal(nombre="Otro", estado=EstadoAnimal.ADOPTADO)
        self.assertTrue(a.en_adopcion)
        self.assertFalse(b.en_adopcion)


class CatalogViewTests(TestCase):
    def test_catalogo_solo_muestra_en_adopcion(self):
        crear_animal(nombre="Disponible", estado=EstadoAnimal.EN_ADOPCION)
        crear_animal(nombre="Adoptado", estado=EstadoAnimal.ADOPTADO)
        resp = self.client.get(reverse("animals:catalog"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Disponible")
        self.assertNotContains(resp, "Adoptado")

    def test_filtro_por_especie(self):
        crear_animal(nombre="Perrito", especie=Especie.PERRO)
        crear_animal(nombre="Gatito", especie=Especie.GATO)
        resp = self.client.get(reverse("animals:catalog"), {"especie": Especie.GATO})
        self.assertContains(resp, "Gatito")
        self.assertNotContains(resp, "Perrito")


class StaffAccessTests(TestCase):
    def test_gestion_requiere_staff(self):
        resp = self.client.get(reverse("animals:manage_list"))
        self.assertEqual(resp.status_code, 302)

    def test_staff_accede_a_gestion(self):
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")
        resp = self.client.get(reverse("animals:manage_list"))
        self.assertEqual(resp.status_code, 200)
