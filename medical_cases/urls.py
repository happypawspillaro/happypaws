from django.urls import path

from . import views

app_name = "medical_cases"

urlpatterns = [
    path("", views.case_list, name="list"),
    path("<int:pk>/", views.detail, name="detail"),
    # Panel administrativo
    path("gestion/", views.manage_list, name="manage_list"),
    path("gestion/nuevo/", views.manage_create, name="manage_create"),
    path("gestion/<int:pk>/", views.manage_detail, name="manage_detail"),
    path("gestion/<int:pk>/editar/", views.manage_update, name="manage_update"),
    path("gestion/<int:pk>/donacion/", views.add_donation, name="add_donation"),
    path(
        "gestion/<int:pk>/donacion/<int:donation_pk>/verificar/",
        views.verify_donation,
        name="verify_donation",
    ),
    path("gestion/<int:pk>/avance/", views.add_update, name="add_update"),
    path("gestion/<int:pk>/estado/", views.toggle_status, name="toggle_status"),
]
