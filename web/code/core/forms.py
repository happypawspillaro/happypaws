from django import forms
from django.urls import reverse
from django.utils.html import format_html


class BootstrapFormMixin:
    """Aplica clases de Bootstrap a los widgets del formulario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class ConsentimientoPrivacidadMixin:
    """Casilla obligatoria para aceptar la política de privacidad (#75).

    La LOPDP pide el consentimiento de quien nos entrega sus datos, así que va
    en todos los formularios públicos que guardan nombre, contacto o dirección.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["acepta_privacidad"] = forms.BooleanField(
            label="Acepto la política de privacidad",
            help_text=format_html(
                'Lee cómo cuidamos tus datos en la <a href="{}" target="_blank">política de privacidad</a>.',
                reverse("core:privacidad"),
            ),
            error_messages={"required": "Debes aceptar la política de privacidad para enviar tus datos."},
            widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        )
