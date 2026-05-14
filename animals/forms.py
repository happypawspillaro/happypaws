from django import forms

from core.forms import BootstrapFormMixin

from .models import Animal, AnimalPhoto, MedicalRecord


class AnimalForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Animal
        fields = [
            "nombre", "especie", "sexo", "tamano", "edad_aprox",
            "descripcion", "estado", "esterilizado", "fecha_ingreso",
            "foto_principal",
        ]
        widgets = {
            "fecha_ingreso": forms.DateInput(attrs={"type": "date"}),
            "descripcion": forms.Textarea(attrs={"rows": 4}),
        }


class AnimalPhotoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AnimalPhoto
        fields = ["imagen", "descripcion"]


class MedicalRecordForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ["fecha", "descripcion", "veterinario", "costo"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }
