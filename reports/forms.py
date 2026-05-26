from django import forms

from core.forms import BootstrapFormMixin

from .models import Report, ReportComment, ReportSighting


class HoneypotMixin:
    """Agrega un campo trampa invisible. Los bots lo rellenan; las personas no.

    El campo se oculta por CSS (clase ``hp-field`` en el wrapper) en lugar de
    ``HiddenInput`` para atrapar más bots. Si llega con contenido, rechazamos.
    """

    honeypot_name = "website"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.honeypot_name] = forms.CharField(
            required=False,
            label="No llenar este campo",
            widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
        )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get(self.honeypot_name):
            raise forms.ValidationError("No pudimos procesar el envío.")
        return cleaned


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


class CommentForm(HoneypotMixin, BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ReportComment
        fields = ["nombre", "contacto", "mensaje"]
        widgets = {
            "mensaje": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Deja una pista, pregunta o ánimo…"}
            ),
        }


class SightingForm(HoneypotMixin, BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ReportSighting
        fields = ["nombre", "contacto", "ubicacion", "fecha", "descripcion", "foto"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "descripcion": forms.Textarea(
                attrs={"rows": 2, "placeholder": "¿Cómo estaba? ¿Hacia dónde fue?"}
            ),
        }
