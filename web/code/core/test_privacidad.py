from datetime import date
from decimal import Decimal

from adoptions.forms import AdoptionApplicationForm
from animals.models import Animal, EstadoAnimal
from constants import DIAS_CONTACTO_VISIBLE
from django.test import TestCase
from django.urls import reverse
from medical_cases.forms import PublicDonationForm
from medical_cases.models import MedicalCase
from reports.forms import CommentForm, ReportForm, SightingForm
from reports.models import Report, TipoReporte


class PaginaPrivacidadTests(TestCase):
    """Política de privacidad pública y enlazada desde todo el sitio (#75)."""

    def test_pagina_responde_con_titulo_y_seccion_de_cookies(self):
        resp = self.client.get(reverse("core:privacidad"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "<h1", count=1)
        self.assertContains(resp, "Política de privacidad")
        self.assertContains(resp, 'id="cookies"')
        self.assertContains(resp, "mailto:happypaws.pillaro@gmail.com")

    def test_muestra_los_dias_que_el_contacto_es_publico(self):
        resp = self.client.get(reverse("core:privacidad"))
        self.assertContains(resp, f"tu contacto hasta {DIAS_CONTACTO_VISIBLE} días")

    def test_footer_enlaza_la_politica_y_el_aviso_de_cookies(self):
        resp = self.client.get(reverse("core:home"))
        self.assertContains(resp, f'href="{reverse("core:privacidad")}"')
        self.assertContains(resp, 'id="aviso-cookies"')
        self.assertContains(resp, "data-abrir-aviso-cookies")
        self.assertContains(resp, "js/consentimiento.js")

    def test_esta_en_el_sitemap(self):
        self.assertContains(self.client.get("/sitemap.xml"), reverse("core:privacidad"))


class ConsentimientoFormulariosTests(TestCase):
    """Todo formulario público que guarda datos personales pide aceptar la política."""

    FORMULARIOS = (AdoptionApplicationForm, PublicDonationForm, ReportForm, CommentForm, SightingForm)

    def test_casilla_obligatoria_en_formularios_publicos(self):
        for formulario in self.FORMULARIOS:
            with self.subTest(formulario=formulario.__name__):
                form = formulario(data={})
                self.assertIn("acepta_privacidad", form.fields)
                self.assertFalse(form.is_valid())
                self.assertIn("Debes aceptar la política de privacidad", str(form.errors["acepta_privacidad"]))

    def test_reporte_sin_aceptar_no_se_guarda(self):
        resp = self.client.post(
            reverse("reports:create"),
            {
                "tipo": TipoReporte.PERDIDO,
                "titulo": "Se perdió Toby",
                "descripcion": "Perro café.",
                "ubicacion": "Barrio Centro",
                "fecha_avistamiento": date.today().isoformat(),
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Debes aceptar la política de privacidad")
        self.assertEqual(Report.objects.count(), 0)

    def test_paginas_con_formulario_muestran_la_casilla(self):
        animal = Animal.objects.create(
            nombre="Luna",
            especie="perro",
            sexo="hembra",
            tamano="mediano",
            descripcion="Juguetona.",
            estado=EstadoAnimal.EN_ADOPCION,
            fecha_ingreso=date.today(),
        )
        caso = MedicalCase.objects.create(titulo="Cirugía", descripcion="...", meta_monto=Decimal("100"))
        reporte = Report.objects.create(
            tipo=TipoReporte.PERDIDO,
            titulo="Se perdió Toby",
            descripcion="...",
            ubicacion="Centro",
            fecha_avistamiento=date.today(),
            aprobado=True,
        )
        for url, cantidad in (
            (reverse("adoptions:apply", args=[animal.pk]), 1),
            (reverse("reports:create"), 1),
            (caso.get_absolute_url(), 1),
            (reporte.get_absolute_url(), 2),  # comentario y avistamiento
        ):
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), 'name="acepta_privacidad"', count=cantidad)
