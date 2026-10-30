from core.forms import BootstrapFormMixin, ConsentimientoPrivacidadMixin, FechaInput
from django import forms

from .models import AdoptionApplication, AdoptionFollowUp


class AdoptionApplicationForm(ConsentimientoPrivacidadMixin, BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AdoptionApplication
        fields = [
            "nombre_solicitante",
            "cedula",
            "telefono",
            "email",
            "canton",
            "parroquia",
            "barrio",
            "tipo_vivienda",
            "tiene_patio",
            "experiencia",
            "proposito",
        ]
        widgets = {
            "experiencia": forms.Textarea(attrs={"rows": 3}),
        }


class StatusForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AdoptionApplication
        fields = ["estado", "notas_internas"]
        widgets = {"notas_internas": forms.Textarea(attrs={"rows": 3})}


class FollowUpForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AdoptionFollowUp
        fields = ["fecha", "notas", "foto"]
        widgets = {
            "fecha": FechaInput(),
            "notas": forms.Textarea(attrs={"rows": 3}),
        }
