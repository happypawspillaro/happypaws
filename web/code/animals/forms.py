from core.forms import BootstrapFormMixin, FechaInput
from django import forms

from .models import Animal, AnimalPhoto, MedicalRecord


class AnimalForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Animal
        fields = [
            "nombre",
            "especie",
            "sexo",
            "tamano",
            "edad_aprox",
            "descripcion",
            "estado",
            "origen",
            "canton",
            "parroquia",
            "barrio",
            "tutor_nombre",
            "tutor_contacto",
            "esterilizado",
            "fecha_esterilizacion",
            "destacado",
            "fecha_ingreso",
            "foto_principal",
        ]
        widgets = {
            "fecha_ingreso": FechaInput(),
            "fecha_esterilizacion": FechaInput(),
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
            "fecha": FechaInput(),
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }
