import logging
from decimal import Decimal

from accounts.decorators import staff_required
from adoptions.models import AdoptionApplication, EstadoSolicitud
from animals.models import Animal, EstadoAnimal
from constants import DIAS_CONTACTO_VISIBLE, PARROQUIAS_CANTON
from core.cache import obtener_locaciones
from django.db.models import Count, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from medical_cases.models import Donation, EstadoCaso, MedicalCase
from reports.models import EstadoReporte, Report

logger = logging.getLogger(__name__)


# Sección Fundación
class QuienesSomosView(TemplateView):
    template_name = "core/fundacion/quienes_somos.html"


class DirectivaView(TemplateView):
    template_name = "core/fundacion/directiva.html"


class ReconocimientosView(TemplateView):
    template_name = "core/fundacion/reconocimientos.html"


class ImpactoView(TemplateView):
    template_name = "core/fundacion/impacto.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "campanas_photo": None,
                "campanas_gallery": [
                    {
                        "src": "assets/impacto/campanas/poalo.jpg",
                        "alt": (
                            "Charla de cuidados Post-quirúrgicos por el equipo de Voluntarios "
                            "Happy Paws Píllaro San José de Poaló"
                        ),
                        "caption": "Campaña de Esterilización San José de Poaló, Agosto 2025",
                    },
                    {
                        "src": "assets/impacto/campanas/yacupamba.jpg",
                        "alt": "Mascotas recién esterilizadas recuperandose en Yacupamba, San Miguelito",
                        "caption": "Campaña de Esterilización Yacupamba San Miguelito, Diciembre 2025",
                    },
                    {
                        "src": "assets/impacto/campanas/urbina.png",
                        "alt": "Tutores esperando su  turno para esterilizar a sus mascotas, Presidente Urbina",
                        "caption": "Tutores esperando su turno Campaña de Esterilización Presidente Urbina, Enero 2026",
                    },
                ],
                "emergencias_gallery": [
                    {
                        "src": "assets/impacto/emergencias/bruce.jpg",
                        "alt": "Bruce en recuperación después de su amputación, 2026",
                        "caption": "Bruce tenía una fractura desplazada en su pata izquierda, atendimos su amputación",
                    },
                    {
                        "src": "assets/impacto/emergencias/cholito.jpg",
                        "alt": "Cholito recuperándose luego de su cirugía",
                        "caption": "Luego de un atropellamiento y sin curación, se le tuvo que apuntar la pata",
                    },
                    {
                        "src": "assets/impacto/emergencias/lulu.png",
                        "alt": "Lulu recuperándose en un hogar temporal",
                        "caption": "Lulu fue encontrada con una fuerte lesión del ojo, se realizó enucleación",
                    },
                ],
                "concientizacion_gallery": [
                    {
                        "src": "assets/impacto/concientizacion/urbina.png",
                        "alt": "Tutores atendiendo la charla de Concientización Presidente Urbina",
                        "caption": "Charla de concientización y tenencia responsable Presidente Urbina",
                    },
                    {
                        "src": "assets/impacto/concientizacion/yacupamba.jpg",
                        "alt": "Responsabilidad con sus mascotas de nuestro equipo veterinario en Yacupamba",
                        "caption": "Charla de concientización por parte de nuestro equipo veterinario, Yacupamba",
                    },
                    {
                        "src": "assets/impacto/concientizacion/sanmiguelito.png",
                        "alt": "La comunidad tiene voz en la concientización en San Miguelito",
                        "caption": "Líderes locales dando su opinión sobre la fauna urbana en San Miguelito",
                    },
                ],
                "gestion_publica_photo": {
                    "src": "assets/impacto/gestion/mesa_intersectorial_urbina.png",
                    "alt": "Reunión de trabajo por la fauna urbana en el GADP Presidente Urbina",
                    "caption": "Participación Mesa Intersectorial Presidente Urbina",
                },
            }
        )
        return context


