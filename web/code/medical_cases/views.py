from django.contrib import messages
from django.db.models import Case, When
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import staff_required

from .forms import (
    CasePhotoForm,
    CaseUpdateForm,
    ExpenseForm,
    MedicalCaseForm,
    PublicDonationForm,
    StaffDonationForm,
)
from .models import EstadoCaso, MedicalCase


def case_list(request):
    """Listado público de casos médicos (activos primero, cerrados al final)."""
    casos = MedicalCase.objects.order_by(
        Case(When(estado=EstadoCaso.CERRADO, then=1), default=0), "-creado"
    )
    return render(request, "medical_cases/list.html", {"casos": casos})


def detail(request, pk):
    caso = get_object_or_404(MedicalCase, pk=pk)
    form = PublicDonationForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            donacion = form.save(commit=False)
            donacion.caso = caso
            donacion.verificado = False
            donacion.save()
            messages.success(
                request,
                "¡Gracias por tu aporte! La fundación verificará tu donación pronto.",
            )
            return redirect(caso.get_absolute_url())
    return render(request, "medical_cases/detail.html", {"caso": caso, "form": form})


# --- Panel administrativo (staff) ---

@staff_required
def manage_list(request):
    casos = MedicalCase.objects.all()
    return render(request, "medical_cases/manage_list.html", {"casos": casos})


@staff_required
def manage_create(request):
    form = MedicalCaseForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        caso = form.save()
        messages.success(request, "Caso médico creado.")
        return redirect("medical_cases:manage_detail", pk=caso.pk)
    return render(
        request, "medical_cases/manage_form.html", {"form": form, "titulo": "Nuevo caso médico"}
    )


@staff_required
def manage_update(request, pk):
    caso = get_object_or_404(MedicalCase, pk=pk)
    form = MedicalCaseForm(request.POST or None, request.FILES or None, instance=caso)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Caso actualizado.")
        return redirect("medical_cases:manage_detail", pk=caso.pk)
    return render(
        request,
        "medical_cases/manage_form.html",
        {"form": form, "titulo": f"Editar: {caso.titulo}"},
    )


@staff_required
def manage_detail(request, pk):
    caso = get_object_or_404(MedicalCase, pk=pk)
    return render(
        request,
        "medical_cases/manage_detail.html",
        {
            "caso": caso,
            "donation_form": StaffDonationForm(),
            "update_form": CaseUpdateForm(),
            "photo_form": CasePhotoForm(),
            "expense_form": ExpenseForm(),
        },
    )


@staff_required
def add_donation(request, pk):
    caso = get_object_or_404(MedicalCase, pk=pk)
    if request.method == "POST":
        form = StaffDonationForm(request.POST, request.FILES)
        if form.is_valid():
            donacion = form.save(commit=False)
            donacion.caso = caso
            donacion.save()
            messages.success(request, "Donación registrada.")
        else:
            messages.error(request, "No se pudo registrar la donación.")
    return redirect("medical_cases:manage_detail", pk=pk)


@staff_required
def verify_donation(request, pk, donation_pk):
    caso = get_object_or_404(MedicalCase, pk=pk)
    donacion = get_object_or_404(caso.donaciones, pk=donation_pk)
    if request.method == "POST":
        donacion.verificado = not donacion.verificado
        donacion.save(update_fields=["verificado"])
        estado = "verificada" if donacion.verificado else "marcada como pendiente"
        messages.success(request, f"Donación {estado}.")
    return redirect("medical_cases:manage_detail", pk=pk)


@staff_required
def add_update(request, pk):
    caso = get_object_or_404(MedicalCase, pk=pk)
    if request.method == "POST":
        form = CaseUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            avance = form.save(commit=False)
            avance.caso = caso
            avance.save()
            messages.success(request, "Avance publicado.")
        else:
            messages.error(request, "No se pudo publicar el avance.")
    return redirect("medical_cases:manage_detail", pk=pk)


@staff_required
def add_photo(request, pk):
    caso = get_object_or_404(MedicalCase, pk=pk)
    if request.method == "POST":
        form = CasePhotoForm(request.POST, request.FILES)
        if form.is_valid():
            foto = form.save(commit=False)
            foto.caso = caso
            foto.save()
            messages.success(request, "Foto añadida a la galería.")
        else:
            messages.error(request, "No se pudo añadir la foto.")
    return redirect("medical_cases:manage_detail", pk=pk)


@staff_required
def delete_photo(request, pk, photo_pk):
    caso = get_object_or_404(MedicalCase, pk=pk)
    foto = get_object_or_404(caso.fotos, pk=photo_pk)
    if request.method == "POST":
        foto.delete()
        messages.success(request, "Foto eliminada.")
    return redirect("medical_cases:manage_detail", pk=pk)


@staff_required
def add_expense(request, pk):
    caso = get_object_or_404(MedicalCase, pk=pk)
    if request.method == "POST":
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            egreso = form.save(commit=False)
            egreso.caso = caso
            egreso.save()
            messages.success(request, "Egreso registrado.")
        else:
            messages.error(request, "No se pudo registrar el egreso.")
    return redirect("medical_cases:manage_detail", pk=pk)


@staff_required
def delete_expense(request, pk, expense_pk):
    caso = get_object_or_404(MedicalCase, pk=pk)
    egreso = get_object_or_404(caso.egresos, pk=expense_pk)
    if request.method == "POST":
        egreso.delete()
        messages.success(request, "Egreso eliminado.")
    return redirect("medical_cases:manage_detail", pk=pk)


@staff_required
def toggle_status(request, pk):
    caso = get_object_or_404(MedicalCase, pk=pk)
    if request.method == "POST":
        caso.estado = (
            EstadoCaso.CERRADO if caso.estado == EstadoCaso.ACTIVO else EstadoCaso.ACTIVO
        )
        caso.save(update_fields=["estado"])
        messages.success(request, f"Caso marcado como {caso.get_estado_display()}.")
    return redirect("medical_cases:manage_detail", pk=pk)
