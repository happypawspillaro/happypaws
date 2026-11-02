# Guía para agentes de código

## Arquitectura

- Happy Paws es un sitio Django con páginas renderizadas en el servidor. La
  configuración de rutas en `web/code/happypaws/urls.py` conecta las apps
  `accounts`, `animals`, `adoptions`, `medical_cases`, `reports` y `core`.
- Cada app es dueña de su flujo: cuentas y usuario personalizado; animales e
  historial médico; solicitudes de adopción; casos médicos y aportes; reportes
  comunitarios. `core` reúne inicio, panel del staff, utilidades compartidas,
  SEO, sitemaps y el comando `seed_demo`.
- La configuración común está en `web/code/happypaws/settings/base.py`;
  `local.py` usa SQLite y los demás módulos configuran despliegues. Las
  plantillas de cada app están en `web/code/templates/<app>/` y las
  compartidas en `web/code/templates/includes/`.
- La interfaz usa plantillas Django, Bootstrap y HTMX. Conserva el renderizado
  del lado del servidor y sigue las rutas, vistas y plantillas de cada app.

## Comandos

- Entorno de desarrollo Docker (desde la raíz; ver también
  `CONTRIBUTING.md`):

  ```bash
  docker compose -f docker-compose.yml -f docker-compose.dev.yml build
  docker compose -f docker-compose.yml -f docker-compose.dev.yml up
  ```

- Ejecutar todas las pruebas Django desde `web/code`:

  ```bash
  SECRET_KEY=ci-secret-key-not-for-production DJANGO_SETTINGS_MODULE=happypaws.settings.local python3 manage.py test
  ```

- Ejecutar un método de prueba específico desde `web/code`:

  ```bash
  SECRET_KEY=ci-secret-key-not-for-production DJANGO_SETTINGS_MODULE=happypaws.settings.local python3 manage.py test core.test_seo.TituloSEOTests.test_animal_en_adopcion
  ```

- CI ejecuta las pruebas con cobertura desde `web/code`:
  `coverage run --rcfile=../../pyproject.toml --branch manage.py test`.
- Para un archivo Python, `./linters.sh ruta/al/archivo.py` ejecuta isort,
  Black, flake8 y pylint. isort y Black modifican el archivo.
- Para plantillas Django, `djlint --reformat ruta/a/plantilla.html` está
  documentado en `CONTRIBUTING.md`. El workflow de Super-Linter verifica el
  formato y lint del repositorio.

## Convenciones del proyecto

- SEO e indexación en buscadores son requisitos para las páginas públicas,
  no mejoras opcionales. Sigue el checklist de `CONTRIBUTING.md`: bloque
  `title` propio, un único `<h1>` descriptivo y bloque `seo` con
  `includes/seo_meta.html`; añade páginas públicas y detalles de modelos a
  `core/sitemaps.py`, y cubre metadatos, encabezados y textos alternativos en
  `core/test_seo.py`.
- Este sistema gestiona información de una fundación y de la comunidad.
  Respeta la normativa ecuatoriana de protección de datos personales (LOPDP) y
  la política vigente en `templates/core/privacidad.html`: recoge y publica
  solo los datos necesarios y conserva el consentimiento en formularios
  públicos que tratan datos personales, siguiendo los patrones de `core/forms.py`.
- Usa nombres de URL con namespace y resuélvelos con las utilidades de Django
  en vez de escribir rutas internas directamente.
- Para estilos, reutiliza la paleta existente en
  `web/code/static/css/styles.css` (incluidos `--hp-primary` y las variables de
  Bootstrap); no introduzcas colores de marca fuera de esa paleta.
- Las imágenes usan los aliases de `easy-thumbnails` definidos en
  `happypaws/settings/base.py`: `card` para listados y `detalle` para páginas
  de detalle y metadatos SEO.
- Las pruebas usan `TestCase`/`SimpleTestCase` y están junto a su app en
  `tests.py` o `test_*.py`; los mixins compartidos están en
  `core/tests_common/`.
- Mantén esta guía breve y enlaza a `CONTRIBUTING.md`, `INSTALL.md` y
  `REFERENCE.md` para el detalle que evolucione, evitando duplicar sus
  instrucciones.
- Prioriza cambios pequeños pero completos: revisa los usos y superficies
  afectados, reutiliza patrones existentes y evita abstracciones, opciones o
  dependencias sin necesidad. Conserva validaciones, manejo de errores,
  privacidad, seguridad y accesibilidad; acompaña los cambios no triviales con
  una prueba enfocada. Este enfoque adapta las prácticas de
  [Ponytail](https://github.com/DietrichGebert/ponytail) al proyecto.
