"""
Genera el documento de tesis (Introduccion + Marco Teorico inicial) en APA 7ma.

Salida: 'Tesis Happy Paws - Introduccion y Marco Teorico.docx' en la raiz del repo.
"""
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Tesis Happy Paws - Introduccion y Marco Teorico.docx"

FONT = "Times New Roman"
FONT_SIZE = Pt(12)


# ---------------------------------------------------------------------------
# Helpers de formato
# ---------------------------------------------------------------------------

def set_base_style(doc):
    style = doc.styles["Normal"]
    style.font.name = FONT
    style.font.size = FONT_SIZE
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), FONT)
    rfonts.set(qn("w:hAnsi"), FONT)
    rfonts.set(qn("w:cs"), FONT)
    pf = style.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)


def set_margins(doc):
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)


def add_page_number(doc):
    section = doc.sections[0]
    header = section.header
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)
    run.font.name = FONT
    run.font.size = FONT_SIZE


def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = True
    run.font.name = FONT
    run.font.size = Pt(14)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    return p


def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.bold = True
    run.font.name = FONT
    run.font.size = Pt(12)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    return p


def add_body(doc, text, indent_first_line=True, italic=False):
    """Anade un parrafo de cuerpo con sangria de primera linea (APA)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    run.font.name = FONT
    run.font.size = FONT_SIZE
    if italic:
        run.italic = True
    if indent_first_line:
        p.paragraph_format.first_line_indent = Cm(1.27)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    return p


def add_blank_line(doc):
    doc.add_paragraph()


def add_reference(doc, text):
    """Parrafo con sangria francesa (hanging indent) para la lista de referencias."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.name = FONT
    run.font.size = FONT_SIZE
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.first_line_indent = Cm(-1.27)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    p.paragraph_format.space_after = Pt(0)
    return p


# ---------------------------------------------------------------------------
# Contenido
# ---------------------------------------------------------------------------

def build_portada(doc):
    """Portada APA 7ma, formato estudiante."""
    for _ in range(6):
        add_blank_line(doc)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(
        "Desarrollo e implementación de un sistema web para la gestión "
        "de adopción responsable, casos médicos con recaudación y "
        "reportes comunitarios de la fundación Happy Paws Píllaro, "
        "del cantón Santiago de Píllaro"
    )
    run.bold = True
    run.font.name = FONT
    run.font.size = Pt(14)

    add_blank_line(doc)
    add_blank_line(doc)

    centered = [
        "Nicolas Bohórquez Escobar",
        "",
        "Tecnología Superior en Desarrollo de Software",
        "",
        "Proyecto de Grado",
        "",
        "[Nombre del docente tutor]",
        "",
        "26 de mayo de 2026",
    ]
    for line in centered:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(line)
        run.font.name = FONT
        run.font.size = FONT_SIZE

    doc.add_page_break()


