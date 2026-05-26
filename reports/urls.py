from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.report_list, name="list"),
    path("nuevo/", views.create, name="create"),
    path("<int:pk>/", views.detail, name="detail"),
    # Interacción pública
    path("<int:pk>/comentar/", views.add_comment, name="add_comment"),
    path("<int:pk>/avistamiento/", views.add_sighting, name="add_sighting"),
    # Panel administrativo
    path("gestion/", views.manage_list, name="manage_list"),
    path("gestion/<int:pk>/estado/", views.toggle_status, name="toggle_status"),
    # Moderación de la interacción
    path("comentario/<int:pk>/ocultar/", views.toggle_comment, name="toggle_comment"),
    path("comentario/<int:pk>/eliminar/", views.delete_comment, name="delete_comment"),
    path("avistamiento/<int:pk>/ocultar/", views.toggle_sighting, name="toggle_sighting"),
    path("avistamiento/<int:pk>/confirmar/", views.confirm_sighting, name="confirm_sighting"),
    path("avistamiento/<int:pk>/eliminar/", views.delete_sighting, name="delete_sighting"),
]
