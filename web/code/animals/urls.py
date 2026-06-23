from django.urls import path

from . import views

app_name = "animals"

urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("<int:pk>/", views.detail, name="detail"),
    # Panel administrativo
    path("gestion/", views.manage_list, name="manage_list"),
    path("gestion/nuevo/", views.manage_create, name="manage_create"),
    path("gestion/<int:pk>/", views.manage_detail, name="manage_detail"),
    path("gestion/<int:pk>/editar/", views.manage_update, name="manage_update"),
    path("gestion/<int:pk>/eliminar/", views.manage_delete, name="manage_delete"),
    path("gestion/<int:pk>/foto/", views.add_photo, name="add_photo"),
    path("gestion/<int:pk>/medico/", views.add_medical_record, name="add_medical_record"),
]