def build_introduccion(doc):
    add_heading_1(doc, "Introducción")
    add_blank_line(doc)

    parrafos = [
        (
            "La sobrepoblación y el abandono de animales de compañía constituyen "
            "uno de los problemas de salud pública y bienestar social menos atendidos "
            "en América Latina. En el Ecuador, el Ministerio de Salud Pública estima "
            "una población canina superior a los dos millones quinientos mil individuos "
            "a escala nacional, de los cuales una proporción significativa carece de "
            "una tenencia responsable, lo que incrementa los riesgos zoonóticos y la "
            "presencia de fauna urbana sin control (Ministerio de Salud Pública del "
            "Ecuador [MSP], 2022). Frente a esta realidad, el Estado ecuatoriano ha "
            "construido un marco normativo que reconoce derechos a la naturaleza y "
            "responsabilidades sobre la fauna urbana, integrado por la Constitución "
            "de la República del Ecuador (Asamblea Constituyente del Ecuador, 2008), "
            "el Código Orgánico del Ambiente (Asamblea Nacional del Ecuador, 2017) y "
            "el Código Orgánico de Organización Territorial, Autonomía y "
            "Descentralización (Asamblea Nacional del Ecuador, 2010)."
        ),
        (
            "En este escenario, las fundaciones de protección animal asumen una "
            "porción considerable del trabajo de rescate, atención veterinaria, "
            "esterilización y reubicación que el Estado y los gobiernos autónomos "
            "descentralizados no alcanzan a cubrir por completo (Protección Animal "
            "Ecuador [PAE], 2022). El cantón Santiago de Píllaro, ubicado en la "
            "provincia de Tungurahua, cuenta con la fundación Happy Paws Píllaro, "
            "una organización ciudadana sin fines de lucro que opera campañas de "
            "esterilización de bajo costo, rescata animales en situación de "
            "vulnerabilidad y promueve la adopción responsable dentro de su área "
            "de influencia. Para sostener las jornadas de esterilización, la "
            "fundación dispone de un sistema informático preexistente denominado "
            "Esterilizaya, cuyo alcance se limita al registro de animales atendidos "
            "durante dichas campañas."
        ),
        (
            "El resto de la operación de Happy Paws Píllaro, sin embargo, se gestiona "
            "principalmente a través de redes sociales y herramientas ofimáticas "
            "dispersas. Las publicaciones de animales en adopción se diluyen en "
            "líneas de tiempo sin posibilidad de búsqueda o filtrado, las solicitudes "
            "de adopción llegan como mensajes directos o comentarios que no "
            "garantizan trazabilidad, la recaudación destinada a tratamientos "
            "veterinarios carece de un mecanismo público de rendición de cuentas y "
            "los reportes ciudadanos de animales perdidos, encontrados o víctimas "
            "de maltrato no encuentran un canal estructurado. Esta dispersión "
            "informacional debilita la trazabilidad del ciclo de vida animal y "
            "limita la capacidad de la fundación para profesionalizar sus procesos."
        ),
        (
            "Frente a esta brecha funcional, el presente proyecto propone el "
            "desarrollo de un sistema web que centralice y automatice la gestión "
            "de adopción responsable, los casos médicos con recaudación transparente "
            "y los reportes comunitarios de la fundación, complementando al sistema "
            "Esterilizaya en lugar de reemplazarlo. La solución se construye sobre "
            "el framework Django (Django Software Foundation, 2024) en lenguaje "
            "Python (Python Software Foundation, 2024), con persistencia en "
            "PostgreSQL (PostgreSQL Global Development Group, 2024) y una interfaz "
            "construida con Bootstrap (Bootstrap Team, 2024). La integración con "
            "Esterilizaya permite que los animales esterilizados durante las "
            "jornadas sean publicados de forma automática en el catálogo de "
            "adopción, cerrando el ciclo institucional de esterilización, atención "
            "y adopción."
        ),
        (
            "El presente documento se organiza de la siguiente manera. La "
            "Introducción contextualiza el problema y delimita el alcance del "
            "proyecto. El Capítulo I, denominado Marco Teórico, fundamenta la "
            "investigación a partir de cinco ejes conceptuales: el bienestar "
            "animal y el marco normativo ecuatoriano; los sistemas de información "
            "aplicados a organizaciones de protección animal; la ingeniería de "
            "software y el desarrollo web; las bases de datos relacionales y la "
            "persistencia; y el diseño responsivo apoyado en bibliotecas de "
            "presentación. Cada eje articula los referentes teóricos que sustentan "
            "las decisiones tecnológicas y funcionales que se concretarán en los "
            "capítulos posteriores. Finalmente, la sección de Referencias reúne "
            "las fuentes consultadas conforme a las normas de la American "
            "Psychological Association en su séptima edición."
        ),
    ]
    for parrafo in parrafos:
        add_body(doc, parrafo)

    doc.add_page_break()


