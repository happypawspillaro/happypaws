from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import staff_required

from .forms import CommentForm, ReportForm, SightingForm
from .models import (
    EstadoReporte,
    Report,
    ReportComment,
    ReportPhoto,
    ReportSighting,
    TipoReporte,
)
from .notifications import notify_report_activity


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


def _detail_context(request, reporte, comment_form=None, sighting_form=None):
    """Contexto del detalle. El staff ve también lo oculto por moderación."""
    es_staff = request.user.is_authenticated and request.user.is_staff
    comentarios = reporte.comentarios.all()
    avistamientos = reporte.avistamientos.all()
    if not es_staff:
        comentarios = comentarios.filter(oculto=False)
        avistamientos = avistamientos.filter(oculto=False)
    return {
        "reporte": reporte,
        "comentarios": comentarios,
        "avistamientos": avistamientos,
        "comment_form": comment_form if comment_form is not None else CommentForm(),
        "sighting_form": sighting_form if sighting_form is not None else SightingForm(),
    }


def detail(request, pk):
    reporte = get_object_or_404(Report, pk=pk)
    return render(request, "reports/detail.html", _detail_context(request, reporte))


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


# --- Interacción pública ---

def add_comment(request, pk):
    """Cualquier persona puede dejar un comentario o pista en un reporte."""
    reporte = get_object_or_404(Report, pk=pk)
    if request.method != "POST":
        return redirect(reporte.get_absolute_url())

    form = CommentForm(request.POST)
    if form.is_valid():
        comentario = form.save(commit=False)
        comentario.reporte = reporte
        comentario.save()
        notify_report_activity(reporte, "comentario", comentario, request)
        messages.success(request, "¡Gracias! Tu comentario fue publicado.")
        return redirect(f"{reporte.get_absolute_url()}#comentarios")

    messages.error(request, "Revisa el formulario: no pudimos publicar tu comentario.")
    return render(
        request, "reports/detail.html", _detail_context(request, reporte, comment_form=form)
    )


def add_sighting(request, pk):
    """Reportar un avistamiento (solo para mascotas perdidas/encontradas)."""
    reporte = get_object_or_404(Report, pk=pk)
    if not reporte.permite_avistamientos:
        messages.warning(request, "Este reporte no admite avistamientos.")
        return redirect(reporte.get_absolute_url())
    if request.method != "POST":
        return redirect(reporte.get_absolute_url())

    form = SightingForm(request.POST, request.FILES)
    if form.is_valid():
        avistamiento = form.save(commit=False)
        avistamiento.reporte = reporte
        avistamiento.save()
        notify_report_activity(reporte, "avistamiento", avistamiento, request)
        messages.success(
            request, "¡Gracias! Tu avistamiento fue registrado y ayuda a la búsqueda."
        )
        return redirect(f"{reporte.get_absolute_url()}#avistamientos")

    messages.error(request, "Revisa el formulario: no pudimos registrar el avistamiento.")
    return render(
        request, "reports/detail.html", _detail_context(request, reporte, sighting_form=form)
    )


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


# --- Moderación de la interacción (staff) ---

@staff_required
def toggle_comment(request, pk):
    """Oculta o muestra un comentario."""
    comentario = get_object_or_404(ReportComment, pk=pk)
    if request.method == "POST":
        comentario.oculto = not comentario.oculto
        comentario.save(update_fields=["oculto"])
        estado = "ocultado" if comentario.oculto else "visible de nuevo"
        messages.success(request, f"Comentario {estado}.")
    return redirect(f"{comentario.reporte.get_absolute_url()}#comentarios")


@staff_required
def delete_comment(request, pk):
    comentario = get_object_or_404(ReportComment, pk=pk)
    url = comentario.reporte.get_absolute_url()
    if request.method == "POST":
        comentario.delete()
        messages.success(request, "Comentario eliminado.")
    return redirect(f"{url}#comentarios")


@staff_required
def toggle_sighting(request, pk):
    """Oculta o muestra un avistamiento."""
    avistamiento = get_object_or_404(ReportSighting, pk=pk)
    if request.method == "POST":
        avistamiento.oculto = not avistamiento.oculto
        avistamiento.save(update_fields=["oculto"])
        estado = "ocultado" if avistamiento.oculto else "visible de nuevo"
        messages.success(request, f"Avistamiento {estado}.")
    return redirect(f"{avistamiento.reporte.get_absolute_url()}#avistamientos")


@staff_required
def confirm_sighting(request, pk):
    """Confirma (o desmarca) un avistamiento como verificado por la fundación."""
    avistamiento = get_object_or_404(ReportSighting, pk=pk)
    if request.method == "POST":
        avistamiento.confirmado = not avistamiento.confirmado
        avistamiento.save(update_fields=["confirmado"])
        estado = "confirmado" if avistamiento.confirmado else "sin confirmar"
        messages.success(request, f"Avistamiento marcado como {estado}.")
    return redirect(f"{avistamiento.reporte.get_absolute_url()}#avistamientos")


@staff_required
def delete_sighting(request, pk):
    avistamiento = get_object_or_404(ReportSighting, pk=pk)
    url = avistamiento.reporte.get_absolute_url()
    if request.method == "POST":
        avistamiento.delete()
        messages.success(request, "Avistamiento eliminado.")
    return redirect(f"{url}#avistamientos")
