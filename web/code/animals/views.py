from django.contrib import messages
from django.db.models import BooleanField, Case, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import staff_required

from .forms import AnimalForm, AnimalPhotoForm, MedicalRecordForm
from .models import (
    MESES_FEATURED_COMUNITARIO,
    Animal,
    Especie,
    EstadoAnimal,
    Origen,
    Sexo,
    Tamano,
    restar_meses,
)


def catalog(request):
    """Catálogo público de animales en adopción, con filtros vía HTMX."""
    animales = Animal.objects.filter(estado=EstadoAnimal.EN_ADOPCION)

    especie = request.GET.get("especie", "")
    sexo = request.GET.get("sexo", "")
    tamano = request.GET.get("tamano", "")
    if especie:
        animales = animales.filter(especie=especie)
    if sexo:
        animales = animales.filter(sexo=sexo)
    if tamano:
        animales = animales.filter(tamano=tamano)

    # Destacados primero: marcados como vulnerables por el staff o comunitarios
    # esterilizados hace menos de 6 meses.
    limite = restar_meses(timezone.now().date(), MESES_FEATURED_COMUNITARIO)
    destacado_q = Q(destacado=True) | Q(
        origen=Origen.COMUNITARIO,
        esterilizado=True,
        fecha_esterilizacion__gte=limite,
    )
    animales = animales.annotate(
        _destacado=Case(
            When(destacado_q, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        )
    ).order_by("-_destacado", "-fecha_ingreso", "nombre")

    context = {
        "animales": animales,
        "especies": Especie.choices,
        "sexos": Sexo.choices,
        "tamanos": Tamano.choices,
        "filtros": {"especie": especie, "sexo": sexo, "tamano": tamano},
    }
    if request.htmx:
        return render(request, "animals/_animal_grid.html", context)
    return render(request, "animals/catalog.html", context)


def detail(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    return render(request, "animals/detail.html", {"animal": animal})


# --- Panel administrativo (staff) ---

@staff_required
def manage_list(request):
    animales = Animal.objects.all()
    estado = request.GET.get("estado", "")
    if estado:
        animales = animales.filter(estado=estado)
    return render(
        request,
        "animals/manage_list.html",
        {"animales": animales, "estados": EstadoAnimal.choices, "estado_sel": estado},
    )


@staff_required
def manage_create(request):
    form = AnimalForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        animal = form.save()
        messages.success(request, f"Animal «{animal.nombre}» registrado.")
        return redirect("animals:manage_detail", pk=animal.pk)
    return render(request, "animals/manage_form.html", {"form": form, "titulo": "Nuevo animal"})


@staff_required
def manage_update(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    form = AnimalForm(request.POST or None, request.FILES or None, instance=animal)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cambios guardados.")
        return redirect("animals:manage_detail", pk=animal.pk)
    return render(
        request,
        "animals/manage_form.html",
        {"form": form, "titulo": f"Editar {animal.nombre}"},
    )


@staff_required
def manage_detail(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    return render(
        request,
        "animals/manage_detail.html",
        {
            "animal": animal,
            "photo_form": AnimalPhotoForm(),
            "medical_form": MedicalRecordForm(),
        },
    )


@staff_required
def manage_delete(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    if request.method == "POST":
        nombre = animal.nombre
        animal.delete()
        messages.success(request, f"Animal «{nombre}» eliminado.")
        return redirect("animals:manage_list")
    return render(request, "animals/manage_confirm_delete.html", {"animal": animal})


@staff_required
def add_photo(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    form = AnimalPhotoForm(request.POST, request.FILES)
    if form.is_valid():
        photo = form.save(commit=False)
        photo.animal = animal
        photo.save()
        messages.success(request, "Foto agregada.")
    else:
        messages.error(request, "No se pudo agregar la foto.")
    return redirect("animals:manage_detail", pk=animal.pk)


@staff_required
def add_medical_record(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    form = MedicalRecordForm(request.POST)
    if form.is_valid():
        record = form.save(commit=False)
        record.animal = animal
        record.save()
        messages.success(request, "Registro médico agregado.")
    else:
        messages.error(request, "No se pudo agregar el registro médico.")
    return redirect("animals:manage_detail", pk=animal.pk)
