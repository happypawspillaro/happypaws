from django.contrib import admin

from .models import Report, ReportComment, ReportPhoto, ReportSighting


class ReportPhotoInline(admin.TabularInline):
    model = ReportPhoto
    extra = 1


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo", "ubicacion", "estado", "fecha_avistamiento", "creado")
    list_filter = ("tipo", "estado")
    search_fields = ("titulo", "descripcion", "ubicacion")
    inlines = [ReportPhotoInline]


@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    list_display = ("nombre", "reporte", "oculto", "creado")
    list_filter = ("oculto",)
    search_fields = ("nombre", "mensaje")
    list_editable = ("oculto",)


@admin.register(ReportSighting)
class ReportSightingAdmin(admin.ModelAdmin):
    list_display = ("nombre", "reporte", "ubicacion", "fecha", "confirmado", "oculto")
    list_filter = ("confirmado", "oculto")
    search_fields = ("nombre", "ubicacion", "descripcion")
    list_editable = ("confirmado", "oculto")
