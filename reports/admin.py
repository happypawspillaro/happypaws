from django.contrib import admin

from .models import Report, ReportPhoto


class ReportPhotoInline(admin.TabularInline):
    model = ReportPhoto
    extra = 1


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo", "ubicacion", "estado", "fecha_avistamiento", "creado")
    list_filter = ("tipo", "estado")
    search_fields = ("titulo", "descripcion", "ubicacion")
    inlines = [ReportPhotoInline]
