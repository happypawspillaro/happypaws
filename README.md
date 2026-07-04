# Happy Paws Píllaro — Sistema web

[![Super-Linter](https://github.com/happypawspillaro/happypaws/actions/workflows/super-linter.yml/badge.svg)](https://github.com/marketplace/actions/super-linter)

Sistema web para la fundación **Happy Paws Píllaro** (Píllaro, Tungurahua,
Ecuador), dedicada a la esterilización y adopción responsable de perros y gatos.
Proyecto de titulación.

Centraliza en un solo lugar la operación que hoy la fundación maneja de forma
dispersa en redes sociales: catálogo de animales en adopción, casos médicos con
recaudación, y reportes comunitarios de mascotas perdidas/encontradas y maltrato.

## Módulos

| Módulo            | Portal público                                                  | Panel administrativo (staff)                                        |
| ----------------- | --------------------------------------------------------------- | ------------------------------------------------------------------- |
| **Animales**      | Catálogo en adopción con filtros, ficha de cada animal          | CRUD, fotos e historial médico                                      |
| **Adopciones**    | Formulario de solicitud por animal                              | Gestión de solicitudes, cambio de estado, seguimiento post-adopción |
| **Casos médicos** | Listado y detalle con barra de recaudación, registro de aportes | CRUD, verificación de donaciones, bitácora de avances               |
| **Reportes**      | Tablero comunitario y formulario de reporte                     | Gestión y marcado de resueltos                                      |
| **Core**          | Página de inicio con destacados                                 | Dashboard con métricas                                              |

## Stack

- **Django 5.1** — plantillas server-rendered
- **HTMX** — filtros e interacciones sin recarga
- **Bootstrap 5** — interfaz
- **SQLite** en desarrollo (configurable a PostgreSQL vía `DATABASE_URL`)

## Instalación

Puedes consultar en el apartado [Instalación](INSTALL.md) para saber como inicializar la página web.

## Configuración

Variables en `.env` (ver `.env.example`):

- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `DATABASE_URL` — `sqlite:///db.sqlite3` por defecto; para PostgreSQL:
  `postgres://usuario:clave@127.0.0.1:5432/happypaws`

## Pruebas

```bash
python manage.py test
```

## Estructura

```bash
happypaws/      Configuración del proyecto (settings, urls)
accounts/       Usuario custom y autenticación
animals/        Catálogo, fichas e historial médico
adoptions/      Solicitudes de adopción y seguimiento
medical_cases/  Casos médicos, donaciones y avances
reports/        Reportes de perdidos/encontrados/maltrato
core/           Página de inicio, dashboard y comando seed_demo
templates/      Plantillas (base + por app)
static/         CSS
```

## Formato de Código

Como buenas prácticas de código para un fácil mantenimiento y colaboración, se sugiere ajustarse al formato de código usado en el proyecto, éste se divide entre código de Python y del Frontend, para saber como configurar tus formateadores d código, revisa las siguientes subsecciones:

### Python

Para formatear tus archivos de Python, sigue las siguientes instrucciones:

1. Crea un nuevo o usa tu ambiente de Python e instala los formateadores con el siguiente comando:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install black flake8 flake8-pyproject isort pylint pylint-django
   # Permite ejecutar el script  
   sudo chmod +x linters.sh
   ```

2. Puedes ejecutar todos los formateadores de una pasada con el script `linters.sh` y especificando como argumento tu script de Python

   ```bash
   ./linters.sh carpeta/codigo.py
   ```

### Frontend

Para formatear y ver errores de código en JavaScript, JSON, CSS, etc. puedes usar las herramientas como `prettier` o `biome`, los puedes instalar así como se muestra en los siguientes pasos:

1. Instala `nodejs` junto las herramientas con `npm` y `npx`, por ejemplo en Ubuntu:

   ```bash
   sudo apt update && sudo apt install nodejs
   ```

2. Instala los formateadores necesarios, por ejemplo en Ubuntu

   ```bash
   npm install --save-dev --save-exact @biomejs/biome prettier
   ```

3. Puedes usar los formateadores de la siguiente forma

   ```bash
   # Formatea y escribe el código
   npx prettier --write DEVELOPMENT.md
   # Formatear código
   npx biome format app/static/js/file.js
   # Verificar errores
   npx biome lint app/static/js/file.js
   ```
