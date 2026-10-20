from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("panel/", views.dashboard, name="dashboard"),
    path("privacidad/", views.privacidad, name="privacidad"),
]
