# Happy Paws Píllaro — Sistema web

Sistema web para la fundación **Happy Paws Píllaro** (Píllaro, Tungurahua,
Ecuador), dedicada a la esterilización y adopción responsable de perros y gatos.
Proyecto de titulación.

Centraliza en un solo lugar la operación que hoy la fundación maneja de forma
dispersa en redes sociales: catálogo de animales en adopción, casos médicos con
recaudación, y reportes comunitarios de mascotas perdidas/encontradas y maltrato.

## Módulos

| Módulo | Portal público | Panel administrativo (staff) |
|---|---|---|
| **Animales** | Catálogo en adopción con filtros, ficha de cada animal | CRUD, fotos e historial médico |
| **Adopciones** | Formulario de solicitud por animal | Gestión de solicitudes, cambio de estado, seguimiento post-adopción |
| **Casos médicos** | Listado y detalle con barra de recaudación, registro de aportes | CRUD, verificación de donaciones, bitácora de avances |
| **Reportes** | Tablero comunitario, formulario de reporte, **comentarios y avistamientos** que cualquiera puede dejar en un aviso | Gestión, marcado de resueltos, confirmación de avistamientos y moderación (ocultar/eliminar) |
| **Core** | Página de inicio con destacados | Dashboard con métricas |

## Stack

- **Django 5.1** — plantillas server-rendered
- **HTMX** — filtros e interacciones sin recarga
- **Bootstrap 5** — interfaz
- **SQLite** en desarrollo (configurable a PostgreSQL vía `DATABASE_URL`)

## Instalación

```bash
# 1. Entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Dependencias
pip install -r requirements.txt

# 3. Variables de entorno
cp .env.example .env

# 4. Base de datos
python manage.py migrate

# 5. Datos de ejemplo (animales, caso médico, reportes y solicitudes)
python manage.py seed_demo

# 6. Servidor
python manage.py runserver
```

La aplicación queda en http://127.0.0.1:8000/

## Acceso

`seed_demo` crea un usuario del staff de la fundación:

- **Usuario:** `fundacion`
- **Contraseña:** `happypaws123`

Para acceder al Django admin crea un superusuario:

```bash
python manage.py createsuperuser
```

## Configuración

Variables en `.env` (ver `.env.example`):

- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `DATABASE_URL` — `sqlite:///db.sqlite3` por defecto; para PostgreSQL:
  `postgres://usuario:clave@127.0.0.1:5432/happypaws`
- `EMAIL_URL` — envío de correos. Por defecto `consolemail://` (los correos se
  imprimen en la consola). Para enviar de verdad:
  `smtp://usuario:clave@smtp.gmail.com:587/?tls=True`
- `FOUNDATION_EMAIL` — correo de la fundación que recibe avisos cuando alguien
  comenta o reporta un avistamiento en un reporte.

### Interacción comunitaria en los reportes

En el detalle de un aviso, **cualquier persona** (sin necesidad de cuenta)
puede dejar **comentarios/pistas** y, en mascotas perdidas o encontradas,
**reportar avistamientos** con ubicación, fecha y foto. Cada interacción avisa
por correo al reportante (si dejó un correo) y a la fundación. El staff puede
**confirmar** avistamientos útiles y **ocultar o eliminar** contenido
inapropiado. Los formularios incluyen un campo trampa (honeypot) anti-spam.

## Pruebas

```bash
python manage.py test
```

## Estructura

```
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
# happypaws