# Sección Proyectos e impacto
class AreasTrabajoView(TemplateView):
    template_name = "core/proyectos_impacto/areas_trabajo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "eventos_gallery": [
                    {
                        "src": "assets/areas_trabajo/eventos/match_canino_2026.jpg",
                        "alt": "2do Match Canino Presidente Urbina 2025",
                        "caption": (
                            "Segundo Match Canino '!Tenencia con amor, dile no al dolor¡'"
                            "Presidente Urbina, Noviembre 2025, Octubre de 2026"
                        ),
                    },
                    {
                        "src": "assets/areas_trabajo/eventos/match_canino_2025.jpg",
                        "alt": "1er Match Canino Presidente Urbina 2025",
                        "caption": ("Primer Match Canino Presidente Urbina, Noviembre 2025" ", Noviembre de 2025"),
                    },
                    {
                        "src": "assets/areas_trabajo/eventos/evento_sm.jpg",
                        "alt": "Evento Concientización San Miguelito de Píllaro",
                        "caption": (
                            "Evento ¡Concientiza San Miguelito! Vamos a cuidar a nuestros animalitos"
                            ", Noviembre de 2024"
                        ),
                    },
                ],
                "gestion_gallery": [
                    {
                        "src": "assets/impacto/gestion/mesa_intersectorial_urbina.png",
                        "alt": "Reunión de trabajo por la fauna urbana en el GADP Presidente Urbina",
                        "caption": "Participación Mesa Intersectorial Presidente Urbina",
                    }
                ],
            }
        )
        return context


class FaunaUrbanaView(TemplateView):
    template_name = "core/proyectos_impacto/fauna_urbana.html"


class SoftwareLibreView(TemplateView):
    template_name = "core/proyectos_impacto/software_libre.html"


class MediosComunicacionView(TemplateView):
    template_name = "core/proyectos_impacto/medios_comunicacion.html"


# Sección Base Legal y Contacto
class MarcoLegalView(TemplateView):
    template_name = "core/transparencia_recursos/marco_legal.html"


class FormatosView(TemplateView):
    template_name = "core/transparencia_recursos/formatos.html"


class ContactosView(TemplateView):
    template_name = "core/transparencia_recursos/contactos.html"


# Sección Contribuir
class ContribuyeView(TemplateView):
    template_name = "core/contribuir/contribuye.html"


def home(request):
    animales = Animal.objects.filter(estado=EstadoAnimal.EN_ADOPCION)[:6]
    casos = MedicalCase.objects.filter(estado=EstadoCaso.ACTIVO)[:3]
    return render(request, "core/home.html", {"animales": animales, "casos": casos})


def privacidad(request):
    """Política de privacidad y uso de cookies (#75)."""
    return render(request, "core/privacidad.html", {"dias_contacto_visible": DIAS_CONTACTO_VISIBLE})


@staff_required
def dashboard(request):
    animales_por_estado = {
        item["estado"]: item["total"] for item in Animal.objects.values("estado").annotate(total=Count("id"))
    }
    estados_animal = [(label, animales_por_estado.get(value, 0)) for value, label in EstadoAnimal.choices]

    total_recaudado = Donation.objects.filter(verificado=True).aggregate(s=Sum("monto"))["s"] or Decimal("0")

    context = {
        "total_animales": Animal.objects.count(),
        "estados_animal": estados_animal,
        "total_adoptados": animales_por_estado.get(EstadoAnimal.ADOPTADO, 0),
        "en_adopcion": animales_por_estado.get(EstadoAnimal.EN_ADOPCION, 0),
        "solicitudes_pendientes": AdoptionApplication.objects.filter(estado=EstadoSolicitud.PENDIENTE).count(),
        "solicitudes_total": AdoptionApplication.objects.count(),
        "casos_activos": MedicalCase.objects.filter(estado=EstadoCaso.ACTIVO).count(),
        "total_recaudado": total_recaudado,
        "reportes_abiertos": Report.objects.filter(estado=EstadoReporte.ABIERTO).count(),
        "donaciones_pendientes": Donation.objects.filter(verificado=False).count(),
        "ultimas_solicitudes": AdoptionApplication.objects.select_related("animal")[:5],
        "ultimos_reportes": Report.objects.all()[:5],
    }
    return render(request, "core/dashboard.html", context)


def listar_canton_parroquia(request):
    canton = request.GET.get("canton") or ""

    selected_parroquia = request.GET.get("parroquia") or ""

    parroquias = PARROQUIAS_CANTON.get(canton, [])

    return render(
        request,
        "core/partials/opciones_parroquias.html",
        {
            "parroquias": parroquias,
            "selected_parroquia": selected_parroquia,
        },
    )


def obtener_barrios(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("barrio", "").strip().lower()
    canton = request.GET.get("canton", "").strip()
    parroquia = request.GET.get("parroquia", "").strip()

    locaciones = obtener_locaciones()

    barrios_dict = locaciones.get(canton, {}).get(parroquia, {})

    barrios = sorted(barrio for barrio in barrios_dict if query in barrio.lower())

    return render(
        request,
        "core/partials/sugerencia_barrios.html",
        {"barrios": barrios},
    )
