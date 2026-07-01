from django import forms

from core.forms import BootstrapFormMixin

from .models import AdoptionApplication, AdoptionFollowUp


class AdoptionApplicationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AdoptionApplication
        fields = [
            "nombre_solicitante", "cedula", "telefono", "email", "direccion",
            "tipo_vivienda", "tiene_patio", "experiencia", "motivo",
        ]
        widgets = {
            "experiencia": forms.Textarea(attrs={"rows": 3}),
            "motivo": forms.Textarea(attrs={"rows": 3}),
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
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "notas": forms.Textarea(attrs={"rows": 3}),
        }
