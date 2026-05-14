from django.urls import path

from . import views

app_name = "adoptions"

urlpatterns = [
    path("solicitar/<int:animal_pk>/", views.apply, name="apply"),
    # Panel administrativo
    path("gestion/", views.manage_list, name="manage_list"),
    path("gestion/<int:pk>/", views.manage_detail, name="manage_detail"),
    path("gestion/<int:pk>/estado/", views.update_status, name="update_status"),
    path("gestion/<int:pk>/seguimiento/", views.add_followup, name="add_followup"),
]
