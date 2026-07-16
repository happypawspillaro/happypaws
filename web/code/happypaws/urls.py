from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cuentas/", include("accounts.urls")),
    path("animales/", include("animals.urls")),
    path("adopciones/", include("adoptions.urls")),
    path("casos/", include("medical_cases.urls")),
    path("reportes/", include("reports.urls")),
    path("", include("core.urls")),
    path("health/", lambda request: HttpResponse("OK")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
