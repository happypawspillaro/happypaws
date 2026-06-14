# -*- coding: utf-8 -*-
"""Genera el documento de entrega 'Introducción y Tesis' (DOCX + PDF).

Replica el formato del documento base (Times New Roman, interlineado doble,
margenes de 1 pulgada, justificado con sangria de primera linea) y contiene
unicamente la Introduccion de la tesis y el planteamiento explicito de la Tesis,
conforme a la consigna del docente.
"""

import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --------------------------------------------------------------------------
# Contenido
# --------------------------------------------------------------------------
TITULO = (
    "Desarrollo e implementación de un sistema web para la gestión de adopción "
    "responsable, casos médicos con recaudación y reportes comunitarios de la "
    "fundación Happy Paws Píllaro, del cantón Santiago de Píllaro"
)
AUTOR = "Nicolas Bohórquez Escobar"
CARRERA = "Tecnología Superior en Desarrollo de Software"
NIVEL = "Cuarto Semestre — Proyecto de Grado"
TUTOR = "Ing. Irving López"
FECHA = "2 de junio de 2026"

INTRO = [
    "La sobrepoblación y el abandono de animales de compañía constituyen uno de los problemas de salud pública y bienestar social menos atendidos en América Latina. En el Ecuador, el Ministerio de Salud Pública estima una población canina superior a los dos millones quinientos mil individuos a escala nacional, de los cuales una proporción significativa carece de una tenencia responsable, lo que incrementa los riesgos zoonóticos y la presencia de fauna urbana sin control (Ministerio de Salud Pública del Ecuador [MSP], 2022). Frente a esta realidad, el Estado ecuatoriano ha construido un marco normativo que reconoce derechos a la naturaleza y responsabilidades sobre la fauna urbana, integrado por la Constitución de la República del Ecuador (Asamblea Constituyente del Ecuador, 2008), el Código Orgánico del Ambiente (Asamblea Nacional del Ecuador, 2017) y el Código Orgánico de Organización Territorial, Autonomía y Descentralización (Asamblea Nacional del Ecuador, 2010).",
    "En este escenario, las fundaciones de protección animal asumen una porción considerable del trabajo de rescate, atención veterinaria, esterilización y reubicación que el Estado y los gobiernos autónomos descentralizados no alcanzan a cubrir por completo (Protección Animal Ecuador [PAE], 2022). El cantón Santiago de Píllaro, ubicado en la provincia de Tungurahua, cuenta con la fundación Happy Paws Píllaro, una organización ciudadana sin fines de lucro que opera campañas de esterilización de bajo costo, rescata animales en situación de vulnerabilidad y promueve la adopción responsable dentro de su área de influencia. Para sostener las jornadas de esterilización, la fundación dispone de un sistema informático preexistente denominado Esterilizaya, cuyo alcance se limita al registro de animales atendidos durante dichas campañas.",
    "El resto de la operación de Happy Paws Píllaro, sin embargo, se gestiona principalmente a través de redes sociales y herramientas ofimáticas dispersas. Las publicaciones de animales en adopción se diluyen en líneas de tiempo sin posibilidad de búsqueda o filtrado, las solicitudes de adopción llegan como mensajes directos o comentarios que no garantizan trazabilidad, la recaudación destinada a tratamientos veterinarios carece de un mecanismo público de rendición de cuentas y los reportes ciudadanos de animales perdidos, encontrados o víctimas de maltrato no encuentran un canal estructurado. Esta dispersión informacional debilita la trazabilidad del ciclo de vida animal y limita la capacidad de la fundación para profesionalizar sus procesos.",
    "Frente a esta brecha funcional, el presente proyecto propone el desarrollo de un sistema web que centralice y automatice la gestión de adopción responsable, los casos médicos con recaudación transparente y los reportes comunitarios de la fundación, complementando al sistema Esterilizaya en lugar de reemplazarlo. La solución se construye sobre el framework Django (Django Software Foundation, 2024) en lenguaje Python (Python Software Foundation, 2024), con persistencia en PostgreSQL (PostgreSQL Global Development Group, 2024) y una interfaz construida con Bootstrap (Bootstrap Team, 2024). La integración con Esterilizaya permite que los animales esterilizados durante las jornadas sean publicados de forma automática en el catálogo de adopción, cerrando el ciclo institucional de esterilización, atención y adopción.",
    "La relevancia de esta investigación radica en que ofrece a una organización de la sociedad civil, con recursos humanos y económicos limitados, una herramienta tecnológica a la medida capaz de preservar el conocimiento institucional más allá de la rotación de voluntarios, profesionalizar su vínculo con la ciudadanía y habilitar la generación de indicadores sobre tiempos de respuesta, tasas de adopción y montos recaudados. De este modo, el proyecto traduce los principios constitucionales de protección a la naturaleza y las obligaciones legales sobre fauna urbana en una intervención concreta y verificable dentro del territorio del cantón Píllaro.",
]

