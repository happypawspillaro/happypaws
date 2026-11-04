from datetime import date, timedelta

from accounts.models import User
from constants import N_MAXIMO_OBJETOS_POR_PAGINA
from core.tests_common.mixins import PaginacionTestMixin, UbicacionCompletaTestMixin
from django.test import TestCase
from django.urls import reverse

from .models import Animal, Especie, EstadoAnimal, Sexo, Tamano


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


class AnimalTests(UbicacionCompletaTestMixin, TestCase):
    def crear_instancia(self, canton, parroquia, barrio) -> Animal:
        return crear_animal(barrio=barrio, parroquia=parroquia, canton=canton)


class AnimalModelTests(TestCase):
    def test_en_adopcion_property(self):
        a = crear_animal(estado=EstadoAnimal.EN_ADOPCION)
        b = crear_animal(nombre="Otro", estado=EstadoAnimal.ADOPTADO)
        self.assertTrue(a.en_adopcion)
        self.assertFalse(b.en_adopcion)

    def test_tiene_tutor(self):
        con = crear_animal(tutor_nombre="María")
        sin = crear_animal(nombre="Sin tutor", tutor_nombre="")
        self.assertTrue(con.tiene_tutor)
        self.assertFalse(sin.tiene_tutor)

    def test_ubicacion_completa_omite_vacios(self):
        self.assertEqual(
            crear_animal(barrio="San Luis", parroquia="LM", canton="PI").ubicacion_completa,
            "Píllaro / La Matriz / San Luis",
        )
        self.assertEqual(
            crear_animal(nombre="x", barrio=None, parroquia="SA", canton="PI").ubicacion_completa,
            "Píllaro / San Andrés",
        )


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

    def test_muestra_hace_cuando_esta_en_adopcion(self):
        crear_animal(nombre="Firulais", fecha_ingreso=date.today() - timedelta(days=70))
        resp = self.client.get(reverse("animals:catalog"))
        self.assertContains(resp, "En adopción hace")
        self.assertContains(resp, "meses")


class StaffAccessTests(TestCase):
    def test_gestion_requiere_staff(self):
        resp = self.client.get(reverse("animals:manage_list"))
        self.assertEqual(resp.status_code, 302)

    def test_staff_accede_a_gestion(self):
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")
        resp = self.client.get(reverse("animals:manage_list"))
        self.assertEqual(resp.status_code, 200)

    def test_muestra_whatsapp_de_tutor_sin_nombre(self):
        """Un contacto sin nombre de tutor igual debe mostrar el botón (issue #46)."""
        animal = crear_animal(tutor_nombre="", tutor_contacto="0991234567")
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")
        resp = self.client.get(reverse("animals:manage_detail", args=[animal.pk]))
        self.assertContains(resp, "https://wa.me/593991234567")

    def test_editar_conserva_fecha_ingreso(self):
        """El formulario de edición muestra la fecha guardada en formato ISO (issue #90)."""
        animal = crear_animal(fecha_ingreso=date(2026, 3, 5), fecha_esterilizacion=date(2026, 4, 1))
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")
        resp = self.client.get(reverse("animals:manage_update", args=[animal.pk]))
        self.assertContains(resp, 'value="2026-03-05"')
        self.assertContains(resp, 'value="2026-04-01"')


# web/code/animals/tests.py
class TestAnimalesView(PaginacionTestMixin, TestCase):
    """Prueba la paginación y los filtros combinados en las vistas de animales."""

    N_MAX_PAGINAS = 3
    VIEWS = ["animals:catalog", "animals:manage_list"]
    model = Animal
    context_name = "animales"
    atributo_busqueda = "nombre"

    def crear_objeto(self, **kwargs):
        """Método puente para usar la función de fábrica con valores por defecto."""
        return crear_animal(**kwargs)

    def setUp(self):
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")
        for i in range(N_MAXIMO_OBJETOS_POR_PAGINA * self.N_MAX_PAGINAS):
            crear_animal(nombre=f"Animal {i+1}")

    def test_paginacion_con_filtro_sexo(self):
        """Prueba que la paginación funcione correctamente filtrando por sexo."""
        self.assert_paginacion_con_filtro(
            view_name="animals:manage_list",
            param_query=f"sexo={Sexo.MACHO}",
            kwargs_creacion_match={"sexo": Sexo.MACHO},
            kwargs_creacion_no_match={"sexo": Sexo.HEMBRA},
            prefijo_nombre="AnimSexo",
        )

    def test_paginacion_con_filtro_tamano(self):
        """Prueba que la paginación funcione correctamente filtrando por tamaño."""
        self.assert_paginacion_con_filtro(
            view_name="animals:manage_list",
            param_query=f"tamano={Tamano.GRANDE}",
            kwargs_creacion_match={"tamano": Tamano.GRANDE},
            kwargs_creacion_no_match={"tamano": Tamano.PEQUENO},
            prefijo_nombre="AnimTam",
        )

    def test_paginacion_con_filtro_estado(self):
        """Prueba que la paginación funcione correctamente filtrando por estado."""
        self.assert_paginacion_con_filtro(
            view_name="animals:manage_list",
            param_query=f"estado={EstadoAnimal.ADOPTADO}",
            kwargs_creacion_match={"estado": EstadoAnimal.ADOPTADO},
            kwargs_creacion_no_match={"estado": EstadoAnimal.EN_ADOPCION},
            prefijo_nombre="AnimEst",
        )
