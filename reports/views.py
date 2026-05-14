from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import staff_required

from .forms import ReportForm
from .models import EstadoReporte, Report, ReportPhoto, TipoReporte


def report_list(request):
    """Tablero público de reportes."""
    reportes = Report.objects.prefetch_related("fotos")
    tipo = request.GET.get("tipo", "")
    if tipo:
        reportes = reportes.filter(tipo=tipo)
    return render(
        request,
        "reports/list.html",
        {"reportes": reportes, "tipos": TipoReporte.choices, "tipo_sel": tipo},
    )


def detail(request, pk):
    reporte = get_object_or_404(Report, pk=pk)
    return render(request, "reports/detail.html", {"reporte": reporte})


def create(request):
    """Formulario público para crear un reporte, con carga de fotos."""
    form = ReportForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        reporte = form.save()
        for imagen in request.FILES.getlist("fotos"):
            ReportPhoto.objects.create(reporte=reporte, imagen=imagen)
        messages.success(
            request, "Tu reporte fue publicado. ¡Gracias por ayudar a la comunidad!"
        )
        return redirect(reporte.get_absolute_url())
    return render(request, "reports/create.html", {"form": form})


# --- Panel administrativo (staff) ---

@staff_required
def manage_list(request):
    reportes = Report.objects.all()
    estado = request.GET.get("estado", "")
    if estado:
        reportes = reportes.filter(estado=estado)
    return render(
        request,
        "reports/manage_list.html",
        {"reportes": reportes, "estados": EstadoReporte.choices, "estado_sel": estado},
    )


@staff_required
def toggle_status(request, pk):
    reporte = get_object_or_404(Report, pk=pk)
    if request.method == "POST":
        reporte.estado = (
            EstadoReporte.RESUELTO
            if reporte.estado == EstadoReporte.ABIERTO
            else EstadoReporte.ABIERTO
        )
        reporte.save(update_fields=["estado"])
        messages.success(request, f"Reporte marcado como {reporte.get_estado_display()}.")
    return redirect("reports:detail", pk=pk)
