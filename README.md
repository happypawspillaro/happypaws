# Happy Paws Píllaro — Sistema web

[![Super-Linter](https://github.com/happypawspillaro/happypaws/actions/workflows/super-linter.yml/badge.svg)](https://github.com/marketplace/actions/super-linter)
[![Django CI](https://github.com/happypawspillaro/happypaws/actions/workflows/django-ci.yml/badge.svg)](https://github.com/happypawspillaro/happypaws/actions/workflows/django-ci.yml)
[![codecov](https://codecov.io/gh/happypawspillaro/happypaws/graph/badge.svg?branch=main)](https://codecov.io/gh/happypawspillaro/happypaws)

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

- **Django 6** — plantillas server-rendered
- **HTMX 2** — filtros e interacciones sin recarga
- **Bootstrap 5** — interfaz
- **PostgreSQL 18** - Base de datos principal
- **SQLite** - Base de datos en modo desarrollo

## Instalación

Puedes consultar en el apartado [Instalación](INSTALL.md) para saber como inicializar la página web.

## Pruebas

```bash
export SECRET_KEY="<tu_clave_secreta>"
cd web/code; python manage.py test
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

## ¿Cómo contribuir?

Por favor lee la [Guía de contribución](CONTRIBUTING.md)

## Errores comunes

### Permisos del volumen media

Si en tus logs del contenedor `web` obtienes el siguiente mensaje:

```bash
web-1    |   File "/usr/local/lib/python3.14/site-packages/django/core/files/storage/filesystem.py", line 113, in _save
web-1    |     fd = os.open(full_path, open_flags, 0o666)
web-1    | PermissionError: [Errno 13] Permission denied: '/home/happypaws/media/reportes/animal.jpg'
```

Es porque el volumen persiste con permisos de `root` desde su primera creación, puedes cambiar sus permisos permanentemente con el comando:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -u root web chown -R 1001:1001 /home/happypaws/media
```
