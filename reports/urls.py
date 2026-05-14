from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.report_list, name="list"),
    path("nuevo/", views.create, name="create"),
    path("<int:pk>/", views.detail, name="detail"),
    # Panel administrativo
    path("gestion/", views.manage_list, name="manage_list"),
    path("gestion/<int:pk>/estado/", views.toggle_status, name="toggle_status"),
]
