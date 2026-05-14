from django import forms

from core.forms import BootstrapFormMixin

from .models import Report


class ReportForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            "tipo", "titulo", "descripcion", "ubicacion",
            "fecha_avistamiento", "nombre_reportante", "contacto_reportante",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "fecha_avistamiento": forms.DateInput(attrs={"type": "date"}),
        }
