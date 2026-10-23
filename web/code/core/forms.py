from django import forms
from django.urls import reverse


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
