from django import forms

# Clases base compartidas por todos los widgets. Se definen aquí (y no en las
# plantillas) porque Django renderiza el campo con {{ field }} y no hay dónde
# inyectarlas desde el HTML.
INPUT_CLASSES = (
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm "
    "text-slate-700 transition placeholder:text-slate-400 "
    "focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30"
)

FILE_CLASSES = (
    "w-full rounded-lg border border-slate-300 bg-white text-sm text-slate-700 "
    "transition file:mr-3 file:rounded-l-lg file:border-0 file:bg-slate-100 "
    "file:px-3 file:py-2 file:text-sm file:font-medium file:text-slate-700 "
    "hover:file:bg-slate-200 focus:border-primary focus:outline-none "
    "focus:ring-2 focus:ring-primary/30"
)

CHECKBOX_CLASSES = (
    "h-4 w-4 rounded border-slate-300 text-primary "
    "focus:ring-2 focus:ring-primary/30"
)


class TailwindFormMixin:
    """Aplica las clases de Tailwind a los widgets del formulario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                widget.attrs.setdefault("class", CHECKBOX_CLASSES)
            elif isinstance(widget, forms.FileInput):
                widget.attrs.setdefault("class", FILE_CLASSES)
            else:
                widget.attrs.setdefault("class", INPUT_CLASSES)
