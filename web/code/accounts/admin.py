from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

UserAdmin.fieldsets = UserAdmin.fieldsets + (
    ("Datos de contacto", {"fields": ("telefono",)}),
)
admin.site.register(User, UserAdmin)