def build_marco_teorico(doc):
    add_heading_1(doc, "Capítulo I")
    add_heading_1(doc, "Marco Teórico")
    add_blank_line(doc)

    add_body(
        doc,
        (
            "El presente capítulo describe los fundamentos teóricos, normativos y "
            "tecnológicos sobre los que se sostiene el sistema web propuesto para "
            "la fundación Happy Paws Píllaro. Los referentes se organizan desde lo "
            "más general, como el bienestar animal y la legislación nacional, "
            "hacia lo más específico, como las decisiones de arquitectura, "
            "persistencia y presentación que configuran la solución informática."
        ),
    )
    add_blank_line(doc)

    # 1.1
    add_heading_2(doc, "1.1. Bienestar animal y marco normativo ecuatoriano")
    add_blank_line(doc)
    for parrafo in [
        (
            "El bienestar animal se entiende, en términos contemporáneos, como el "
            "estado físico y mental de un animal en relación con las condiciones en "
            "que vive y muere. La Organización Mundial de Sanidad Animal ha "
            "consolidado el principio de las cinco libertades, que incluye estar "
            "libre de hambre y sed, de incomodidad, de dolor y enfermedad, de miedo "
            "y angustia, y la libertad de expresar un comportamiento natural. Este "
            "principio se ha convertido en una referencia transversal para diseñar "
            "políticas públicas y proyectos de cooperación enfocados en la fauna "
            "doméstica y urbana (Ministerio del Ambiente, Agua y Transición "
            "Ecológica [MAATE], 2023)."
        ),
        (
            "En el Ecuador, la Constitución de la República consagra los derechos "
            "de la naturaleza y mandata su protección integral, incluido el "
            "respeto al ciclo vital de las especies que la componen (Asamblea "
            "Constituyente del Ecuador, 2008, arts. 71 a 74). A partir de este "
            "marco constitucional, el Código Orgánico del Ambiente desarrolla "
            "competencias específicas sobre fauna urbana, control poblacional, "
            "tenencia responsable y bienestar animal, distribuyendo "
            "responsabilidades entre la autoridad ambiental nacional y los "
            "gobiernos autónomos descentralizados (Asamblea Nacional del Ecuador, "
            "2017, arts. 139 a 145). Complementariamente, el Código Orgánico de "
            "Organización Territorial, Autonomía y Descentralización asigna a los "
            "municipios la facultad de regular y controlar la presencia de fauna "
            "urbana en su jurisdicción (Asamblea Nacional del Ecuador, 2010)."
        ),
        (
            "Desde la política sanitaria, el Ministerio de Salud Pública del "
            "Ecuador implementa el Programa Nacional de Tenencia Responsable y "
            "Control de la Población Canina y Felina, orientado a reducir riesgos "
            "zoonóticos como la rabia y a promover prácticas responsables de "
            "tenencia (MSP, 2022). Sobre el terreno, la gestión cotidiana de "
            "rescate, atención veterinaria y reubicación se sostiene en gran "
            "medida gracias al trabajo de organizaciones de la sociedad civil, "
            "como la Protección Animal Ecuador, que documenta de manera anual la "
            "magnitud del problema y la limitada cobertura institucional (PAE, "
            "2022). En este ecosistema operan fundaciones locales como Happy Paws "
            "Píllaro, cuya labor materializa principios constitucionales y "
            "obligaciones legales en intervenciones concretas dentro de su "
            "territorio."
        ),
    ]:
        add_body(doc, parrafo)
    add_blank_line(doc)

    # 1.2
    add_heading_2(
        doc,
        "1.2. Sistemas de información aplicados a organizaciones de protección animal",
    )
    add_blank_line(doc)
    for parrafo in [
        (
            "Un sistema de información puede definirse como un conjunto "
            "interrelacionado de componentes que recolectan, procesan, almacenan y "
            "distribuyen información para apoyar la toma de decisiones, la "
            "coordinación y el control en una organización (Laudon y Laudon, "
            "2020). Más allá del componente tecnológico, los sistemas de "
            "información integran personas, procesos y datos en un mismo flujo "
            "operativo, lo que les permite producir valor cuando se alinean con "
            "los objetivos estratégicos de la institución que los utiliza."
        ),
        (
            "En el caso de las organizaciones de protección animal, la adopción "
            "de tecnologías de la información ha demostrado mejorar la "
            "trazabilidad de los animales rescatados, la transparencia financiera "
            "de las campañas de recaudación y la capacidad de respuesta frente a "
            "denuncias y reportes ciudadanos (Albarracín y Vásquez, 2021). La "
            "centralización de la información en una única plataforma evita la "
            "fragmentación que se produce cuando los datos se distribuyen entre "
            "hojas de cálculo, mensajes privados y publicaciones efímeras en "
            "redes sociales."
        ),
        (
            "Para una fundación con recursos limitados, como Happy Paws Píllaro, "
            "un sistema de información a la medida ofrece beneficios concretos. "
            "En primer lugar, permite preservar el conocimiento institucional "
            "más allá de la rotación de voluntarios, dado que los registros "
            "persisten en una base de datos y no en la memoria de personas "
            "puntuales. En segundo lugar, profesionaliza la relación con la "
            "ciudadanía, al ofrecer un punto único y verificable para registrar "
            "solicitudes de adopción, donaciones y reportes. En tercer lugar, "
            "habilita el análisis posterior de la operación, ya que la "
            "información estructurada permite generar indicadores sobre tiempos "
            "de respuesta, tasas de adopción y montos recaudados por caso "
            "(Laudon y Laudon, 2020)."
        ),
    ]:
        add_body(doc, parrafo)
    add_blank_line(doc)

    # 1.3
    add_heading_2(doc, "1.3. Ingeniería de software y desarrollo web")
    add_blank_line(doc)
    for parrafo in [
        (
            "La ingeniería de software se ocupa de la aplicación sistemática, "
            "disciplinada y cuantificable de principios de ingeniería al "
            "desarrollo, operación y mantenimiento del software (Sommerville, "
            "2011). Sus modelos de ciclo de vida, entre los que se cuentan el "
            "modelo en cascada, los enfoques iterativos e incrementales y las "
            "metodologías ágiles, ofrecen estructuras de trabajo que orientan la "
            "construcción de productos de calidad. Para un proyecto de alcance "
            "acotado, dirigido a una organización sin departamento de "
            "tecnologías de la información, un enfoque iterativo resulta "
            "particularmente conveniente, porque permite entregar valor de forma "
            "progresiva y ajustar requerimientos en función de la "
            "retroalimentación de los usuarios (Pressman y Maxim, 2014)."
        ),
        (
            "El desarrollo web se inscribe dentro de la ingeniería de software "
            "como una rama orientada a la construcción de aplicaciones que se "
            "ejecutan sobre la arquitectura cliente servidor. En este modelo, el "
            "navegador del usuario realiza solicitudes mediante el protocolo "
            "HTTP y un servidor produce respuestas dinámicas en función de la "
            "lógica de negocio y de la información almacenada. Pressman y Maxim "
            "(2014) destacan que las aplicaciones web exigen disciplinas "
            "adicionales como la usabilidad, la seguridad, el rendimiento y la "
            "interoperabilidad, dado que se exponen a un universo amplio y "
            "heterogéneo de usuarios y dispositivos."
        ),
        (
            "Para satisfacer estas exigencias, el ecosistema Python ofrece "
            "Django, un framework de alto nivel que fomenta el desarrollo rápido "
            "y un diseño limpio y pragmático (Django Software Foundation, 2024; "
            "Python Software Foundation, 2024). Django adopta el patrón "
            "arquitectónico Model View Template, que separa la representación de "
            "los datos, la lógica de control y la presentación. Aunque suele "
            "compararse con el clásico Model View Controller, en Django el "
            "componente que en otros frameworks se denomina controlador es "
            "asumido por el propio framework a través del enrutador de "
            "solicitudes, de modo que el desarrollador se concentra en los "
            "modelos, las vistas y las plantillas. Esta separación favorece la "
            "mantenibilidad y la reutilización del código, dos atributos de "
            "calidad ampliamente reconocidos en la literatura de ingeniería de "
            "software (Sommerville, 2011)."
        ),
        (
            "Adicionalmente, Django incluye de forma nativa un sistema de "
            "administración, un mapeador objeto relacional, un sistema de "
            "autenticación y mecanismos de protección frente a vulnerabilidades "
            "comunes como inyección SQL, cross site scripting y falsificación de "
            "solicitudes entre sitios (Django Software Foundation, 2024). Estas "
            "características permiten que un equipo reducido construya en menos "
            "tiempo aplicaciones robustas, sin reinventar componentes que ya "
            "están resueltos por el framework."
        ),
    ]:
        add_body(doc, parrafo)
    add_blank_line(doc)

    # 1.4
    add_heading_2(doc, "1.4. Bases de datos relacionales y persistencia")
    add_blank_line(doc)
    for parrafo in [
        (
            "La persistencia de la información en aplicaciones web descansa, en "
            "su gran mayoría, sobre sistemas de bases de datos relacionales. El "
            "modelo relacional, formulado originalmente por Edgar F. Codd, "
            "representa los datos como un conjunto de relaciones organizadas en "
            "tablas, con tuplas y atributos sujetos a reglas de integridad (Date, "
            "2003). Esta abstracción ha demostrado ser suficientemente flexible "
            "para representar fenómenos diversos y, al mismo tiempo, lo "
            "suficientemente rigurosa para garantizar consistencia mediante "
            "transacciones que cumplen las propiedades de atomicidad, "
            "consistencia, aislamiento y durabilidad (Silberschatz et al., 2020)."
        ),
        (
            "Entre las implementaciones libres y de código abierto del modelo "
            "relacional, PostgreSQL se destaca por su madurez, su cumplimiento "
            "estricto del estándar SQL y su amplio conjunto de características "
            "avanzadas, como tipos de datos extensibles, indexación múltiple, "
            "vistas materializadas y restricciones declarativas (PostgreSQL "
            "Global Development Group, 2024). Para un proyecto académico que "
            "aspira a ser desplegado en producción y a sostener crecimiento "
            "futuro, PostgreSQL ofrece una alternativa profesional sin costos "
            "de licenciamiento, lo que se alinea con la realidad presupuestaria "
            "de una fundación pequeña."
        ),
        (
            "El acceso a la base de datos desde la aplicación Django se realiza "
            "a través de su mapeador objeto relacional, una capa de abstracción "
            "que traduce clases de Python en tablas y consultas en métodos del "
            "lenguaje. Este enfoque reduce el riesgo de errores manuales en la "
            "construcción de sentencias SQL, facilita la portabilidad entre "
            "motores de base de datos y permite expresar de manera declarativa "
            "las restricciones de integridad y las relaciones entre entidades "
            "(Django Software Foundation, 2024). En el contexto del sistema "
            "propuesto, el mapeador objeto relacional modela conceptos como "
            "animales, solicitudes de adopción, casos médicos, donaciones y "
            "reportes comunitarios como entidades de primer orden, con "
            "relaciones explícitas que reflejan las reglas de negocio de la "
            "fundación."
        ),
    ]:
        add_body(doc, parrafo)
    add_blank_line(doc)

    # 1.5
    add_heading_2(doc, "1.5. Diseño responsivo y bibliotecas de presentación")
    add_blank_line(doc)
    for parrafo in [
        (
            "La presentación de un sistema web debe adaptarse a la diversidad "
            "de dispositivos desde los que la ciudadanía accede a internet, "
            "que abarca desde teléfonos móviles hasta computadoras de "
            "escritorio. El diseño responsivo, basado en una rejilla flexible, "
            "imágenes adaptables y consultas de medios, permite que la "
            "interfaz reorganice sus elementos en función del tamaño y la "
            "orientación de la pantalla. Bootstrap es una biblioteca de "
            "presentación ampliamente adoptada que provee componentes y "
            "utilidades preconstruidas para implementar este enfoque sin "
            "necesidad de escribir todo el sistema de estilos desde cero "
            "(Bootstrap Team, 2024)."
        ),
        (
            "Complementariamente, el sistema propuesto incorpora HTMX, una "
            "biblioteca pequeña que extiende el lenguaje HTML para permitir "
            "interacciones dinámicas mediante atributos declarativos, sin "
            "requerir frameworks de JavaScript del lado del cliente (Gross, "
            "2024). Este enfoque, conocido como hipermedia, se alinea con la "
            "filosofía de Django de generar páginas en el servidor y "
            "transferir fragmentos de HTML en lugar de objetos JSON, lo que "
            "simplifica el desarrollo y reduce la complejidad del código "
            "frontend en proyectos donde no se justifica una aplicación de "
            "página única. La combinación de Bootstrap y HTMX ofrece una "
            "experiencia de usuario moderna, accesible y mantenible, en línea "
            "con los recursos y la curva de aprendizaje del equipo de "
            "desarrollo de un proyecto de grado."
        ),
    ]:
        add_body(doc, parrafo)

    doc.add_page_break()


