from django.contrib import admin

from .models import Animal, AnimalPhoto, MedicalRecord


class AnimalPhotoInline(admin.TabularInline):
    model = AnimalPhoto
    extra = 1


class MedicalRecordInline(admin.TabularInline):
    model = MedicalRecord
    extra = 0


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        "nombre", "especie", "sexo", "estado", "origen", "parroquia",
        "tutor_nombre", "esterilizado", "destacado", "fecha_ingreso",
    )
    list_filter = (
        "especie", "sexo", "tamano", "estado", "origen", "parroquia",
        "esterilizado", "destacado",
    )
    search_fields = ("nombre", "descripcion", "barrio", "parroquia", "tutor_nombre")
    inlines = [AnimalPhotoInline, MedicalRecordInline]


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ("animal", "fecha", "veterinario", "costo")
    list_filter = ("fecha",)
