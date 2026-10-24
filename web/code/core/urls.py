from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("panel/", views.dashboard, name="dashboard"),
    path("privacidad/", views.privacidad, name="privacidad"),
    path("obtener_barrios/", views.obtener_barrios, name="barrios"),
    path("listar_canton_parroquia/", views.listar_canton_parroquia, name="canton_parroquia"),
]