def build_referencias(doc):
    add_heading_1(doc, "Referencias")
    add_blank_line(doc)

    refs = [
        "Albarracín, M., y Vásquez, J. (2021). Tecnologías de la información aplicadas a la gestión de organizaciones de protección animal en el Ecuador. Revista Ciencia y Tecnología, 14(2), 45 a 58.",
        "Asamblea Constituyente del Ecuador. (2008). Constitución de la República del Ecuador. Registro Oficial 449. https://www.asambleanacional.gob.ec/",
        "Asamblea Nacional del Ecuador. (2010). Código Orgánico de Organización Territorial, Autonomía y Descentralización. Registro Oficial Suplemento 303.",
        "Asamblea Nacional del Ecuador. (2017). Código Orgánico del Ambiente. Registro Oficial Suplemento 983. https://www.ambiente.gob.ec/",
        "Bootstrap Team. (2024). Bootstrap documentation. https://getbootstrap.com/docs/",
        "Date, C. J. (2003). Introducción a los sistemas de bases de datos (7.a ed.). Pearson Educación.",
        "Django Software Foundation. (2024). Django documentation. https://docs.djangoproject.com/",
        "Gross, C. (2024). HTMX documentation. https://htmx.org/docs/",
        "Laudon, K. C., y Laudon, J. P. (2020). Sistemas de información gerencial (16.a ed.). Pearson Educación.",
        "Ministerio del Ambiente, Agua y Transición Ecológica. (2023). Lineamientos para el bienestar de la fauna urbana en el Ecuador. https://www.ambiente.gob.ec/",
        "Ministerio de Salud Pública del Ecuador. (2022). Programa Nacional de Tenencia Responsable y Control de la Población Canina y Felina. https://www.salud.gob.ec/",
        "PostgreSQL Global Development Group. (2024). PostgreSQL documentation. https://www.postgresql.org/docs/",
        "Pressman, R. S., y Maxim, B. R. (2014). Ingeniería del software: un enfoque práctico (8.a ed.). McGraw Hill.",
        "Protección Animal Ecuador. (2022). Informe anual de gestión de bienestar animal. https://www.pae.ec/",
        "Python Software Foundation. (2024). Python documentation. https://docs.python.org/3/",
        "Silberschatz, A., Korth, H. F., y Sudarshan, S. (2020). Fundamentos de bases de datos (7.a ed.). McGraw Hill.",
        "Sommerville, I. (2011). Ingeniería de software (9.a ed.). Pearson Educación.",
    ]
    for r in refs:
        add_reference(doc, r)


# ---------------------------------------------------------------------------
# Build & validate
# ---------------------------------------------------------------------------

def main():
    doc = Document()
    set_base_style(doc)
    set_margins(doc)
    add_page_number(doc)

    build_portada(doc)
    build_introduccion(doc)
    build_marco_teorico(doc)
    build_referencias(doc)

    # Validacion: no debe haber em dashes (U+2014) ni en dashes (U+2013) en la prosa
    bad_chars = {"—": "em dash", "–": "en dash"}
    for p in doc.paragraphs:
        for ch, name in bad_chars.items():
            if ch in p.text:
                raise SystemExit(
                    f"ERROR: encontrado {name} en parrafo: {p.text[:120]!r}"
                )

    doc.save(OUT)
    print(f"OK: documento generado en {OUT}")


if __name__ == "__main__":
    main()
