from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import staff_required
from animals.models import Animal, EstadoAnimal

from .forms import AdoptionApplicationForm, FollowUpForm, StatusForm
from .models import AdoptionApplication, EstadoSolicitud


def apply(request, animal_pk):
    """Formulario público para solicitar la adopción de un animal."""
    animal = get_object_or_404(Animal, pk=animal_pk)
    if not animal.en_adopcion:
        messages.warning(request, "Este animal no está disponible para adopción.")
        return redirect(animal.get_absolute_url())

    form = AdoptionApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        solicitud = form.save(commit=False)
        solicitud.animal = animal
        if request.user.is_authenticated:
            solicitud.usuario = request.user
        solicitud.save()
        messages.success(
            request,
            "¡Gracias! Tu solicitud fue enviada. La fundación se pondrá en contacto contigo.",
        )
        return redirect(animal.get_absolute_url())
    return render(request, "adoptions/apply.html", {"animal": animal, "form": form})


# --- Panel administrativo (staff) ---

@staff_required
def manage_list(request):
    solicitudes = AdoptionApplication.objects.select_related("animal")
    estado = request.GET.get("estado", "")
    if estado:
        solicitudes = solicitudes.filter(estado=estado)
    return render(
        request,
        "adoptions/manage_list.html",
        {
            "solicitudes": solicitudes,
            "estados": EstadoSolicitud.choices,
            "estado_sel": estado,
        },
    )


@staff_required
def manage_detail(request, pk):
    solicitud = get_object_or_404(
        AdoptionApplication.objects.select_related("animal"), pk=pk
    )
    status_form = StatusForm(instance=solicitud)
    followup_form = FollowUpForm()
    return render(
        request,
        "adoptions/manage_detail.html",
        {
            "solicitud": solicitud,
            "status_form": status_form,
            "followup_form": followup_form,
        },
    )


@staff_required
def update_status(request, pk):
    solicitud = get_object_or_404(AdoptionApplication, pk=pk)
    if request.method == "POST":
        form = StatusForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()
            if solicitud.estado == EstadoSolicitud.APROBADA:
                solicitud.animal.estado = EstadoAnimal.ADOPTADO
                solicitud.animal.save(update_fields=["estado"])
                messages.success(
                    request,
                    f"Solicitud aprobada. «{solicitud.animal.nombre}» marcado como adoptado.",
                )
            else:
                messages.success(request, "Estado de la solicitud actualizado.")
    return redirect("adoptions:manage_detail", pk=pk)


@staff_required
def print_sheet(request, pk):
    """Ficha imprimible con los datos de la persona aceptada a adoptar."""
    solicitud = get_object_or_404(
        AdoptionApplication.objects.select_related("animal"), pk=pk
    )
    if solicitud.estado != EstadoSolicitud.APROBADA:
        messages.warning(
            request,
            "La ficha solo está disponible para solicitudes aprobadas.",
        )
        return redirect("adoptions:manage_detail", pk=pk)
    return render(request, "adoptions/print_sheet.html", {"solicitud": solicitud})


@staff_required
def add_followup(request, pk):
    solicitud = get_object_or_404(AdoptionApplication, pk=pk)
    if request.method == "POST":
        form = FollowUpForm(request.POST, request.FILES)
        if form.is_valid():
            followup = form.save(commit=False)
            followup.solicitud = solicitud
            followup.save()
            messages.success(request, "Seguimiento registrado.")
        else:
            messages.error(request, "No se pudo registrar el seguimiento.")
    return redirect("adoptions:manage_detail", pk=pk)
