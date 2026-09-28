from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("panel/", views.dashboard, name="dashboard"),
    path("quienes_somos", views.quienes_somos, name="quienes_somos"),
    path("organizacion", views.organizacion, name="organizacion"),
]
