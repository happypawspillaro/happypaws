from datetime import date

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User

from .models import (
    Report,
    ReportComment,
    ReportSighting,
    TipoReporte,
)


def crear_reporte(**kwargs):
    defaults = dict(
        tipo=TipoReporte.PERDIDO,
        titulo="Se perdió Toby",
        descripcion="Perro café, collar rojo.",
        ubicacion="Barrio Centro",
        fecha_avistamiento=date.today(),
        nombre_reportante="Ana",
        contacto_reportante="ana@example.com",
    )
    defaults.update(kwargs)
    return Report.objects.create(**defaults)


class CommentTests(TestCase):
    def setUp(self):
        self.reporte = crear_reporte()
        self.url = reverse("reports:add_comment", args=[self.reporte.pk])

    def test_cualquiera_puede_comentar(self):
        resp = self.client.post(
            self.url,
            {"nombre": "Luis", "contacto": "", "mensaje": "Lo vi cerca del parque.", "website": ""},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.reporte.comentarios.count(), 1)

    def test_honeypot_bloquea_spam(self):
        resp = self.client.post(
            self.url,
            {"nombre": "Bot", "mensaje": "spam", "website": "http://spam.com"},
        )
        self.assertEqual(resp.status_code, 200)  # re-render con error
        self.assertEqual(self.reporte.comentarios.count(), 0)

    def test_comentario_oculto_no_se_muestra_al_publico(self):
        ReportComment.objects.create(reporte=self.reporte, nombre="X", mensaje="visible")
        ReportComment.objects.create(
            reporte=self.reporte, nombre="Y", mensaje="escondido", oculto=True
        )
        resp = self.client.get(self.reporte.get_absolute_url())
        self.assertContains(resp, "visible")
        self.assertNotContains(resp, "escondido")

    def test_staff_ve_comentarios_ocultos(self):
        ReportComment.objects.create(
            reporte=self.reporte, nombre="Y", mensaje="escondido", oculto=True
        )
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")
        resp = self.client.get(self.reporte.get_absolute_url())
        self.assertContains(resp, "escondido")


class SightingTests(TestCase):
    def test_avistamiento_en_reporte_perdido(self):
        reporte = crear_reporte(tipo=TipoReporte.PERDIDO)
        resp = self.client.post(
            reverse("reports:add_sighting", args=[reporte.pk]),
            {
                "nombre": "Pedro",
                "contacto": "0991112233",
                "ubicacion": "Av. Bolívar",
                "fecha": date.today().isoformat(),
                "descripcion": "Iba hacia el sur.",
                "website": "",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(reporte.avistamientos.count(), 1)

    def test_maltrato_no_admite_avistamientos(self):
        reporte = crear_reporte(tipo=TipoReporte.MALTRATO)
        self.assertFalse(reporte.permite_avistamientos)
        resp = self.client.post(
            reverse("reports:add_sighting", args=[reporte.pk]),
            {"nombre": "X", "ubicacion": "y", "fecha": date.today().isoformat(), "website": ""},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(reporte.avistamientos.count(), 0)


class ModerationTests(TestCase):
    def setUp(self):
        self.reporte = crear_reporte()
        self.sighting = ReportSighting.objects.create(
            reporte=self.reporte, nombre="P", ubicacion="x", fecha=date.today()
        )
        User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.login(username="staff", password="x")

    def test_confirmar_avistamiento(self):
        self.client.post(reverse("reports:confirm_sighting", args=[self.sighting.pk]))
        self.sighting.refresh_from_db()
        self.assertTrue(self.sighting.confirmado)

    def test_ocultar_avistamiento(self):
        self.client.post(reverse("reports:toggle_sighting", args=[self.sighting.pk]))
        self.sighting.refresh_from_db()
        self.assertTrue(self.sighting.oculto)

    def test_moderacion_requiere_staff(self):
        self.client.logout()
        resp = self.client.post(reverse("reports:confirm_sighting", args=[self.sighting.pk]))
        self.assertEqual(resp.status_code, 302)  # redirige al login
        self.sighting.refresh_from_db()
        self.assertFalse(self.sighting.confirmado)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    FOUNDATION_EMAIL="fundacion@example.com",
)
class NotificationTests(TestCase):
    def test_comentario_envia_correo_al_reportante_y_fundacion(self):
        reporte = crear_reporte(contacto_reportante="ana@example.com")
        self.client.post(
            reverse("reports:add_comment", args=[reporte.pk]),
            {"nombre": "Luis", "mensaje": "Pista", "website": ""},
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("ana@example.com", mail.outbox[0].to)
        self.assertIn("fundacion@example.com", mail.outbox[0].to)

    def test_no_correo_al_reportante_si_dejo_telefono(self):
        reporte = crear_reporte(contacto_reportante="0991234567")
        self.client.post(
            reverse("reports:add_comment", args=[reporte.pk]),
            {"nombre": "Luis", "mensaje": "Pista", "website": ""},
        )
        # Solo va a la fundación, no a un "correo" que en realidad es un teléfono.
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["fundacion@example.com"])
