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
