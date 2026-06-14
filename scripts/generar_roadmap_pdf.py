#!/usr/bin/env python3
"""Genera ROADMAP.pdf a partir de ROADMAP.md.

Convierte el Markdown a HTML (tablas + bloques de codigo) y lo renderiza con
fpdf2 usando Arial para el cuerpo y Consolas para los diagramas ASCII, de modo
que los caracteres de caja (Box Drawing) y flechas se alineen correctamente.

Uso:
    ./venv/bin/python scripts/generar_roadmap_pdf.py
"""

import re
from pathlib import Path

import markdown
from fpdf import FPDF

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "ROADMAP.md"
SALIDA = RAIZ / "ROADMAP.pdf"

FUENTES = Path("/mnt/c/Windows/Fonts")
ARIAL = {
    "": FUENTES / "arial.ttf",
    "B": FUENTES / "arialbd.ttf",
    "I": FUENTES / "ariali.ttf",
    "BI": FUENTES / "arialbi.ttf",
}
CONSOLAS = {
    "": FUENTES / "consola.ttf",
    "B": FUENTES / "consolab.ttf",
    "I": FUENTES / "consolai.ttf",
}


def limpiar(texto: str) -> str:
    """Quita emojis (que las fuentes no tienen) y normaliza simbolos.

    Las fuentes Arial/Consolas no incluyen pictogramas a color, asi que se
    eliminan los caracteres >= U+1F000 y el selector de variacion U+FE0F.
    Algunos simbolos (✅ ✓ ▶) no estan en Arial/Consolas, asi que se
    reemplazan por equivalentes presentes para evitar recuadros vacios.
    """
    texto = (texto.replace("✅", "OK").replace("✓", "OK").replace("▶", ">"))
    return "".join(ch for ch in texto if ord(ch) < 0x1F000 and ch != "️")


class PDF(FPDF):
    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Arial", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, f"Happy Paws Pillaro  ·  Hoja de ruta  ·  Pag. {self.page_no()}",
                  align="C")


def main() -> None:
    md = limpiar(ENTRADA.read_text(encoding="utf-8"))
    html = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])
    # fpdf2 no soporta <code> anidado en celdas; el monoespaciado de los
    # diagramas lo da <pre>, asi que removemos solo el envoltorio <code>.
    html = re.sub(r"</?code[^>]*>", "", html)

    pdf = PDF(format="A4")
    pdf.set_margins(18, 16, 18)
    pdf.set_auto_page_break(auto=True, margin=16)

    for estilo, ruta in ARIAL.items():
        pdf.add_font("Arial", estilo, str(ruta))
    for estilo, ruta in CONSOLAS.items():
        pdf.add_font("Consolas", estilo, str(ruta))
    # Si Arial no tiene un glifo (✓, flechas), lo toma de Consolas.
    pdf.set_fallback_fonts(["Consolas"])

    pdf.add_page()
    pdf.write_html(
        html,
        font_family="Arial",
        pre_code_font="Consolas",
        table_line_separators=True,
    )

    pdf.output(str(SALIDA))
    print(f"PDF generado: {SALIDA}")


if __name__ == "__main__":
    main()
