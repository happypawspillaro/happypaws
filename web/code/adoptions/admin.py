from django.contrib import admin

from .models import AdoptionApplication, AdoptionFollowUp


class FollowUpInline(admin.TabularInline):
    model = AdoptionFollowUp
    extra = 0


@admin.register(AdoptionApplication)
class AdoptionApplicationAdmin(admin.ModelAdmin):
    list_display = ("nombre_solicitante", "animal", "estado", "creado")
    list_filter = ("estado", "tipo_vivienda")
    search_fields = ("nombre_solicitante", "cedula", "email")
    inlines = [FollowUpInline]
