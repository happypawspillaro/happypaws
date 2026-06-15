from django import forms

from core.forms import BootstrapFormMixin

from .models import CasePhoto, CaseUpdate, Donation, Expense, MedicalCase


class MedicalCaseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = MedicalCase
        fields = ["animal", "titulo", "descripcion", "meta_monto", "estado", "foto"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 4})}


class PublicDonationForm(BootstrapFormMixin, forms.ModelForm):
    """Formulario público: la donación queda pendiente de verificación."""

    class Meta:
        model = Donation
        fields = ["nombre_donante", "email", "monto", "fecha", "comprobante"]
        widgets = {"fecha": forms.DateInput(attrs={"type": "date"})}
        help_texts = {
            "nombre_donante": "Opcional. Si lo dejas en blanco aparecerás como anónimo.",
        }


class StaffDonationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Donation
        fields = ["nombre_donante", "email", "monto", "fecha", "comprobante", "verificado"]
        widgets = {"fecha": forms.DateInput(attrs={"type": "date"})}


class CaseUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CaseUpdate
        fields = ["fecha", "texto", "foto"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "texto": forms.Textarea(attrs={"rows": 3}),
        }


class CasePhotoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CasePhoto
        fields = ["imagen", "descripcion"]


class ExpenseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["categoria", "descripcion", "monto", "fecha", "comprobante"]
        widgets = {"fecha": forms.DateInput(attrs={"type": "date"})}
