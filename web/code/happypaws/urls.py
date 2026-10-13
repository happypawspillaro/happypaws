from core.sitemaps import (
    AnimalSitemap,
    MedicalCaseSitemap,
    ReportSitemap,
    StaticViewSitemap,
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import TemplateView

sitemaps = {
    "estaticas": StaticViewSitemap,
    "animales": AnimalSitemap,
    "casos": MedicalCaseSitemap,
    "reportes": ReportSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cuentas/", include("accounts.urls")),
    path("animales/", include("animals.urls")),
    path("adopciones/", include("adoptions.urls")),
    path("casos/", include("medical_cases.urls")),
    path("reportes/", include("reports.urls")),
    path("", include("core.urls")),
    path("health/", lambda request: HttpResponse("OK")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    # Se sirve desde Django y no desde /static/ porque los buscadores lo piden en la raíz (#65).
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
