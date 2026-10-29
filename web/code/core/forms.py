from django import forms
from django.urls import reverse
from django.utils.html import format_html


class FechaInput(forms.DateInput):
    """Selector de fecha nativo del navegador (#90).

    `<input type="date">` solo entiende fechas ISO (AAAA-MM-DD). Con el idioma en
    español Django escribe 28/10/2026, el navegador deja el campo vacío y al
    editar se pierde la fecha guardada.
    """

    input_type = "date"

    def __init__(self, attrs=None):
        super().__init__(attrs, format="%Y-%m-%d")


class BootstrapFormMixin:
    """Aplica clases de Bootstrap a los widgets del formulario."""

    def __init__(self, *args, **kwargs):
        # Extraemos nuestros argumentos personalizados antes de llamar a super()
        canton_base = kwargs.pop("canton_base", None)
        parroquia_base = kwargs.pop("parroquia_base", None)
        super().__init__(*args, **kwargs)
        # Lo ideal es pasar por defecto el canton y parroquia del reporte,
        # acá inicializamos con los valores pasados del reporte
        if not self.data and not self.initial:
            if canton_base and "canton" in self.fields:
                self.initial["canton"] = canton_base
            if parroquia_base and "parroquia" in self.fields:
                self.initial["parroquia"] = parroquia_base
        # Inyecta código de HTMX para sugerir el nombre de un barrio
        # con respecto al cantón y parroquia seleccionada
        if "barrio" in self.fields:
            self.fields["barrio"].widget.attrs.update(
                {
                    "list": "sugerencias-barrios",
                    "autocomplete": "off",
                    "hx-get": reverse("core:barrios"),
                    "hx-trigger": "input changed delay:300ms",
                    "hx-target": "#sugerencias-barrios",
                    "hx-swap": "innerHTML",
                    "hx-include": "#id_canton,#id_parroquia",
                }
            )
            # En caso de cambio en los valores de cantón o parroquia,
            # reinicia el campo de barrio
            for field_name in ("canton", "parroquia"):
                self.fields[field_name].widget.attrs["hx-on:change"] = (
                    "document.getElementById('id_barrio').value = '';"
                    "document.getElementById('sugerencias-barrios').innerHTML = '';"
                )
        # De todas las opciones de parroquias, filtra por cantón
        if "canton" in self.fields:
            self.fields["canton"].widget.attrs.update(
                {
                    "hx-get": reverse("core:canton_parroquia"),
                    "hx-trigger": "change, load",
                    "hx-target": "#id_parroquia",
                    "hx-swap": "innerHTML",
                    "hx-include": "#id_parroquia",
                }
            )

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
