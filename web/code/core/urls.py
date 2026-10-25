from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("panel/", views.dashboard, name="dashboard"),
    path("privacidad/", views.privacidad, name="privacidad"),
    # Sobre la fundación
    path("fundacion/quienes-somos", views.QuienesSomosView.as_view(), name="quienes_somos"),
    path("fundacion/directiva", views.DirectivaView.as_view(), name="directiva"),
    path("fundacion/reconocimientos", views.ReconocimientosView.as_view(), name="reconocimientos"),
    path("fundacion/impacto", views.ImpactoView.as_view(), name="impacto"),
    # Proyectos e impacto
    path("proyectos/fauna-urbana/", views.FaunaUrbanaView.as_view(), name="fauna_urbana"),
    path("proyectos/areas-trabajo/", views.AreasTrabajoView.as_view(), name="areas_trabajo"),
    path("proyectos/software-libre/", views.SoftwareLibreView.as_view(), name="software_libre"),
    path("proyectos/media/", views.MediosComunicacionView.as_view(), name="media"),
    # Transparencia y Recursos
    path("recursos/marco-legal/", views.MarcoLegalView.as_view(), name="marco_legal"),
    path("recursos/formatos/", views.FormatosView.as_view(), name="formatos"),
    path("recursos/contacto/", views.ContactosView.as_view(), name="contacto"),
    # Contribuir
    path("contribuir/", views.ContribuyeView.as_view(), name="contribuir_home"),
    path("contribuir/voluntariado/", views.VoluntariadoView.as_view(), name="voluntariado"),
]
