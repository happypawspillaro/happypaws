import re

from django import forms
from django.core.validators import EmailValidator

from core.forms import BootstrapFormMixin

from .models import Report, ReportComment, ReportSighting

# Teléfono: opcional "+", dígitos y separadores comunes. Validamos aparte que
# tenga al menos 7 dígitos para descartar entradas demasiado cortas.
_PHONE_RE = re.compile(r"^\+?[\d\s\-()]{7,20}$")


def validar_contacto(valor):
    """Acepta un correo válido o un número de teléfono; si no, lanza error."""
    valor = (valor or "").strip()
    if not valor:
        return valor
    try:
        EmailValidator()(valor)
        return valor
    except forms.ValidationError:
        pass
    if _PHONE_RE.match(valor) and sum(c.isdigit() for c in valor) >= 7:
        return valor
    raise forms.ValidationError(
        "Ingresa un correo válido o un número de teléfono (mínimo 7 dígitos)."
    )


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
            "tipo", "titulo", "descripcion",
            "especie", "sexo", "callejero", "senales_distinguibles",
            "ubicacion", "fecha_avistamiento", "hora_aproximada",
            "nombre_reportante", "contacto_reportante",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "senales_distinguibles": forms.Textarea(attrs={"rows": 2}),
            "fecha_avistamiento": forms.DateInput(attrs={"type": "date"}),
            "hora_aproximada": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean_ubicacion(self):
        ubicacion = (self.cleaned_data.get("ubicacion") or "").strip()
        if len(ubicacion) < 3:
            raise forms.ValidationError(
                "Indica una ubicación o sector válido (mínimo 3 caracteres)."
            )
        return ubicacion

    def clean_contacto_reportante(self):
        # El contacto es opcional (reporte anónimo); si se provee, lo validamos.
        return validar_contacto(self.cleaned_data.get("contacto_reportante"))


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