TESIS = [
    "La centralización y automatización de los procesos de adopción responsable, gestión de casos médicos con recaudación transparente y reportes comunitarios en un único sistema web, desarrollado con tecnologías libres e integrado al sistema Esterilizaya, permitirá a la fundación Happy Paws Píllaro superar la dispersión informacional que hoy limita su operación, fortalecer la trazabilidad del ciclo de vida animal, profesionalizar su relación con la ciudadanía y consolidar la rendición de cuentas de sus campañas de recaudación.",
    "En consecuencia, este trabajo sostiene y se propone demostrar que una solución informática a la medida, construida sobre Django, PostgreSQL, Bootstrap y HTMX, constituye una herramienta determinante para que una organización de protección animal con recursos limitados transforme una gestión fragmentada en redes sociales y herramientas ofimáticas dispersas en un proceso institucional estructurado, sostenible y verificable.",
]


# --------------------------------------------------------------------------
# DOCX
# --------------------------------------------------------------------------
def build_docx(path):
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)

    def centered(text, size=12, bold=False, space_after=0):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(size)
        r.font.bold = bold
        p.paragraph_format.space_after = Pt(space_after)
        return p

    def body(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf = p.paragraph_format
        pf.line_spacing = 2.0
        pf.first_line_indent = Inches(0.5)
        pf.space_after = Pt(0)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        return p

    # Portada
    for _ in range(4):
        doc.add_paragraph()
    centered(TITULO, size=14, bold=True, space_after=24)
    for _ in range(2):
        doc.add_paragraph()
    centered(AUTOR, space_after=12)
    centered(CARRERA, space_after=12)
    centered(NIVEL, space_after=12)
    centered(TUTOR, space_after=12)
    centered(FECHA, space_after=12)

    doc.add_page_break()

    # Introducción
    centered("Introducción", size=14, bold=True, space_after=12)
    for par in INTRO:
        body(par)

    # Tesis
    centered("Tesis", size=14, bold=True, space_after=12)
    for par in TESIS:
        body(par)

    doc.save(path)
    print("DOCX ->", path)


# --------------------------------------------------------------------------
# PDF
# --------------------------------------------------------------------------
def build_pdf(path):
    from fpdf import FPDF

    def san(t):
        # El core font Times solo soporta latin-1; normaliza tipografia fina.
        return (t.replace("—", "-").replace("–", "-")
                 .replace("‘", "'").replace("’", "'")
                 .replace("“", '"').replace("”", '"'))

    pdf = FPDF(unit="in", format="Letter")
    pdf.set_margins(1, 1, 1)
    pdf.set_auto_page_break(auto=True, margin=1)
    line_h = 12 / 72 * 2  # 12 pt, interlineado doble

    # Portada
    pdf.add_page()
    pdf.ln(2.5)
    pdf.set_font("Times", "B", 14)
    pdf.multi_cell(0, 14 / 72 * 1.5, TITULO, align="C")
    pdf.ln(0.6)
    pdf.set_font("Times", "", 12)
    for t in (AUTOR, CARRERA, NIVEL, TUTOR, FECHA):
        pdf.multi_cell(0, line_h, san(t), align="C")
        pdf.ln(0.05)

    def pdf_body(par):
        # Sangria de primera linea emulada con espacios iniciales (~0.5").
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, line_h, "       " + san(par), align="J")

    # Introducción
    pdf.add_page()
    pdf.set_font("Times", "B", 14)
    pdf.multi_cell(0, line_h, san("Introducción"), align="C")
    pdf.ln(0.1)
    pdf.set_font("Times", "", 12)
    for par in INTRO:
        pdf_body(par)

    # Tesis
    pdf.ln(0.1)
    pdf.set_font("Times", "B", 14)
    pdf.multi_cell(0, line_h, san("Tesis"), align="C")
    pdf.ln(0.1)
    pdf.set_font("Times", "", 12)
    for par in TESIS:
        pdf_body(par)

    pdf.output(path)
    print("PDF  ->", path)


if __name__ == "__main__":
    base = "/home/elliot/Documents/happypaws/"
    build_docx(base + "Tesis Happy Paws - Introduccion.docx")
    build_pdf(base + "Tesis Happy Paws - Introduccion.pdf")
