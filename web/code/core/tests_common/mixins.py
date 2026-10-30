from constants import N_MAXIMO_OBJETOS_POR_PAGINA
from django.urls import reverse


class UbicacionCompletaTestMixin:
    """Mixin global para probar la propiedad ubicacion_completa en cualquier modelo."""

    def crear_instancia(self, canton, parroquia, barrio):
        """Método que las clases hijas deben implementar obligatoriamente."""
        raise NotImplementedError("Las clases hijas deben implementar crear_instancia")

    def test_formatear_ubicacion_completa(self):
        casos_ubicacion_esperada = [
            ("PI", "SM", "Yacupamba", "Píllaro / San Miguelito / Yacupamba"),
            ("PA", "LA", None, "Patate / Los Andes"),
            ("AM", "IZA", "Yacupamba", "Ambato / Izamba / Yacupamba"),
            ("PE", "GM", None, "Pelileo / García Moreno"),
        ]

        for canton, parroquia, barrio, texto_esperado in casos_ubicacion_esperada:
            with self.subTest(canton=canton, parroquia=parroquia, barrio=barrio):
                instancia = self.crear_instancia(canton=canton, parroquia=parroquia, barrio=barrio)
                self.assertEqual(instancia.ubicacion_completa, texto_esperado)


class PaginacionTestMixin:
    """Mixin genérico para probar la paginación y su combinación con filtros en vistas de listas."""

    N_MAX_PAGINAS = 3
    VIEWS = []
    model = None
    context_name = ""
    atributo_busqueda = "nombre"

    def test_paginacion_vistas(self):
        """Prueba que cada página muestre los elementos correctos y oculte los de la siguiente."""
        todos_los_elementos = list(
            self.model.objects.all().order_by("-fecha_avistamiento", "-creado")
            if hasattr(self.model, "fecha_avistamiento")
            else self.model.objects.all()
        )
        for view_name in self.VIEWS:
            with self.subTest(view_name=view_name):
                for n_pagina in range(1, self.N_MAX_PAGINAS + 1):
                    with self.subTest(n_pagina=n_pagina):
                        url = reverse(view_name) + f"?page={n_pagina}"
                        response = self.client.get(url)

                        self.assertEqual(response.status_code, 200)

                        inicio = (n_pagina - 1) * N_MAXIMO_OBJETOS_POR_PAGINA
                        fin = n_pagina * N_MAXIMO_OBJETOS_POR_PAGINA

                        elementos_pagina_actual = todos_los_elementos[inicio:fin]
                        primer_elemento = elementos_pagina_actual[0]
                        ultimo_elemento = elementos_pagina_actual[-1]

                        self.assertContains(response, getattr(primer_elemento, self.atributo_busqueda))
                        self.assertContains(response, getattr(ultimo_elemento, self.atributo_busqueda))

                        if n_pagina < self.N_MAX_PAGINAS:
                            siguiente_elemento = todos_los_elementos[fin]
                            self.assertNotContains(response, getattr(siguiente_elemento, self.atributo_busqueda))

    def test_primera_pagina_por_defecto(self):
        """Prueba que al acceder sin parámetro page se cargue la primera página con su respectivo límite."""
        for view_name in self.VIEWS:
            with self.subTest(view_name=view_name):
                response = self.client.get(reverse(view_name))
                self.assertEqual(response.status_code, 200)
                self.assertTrue(self.context_name in response.context)
                self.assertEqual(response.context[self.context_name].number, 1)
                self.assertEqual(len(response.context[self.context_name]), N_MAXIMO_OBJETOS_POR_PAGINA)

    def test_pagina_invalida_muestra_primera(self):
        """Si pasan letras o parámetros inválidos, debe caer por defecto en la página 1."""
        for view_name in self.VIEWS:
            with self.subTest(view_name=view_name):
                response = self.client.get(reverse(view_name) + "?page=abc")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context[self.context_name].number, 1)

    def test_pagina_fuera_de_rango(self):
        """Si piden una página muy alta, maneja el límite sin romper la vista."""
        for view_name in self.VIEWS:
            with self.subTest(view_name=view_name):
                response = self.client.get(reverse(view_name) + "?page=999")
                self.assertEqual(response.status_code, 200)

    def assert_paginacion_con_filtro(
        self, view_name, param_query, kwargs_creacion_match, kwargs_creacion_no_match, prefijo_nombre
    ):
        """Método DRY reutilizable para validar la paginación aplicando un filtro específico."""
        self.model.objects.all().delete()

        # 1. Crear suficientes elementos que SÍ coinciden para abarcar al menos 2 páginas
        for i in range(N_MAXIMO_OBJETOS_POR_PAGINA * 2):
            params = {self.atributo_busqueda: f"{prefijo_nombre} Match {i+1}"}
            params.update(kwargs_creacion_match)
            self.crear_objeto(**params)

        # 2. Crear elementos que NO coinciden para asegurar que se excluyen del resultado filtrado
        for i in range(3):
            params = {self.atributo_busqueda: f"{prefijo_nombre} NoMatch {i+1}"}
            params.update(kwargs_creacion_no_match)
            self.crear_objeto(**params)

        # Verificar página 1 del filtro
        url_p1 = reverse(view_name) + f"?{param_query}&page=1"
        res_p1 = self.client.get(url_p1)
        self.assertEqual(res_p1.status_code, 200)
        self.assertEqual(len(res_p1.context[self.context_name]), N_MAXIMO_OBJETOS_POR_PAGINA)
        for i in range(3):
            self.assertNotContains(res_p1, f"{prefijo_nombre} NoMatch {i+1}")

        # Verificar página 2 del filtro
        url_p2 = reverse(view_name) + f"?{param_query}&page=2"
        res_p2 = self.client.get(url_p2)
        self.assertEqual(res_p2.status_code, 200)
        self.assertEqual(len(res_p2.context[self.context_name]), N_MAXIMO_OBJETOS_POR_PAGINA)
        for i in range(3):
            self.assertNotContains(res_p2, f"{prefijo_nombre} NoMatch {i+1}")
