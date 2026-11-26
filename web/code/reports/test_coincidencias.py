from datetime import date, timedelta

from accounts.models import User
from constants import Especie, Sexo
from django.test import TestCase
from reports.coincidencias import (
    MAXIMO_SUGERENCIAS,
    buscar_coincidencias,
    obtener_rasgos,
)
from reports.models import EstadoReporte, Report, TipoReporte

PERDIDA_EL = date(2026, 10, 12)


def crear(tipo=TipoReporte.ENCONTRADO, dias=3, **kwargs):
    datos = dict(
        tipo=tipo,
        titulo="Gatita gris",
        descripcion="Tiene collar.",
        canton="PI",
        parroquia="LM",
        barrio="Centro",
        fecha_avistamiento=PERDIDA_EL + timedelta(days=dias),
        especie=Especie.GATO,
        sexo=Sexo.HEMBRA,
        aprobado=True,
    )
    datos.update(kwargs)
    return Report.objects.create(**datos)


class BuscarCoincidenciasTests(TestCase):
    def setUp(self):
        self.perdida = crear(TipoReporte.PERDIDO, dias=0, titulo="Vita se extravió")

    def sugeridos(self, reporte=None, **kwargs):
        return [c.reporte for c in buscar_coincidencias(reporte or self.perdida, **kwargs)]

    def test_funciona_en_los_dos_sentidos(self):
        encontrada = crear()
        self.assertEqual(self.sugeridos(), [encontrada])
        self.assertEqual(self.sugeridos(encontrada), [self.perdida])

    def test_explica_los_motivos(self):
        crear()
        self.assertEqual(
            buscar_coincidencias(self.perdida)[0].motivos,
            ("gato", "hembra", "mismo barrio (Centro)", "3 días de diferencia", "en común: collar"),
        )

    def test_descarta_lo_que_no_puede_ser_la_misma_mascota(self):
        casos = {
            "otra especie": {"especie": Especie.PERRO},
            "especie vacía": {"especie": ""},
            "otro sexo": {"sexo": Sexo.MACHO},
            "encontrada antes de perderse": {"dias": -3},
            "pasó demasiado tiempo": {"dias": 91},
            "mismo tipo": {"tipo": TipoReporte.PERDIDO},
            "maltrato": {"tipo": TipoReporte.MALTRATO},
            "resuelto": {"estado": EstadoReporte.RESUELTO},
            "sin aprobar": {"aprobado": False},
        }
        for nombre, cambios in casos.items():
            with self.subTest(nombre):
                reporte = crear(**cambios)
                self.assertEqual(self.sugeridos(), [])
                reporte.delete()

    def test_tolera_fechas_aproximadas_en_los_dos_sentidos(self):
        for dias in (-2, 90):
            with self.subTest(dias=dias):
                encontrada = crear(dias=dias)
                self.assertEqual(self.sugeridos(), [encontrada])
                self.assertEqual(self.sugeridos(encontrada), [self.perdida])
                encontrada.delete()

    def test_sexo_desconocido_no_descarta(self):
        for sexo in ("", Sexo.DESCONOCIDO):
            with self.subTest(sexo=sexo):
                encontrada = crear(sexo=sexo)
                self.assertEqual(self.sugeridos(), [encontrada])
                encontrada.delete()

    def test_misma_parroquia_sin_rasgos_ni_fecha_cercana_no_basta(self):
        crear(dias=60, barrio="San Luis", titulo="Gatita", descripcion="Es tranquila.")
        self.assertEqual(self.sugeridos(), [])

    def test_mismo_codigo_de_parroquia_en_otro_canton_no_es_la_misma(self):
        # "SA" es San Andrés en Píllaro; se compara junto con el cantón.
        self.perdida.parroquia = "SA"
        crear(canton="AM", parroquia="SA")
        coincidencia = buscar_coincidencias(self.perdida)[0]
        self.assertFalse([m for m in coincidencia.motivos if "parroquia" in m or "barrio" in m])

    def test_ordena_por_parecido_y_limita_la_cantidad(self):
        for _ in range(MAXIMO_SUGERENCIAS):
            crear(barrio="San Luis")
        mejor = crear()
        sugeridos = self.sugeridos()
        self.assertEqual(sugeridos[0], mejor)
        self.assertEqual(len(sugeridos), MAXIMO_SUGERENCIAS)

    def test_reporte_cerrado_o_de_maltrato_no_busca(self):
        crear()
        for cambios in ({"estado": EstadoReporte.RESUELTO}, {"tipo": TipoReporte.MALTRATO}, {"especie": ""}):
            with self.subTest(cambios):
                reporte = crear(**{"tipo": TipoReporte.PERDIDO, "dias": 0, **cambios})
                self.assertEqual(self.sugeridos(reporte), [])

    def test_staff_puede_incluir_los_que_faltan_aprobar(self):
        pendiente = crear(aprobado=False)
        self.assertEqual(self.sugeridos(incluir_sin_aprobar=True), [pendiente])

    def test_no_aumenta_las_consultas_con_mas_candidatos(self):
        for _ in range(5):
            crear()
        with self.assertNumQueries(2):  # candidatos y sus fotos
            buscar_coincidencias(self.perdida)


class ObtenerRasgosTests(TestCase):
    def test_reconoce_variantes_tildes_y_letras_decorativas(self):
        reporte = Report(titulo="Huskey 𝗡𝗲𝗴𝗿𝗮", descripcion="Cálico, con MANCHAS", senales_distinguibles="")
        self.assertEqual(obtener_rasgos(reporte), {"husky", "negro", "cálico", "manchas"})

    def test_ignora_lo_que_no_describe_al_animal(self):
        reporte = Report(titulo="Ayuda", descripcion="Parque central, llama al 0990000000", senales_distinguibles="")
        self.assertEqual(obtener_rasgos(reporte), set())


class CoincidenciasEnDetalleTests(TestCase):
    def setUp(self):
        self.perdida = crear(TipoReporte.PERDIDO, dias=0)

    def test_muestra_el_enlace_y_aclara_que_es_automatico(self):
        encontrada = crear()
        resp = self.client.get(self.perdida.get_absolute_url())
        self.assertContains(resp, 'id="coincidencias"')
        self.assertContains(resp, f'href="{encontrada.get_absolute_url()}"')
        self.assertContains(resp, "Sugerencia automática")

    def test_sin_coincidencias_no_aparece_la_seccion(self):
        self.assertNotContains(self.client.get(self.perdida.get_absolute_url()), 'id="coincidencias"')

    def test_lo_que_falta_aprobar_solo_lo_ve_el_staff(self):
        crear(aprobado=False)
        self.assertNotContains(self.client.get(self.perdida.get_absolute_url()), 'id="coincidencias"')
        self.client.force_login(User.objects.create_user("staff", password="x", is_staff=True))
        self.assertContains(self.client.get(self.perdida.get_absolute_url()), "Sin aprobar")
