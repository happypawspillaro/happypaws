from django import forms
from django.contrib.auth.forms import UserCreationForm

from core.forms import TailwindFormMixin

from .models import User


class SignUpForm(TailwindFormMixin, UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellido", max_length=150)
    email = forms.EmailField(label="Correo")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "telefono"]
