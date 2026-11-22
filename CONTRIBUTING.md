# Guía de Contribución

Para contribuir al desarrollo de Happy Paws, primero prepara el entorno siguiendo la [Guía de instalación](INSTALL.md).

## Flujo de desarrollo

Se recomienda seguir este flujo de desarrollo:

- _(Opcional)_ Añadir un [issue](https://github.com/happypawspillaro/happypaws/issues) que describa el cambio propuesto.
- Crear una rama nueva a partir de `main`.
- Cumplir el [Formato de código](#formato-de-código) del proyecto.
- Si la página es pública, seguir los requisitos de [SEO](#seo-en-páginas-públicas).
- Crear un pull request y verificar que pase las pruebas de formato y regresión para su revisión.

## Configuraciones de desarrollo

Para modificar los scripts de Python y los archivos web y ver los cambios en tiempo real, inicia el entorno de desarrollo con estos comandos:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml build
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Exponer puertos

Si necesitas exponer el puerto de PostgreSQL en el equipo local para revisar datos con un programa como `DBeaver`, usa un archivo de [Docker Compose Override](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/):

1. Crea el archivo local `docker-compose.prod.override.yml`:

   ```bash
   touch docker-compose.prod.override.yml
   ```

2. Añade esta configuración. El puerto queda disponible solo desde el mismo equipo:

   ```yaml
   services:
    postgres:
     ports:
      - "127.0.0.1:5432:5432"
   ```

3. Inicia PostgreSQL aplicando el override:

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml \
     -f docker-compose.prod.override.yml up -d postgres
   ```

   Conecta DBeaver a `127.0.0.1:5432`.

### Incrementar la verbosidad

Si necesitas más detalle en los registros del sistema, descomenta `DJANGO_LOG_LEVEL=DEBUG` en tu archivo `.env`. Consulta la [guía de variables de entorno](REFERENCE.md#variables-de-entorno) para más información:

```dotenv
DJANGO_LOG_LEVEL=DEBUG
```

## SEO en páginas públicas

Toda página nueva que sea visible sin iniciar sesión debe incluir su SEO:

- Un `{% block title %}` propio y un único `<h1>` que describa la página.
- El bloque `{% block seo %}` con `includes/seo_meta.html`, pasando `titulo`, `descripcion` y, si la página tiene foto, `imagen`. Así se generan la descripción para buscadores y la vista previa al compartir el link en WhatsApp, Facebook, Telegram o X.
- Texto alternativo (`alt`) descriptivo en las imágenes, con nombre y ubicación cuando aplique.
- Si es una página nueva o un modelo con página de detalle, añadirlo en `core/sitemaps.py`.
- Pruebas en `core/test_seo.py` que verifiquen lo anterior.

## Formato de Código

Para facilitar el mantenimiento y la colaboración, sigue el formato de código del proyecto. Las instrucciones para Python y frontend están en las siguientes secciones:

### Python

Para formatear tus archivos de Python, sigue las siguientes instrucciones:

1. En Linux o macOS, crea y activa un entorno virtual de Python e instala las herramientas de formato y análisis:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install black flake8 flake8-pyproject isort pylint pylint-django djlint
   ```

2. Ejecuta las herramientas de Python en una pasada con `linters.sh`, indicando como argumento el archivo que quieres revisar:

   ```bash
   ./linters.sh carpeta/codigo.py
   ```

3. Para formatear tus [plantillas de Django](https://docs.djangoproject.com/en/6.1/topics/templates/), usa `djlint`:

   ```bash
   djlint --reformat carpeta/templates/plantilla.html
   ```

### Frontend

Para formatear y revisar JavaScript, JSON, CSS y otros archivos del frontend, usa las herramientas declaradas en `package.json`.

El servidor Playwright MCP configurado en `.mcp.json` requiere Node.js 20 o posterior. Sigue las instrucciones de [instalación de Node.js y npm](INSTALL.md#nodejs-y-npm-opcional) y ejecuta `npm ci` desde la raíz del proyecto para instalar de una vez las dependencias fijadas en `package-lock.json`: Playwright MCP, Biome y Prettier.

Para añadir paquetes npm y mantener sincronizados el manifiesto y el lockfile:

- Herramientas usadas solo durante el desarrollo:

  ```bash
  npm install --save-dev --save-exact <paquete>
  ```

- Dependencias de ejecución para un componente Node.js:

  ```bash
  npm install --save-prod --save-exact <paquete>
  ```

El sitio corre en Django: sus dependencias de ejecución se agregan en `web/requirements.txt`, no en npm. Al añadir o cambiar paquetes npm, confirma los cambios en `package.json` y `package-lock.json`; Dependabot revisa estas dependencias semanalmente.

Ejecuta los formateadores instalados:

```bash
# Formatea y escribe el código
npx prettier --write CONTRIBUTING.md
# Formatea el código
npx biome format app/static/js/file.js
# Verifica errores
npx biome lint app/static/js/file.js
```
