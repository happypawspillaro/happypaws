from django.contrib import admin

from .models import CasePhoto, CaseUpdate, Donation, Expense, MedicalCase


class DonationInline(admin.TabularInline):
    model = Donation
    extra = 0


class CaseUpdateInline(admin.TabularInline):
    model = CaseUpdate
    extra = 0


class CasePhotoInline(admin.TabularInline):
    model = CasePhoto
    extra = 0


class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 0


@admin.register(MedicalCase)
class MedicalCaseAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "animal",
        "meta_monto",
        "monto_recaudado",
        "total_egresos",
        "estado",
    )
    list_filter = ("estado",)
    search_fields = ("titulo", "descripcion")
    inlines = [CasePhotoInline, DonationInline, ExpenseInline, CaseUpdateInline]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("descripcion", "caso", "categoria", "monto", "fecha")
    list_filter = ("categoria", "fecha")
    search_fields = ("descripcion", "caso__titulo")


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("nombre_donante", "caso", "monto", "fecha", "verificado")
    list_filter = ("verificado", "fecha")
    search_fields = ("nombre_donante", "email")
