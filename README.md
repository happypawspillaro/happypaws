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

- **Django 6** — plantillas server-rendered
- **HTMX 2** — filtros e interacciones sin recarga
- **Bootstrap 5** — interfaz
- **PostgreSQL 18** - Base de datos principal
- **SQLite** - Base de datos en modo desarrollo

## Instalación

Puedes consultar en el apartado [Instalación](INSTALL.md) para saber como inicializar la página web.

## Pruebas

```bash
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
