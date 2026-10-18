from datetime import date, timedelta

from accounts.models import User
from constants import N_MAXIMO_OBJETOS_POR_PAGINA
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
            crear_animal(barrio="La Floresta", parroquia="Píllaro").ubicacion_completa,
            "La Floresta, Píllaro",
        )
        self.assertEqual(
            crear_animal(nombre="x", barrio="", parroquia="San Andrés").ubicacion_completa,
            "San Andrés",
        )
        self.assertEqual(crear_animal(nombre="y").ubicacion_completa, "")


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


class TestPaginacion(TestCase):
    """Prueba que la paginación funciona correctamente."""

    N_MAX_PAGINAS = 3
    VIEWS = ["animals:catalog", "animals:manage_list"]

    def setUp(self):
        # Creamos un usuario y autenticamos para poder ejecutar la prueba
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")
        for i in range(N_MAXIMO_OBJETOS_POR_PAGINA * self.N_MAX_PAGINAS):
            crear_animal(nombre=f"Animal {i+1}")

    def test_paginacion_vistas(self):
        """Prueba que cada página muestre los elementos correctos y oculte los de la siguiente."""
        todos_los_animales = list(Animal.objects.all())
        for view_name in self.VIEWS:
            with self.subTest(view_name=view_name):
                for n_pagina in range(1, self.N_MAX_PAGINAS + 1):
                    with self.subTest(n_pagina=n_pagina):
                        url = reverse(view_name) + f"?page={n_pagina}"
                        response = self.client.get(url)

                        self.assertEqual(response.status_code, 200)

                        # Calculamos los índices exactos del slice correspondiente a esta página
                        inicio = (n_pagina - 1) * N_MAXIMO_OBJETOS_POR_PAGINA
                        fin = n_pagina * N_MAXIMO_OBJETOS_POR_PAGINA

                        animales_pagina_actual = todos_los_animales[inicio:fin]

                        # 1. Verificar que los animales de esta página SÍ están en la respuesta
                        primer_animal = animales_pagina_actual[0]
                        ultimo_animal = animales_pagina_actual[-1]

                        self.assertContains(response, primer_animal.nombre)
                        self.assertContains(response, ultimo_animal.nombre)

                        # 2. Verificar que el primer animal de la SIGUIENTE página NO está en esta respuesta
                        if n_pagina < self.N_MAX_PAGINAS:
                            siguiente_animal = todos_los_animales[fin]
                            self.assertNotContains(response, siguiente_animal.nombre)

    def test_primera_pagina_por_defecto(self):
        """Prueba que al acceder sin parámetro page se cargue la primera página con su respectivo límite."""
        for view_name in self.VIEWS:
            with self.subTest(view_name=view_name):
                response = self.client.get(reverse(view_name))
                self.assertEqual(response.status_code, 200)
                self.assertTrue("animales" in response.context)
                self.assertEqual(response.context["animales"].number, 1)
                self.assertEqual(len(response.context["animales"]), N_MAXIMO_OBJETOS_POR_PAGINA)

    def test_pagina_invalida_muestra_primera(self):
        """Si pasan letras o parámetros inválidos, debe caer por defecto en la página 1."""
        for view_name in self.VIEWS:
            with self.subTest(view_name=view_name):
                response = self.client.get(reverse(view_name) + "?page=abc")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["animales"].number, 1)

    def test_pagina_fuera_de_rango(self):
        """Si piden una página muy alta, maneja el límite sin romper la vista."""
        for view_name in self.VIEWS:
            with self.subTest(view_name=view_name):
                response = self.client.get(reverse(view_name) + "?page=999")
                self.assertEqual(response.status_code, 200)
