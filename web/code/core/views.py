import logging
from decimal import Decimal

from accounts.decorators import staff_required
from adoptions.models import AdoptionApplication, EstadoSolicitud
from animals.models import Animal, EstadoAnimal
from cache import obtener_locaciones
from constants import PARROQUIAS_CANTON
from django.db.models import Count, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from medical_cases.models import Donation, EstadoCaso, MedicalCase
from reports.models import EstadoReporte, Report

logger = logging.getLogger(__name__)


def home(request):
    animales = Animal.objects.filter(estado=EstadoAnimal.EN_ADOPCION)[:6]
    casos = MedicalCase.objects.filter(estado=EstadoCaso.ACTIVO)[:3]
    return render(request, "core/home.html", {"animales": animales, "casos": casos})


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
        "registro/partials/barrio_suggestions.html",
        {"barrios": barrios},
    )
