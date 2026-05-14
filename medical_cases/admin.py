from django.contrib import admin

from .models import CaseUpdate, Donation, MedicalCase


class DonationInline(admin.TabularInline):
    model = Donation
    extra = 0


class CaseUpdateInline(admin.TabularInline):
    model = CaseUpdate
    extra = 0


@admin.register(MedicalCase)
class MedicalCaseAdmin(admin.ModelAdmin):
    list_display = ("titulo", "animal", "meta_monto", "monto_recaudado", "estado")
    list_filter = ("estado",)
    search_fields = ("titulo", "descripcion")
    inlines = [DonationInline, CaseUpdateInline]


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("nombre_donante", "caso", "monto", "fecha", "verificado")
    list_filter = ("verificado", "fecha")
    search_fields = ("nombre_donante", "email")
