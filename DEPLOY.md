# Despliegue gratuito en PythonAnywhere

Guía para publicar **Happy Paws Píllaro** en una URL pública gratuita
(`https://tuusuario.pythonanywhere.com`), sin tarjeta de crédito y sin que la
app se "duerma".

> Reemplaza `tuusuario` por tu nombre de usuario real de PythonAnywhere en
> todos los pasos.

## 1. Subir el código a GitHub

PythonAnywhere clona el proyecto desde un repositorio. Desde tu máquina:

```bash
git add .
git commit -m "Preparar despliegue"
git remote add origin https://github.com/tuusuario/happypaws.git
git push -u origin main
```

`.gitignore` ya excluye `.venv/`, `.env`, `db.sqlite3` y `/media/`, así que no
se sube nada sensible ni la base de datos local.

## 2. Crear la cuenta y clonar

1. Regístrate en https://www.pythonanywhere.com (plan **Beginner**, gratis).
2. Abre una consola **Bash** (pestaña _Consoles_ → _Bash_).
3. Clona el proyecto:

   ```bash
   git clone https://github.com/tuusuario/happypaws.git
   cd happypaws
   ```

## 3. Crear el entorno virtual e instalar dependencias

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Crear el archivo `.env` de producción

Genera una clave nueva:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Crea el archivo `.env` (editor _Files_ o `nano .env`) con:

```
SECRET_KEY=pega-aqui-la-clave-generada
DEBUG=False
ALLOWED_HOSTS=tuusuario.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://tuusuario.pythonanywhere.com
DATABASE_URL=sqlite:///db.sqlite3
```

## 5. Preparar la base de datos y los estáticos

Con el virtualenv activo y dentro de `~/happypaws`:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## 6. Crear la aplicación web

1. Pestaña **Web** → _Add a new web app_.
2. Elige **Manual configuration** → **Python 3.11**.
3. En la sección **Virtualenv**, escribe la ruta:
   `/home/tuusuario/happypaws/.venv`

## 7. Configurar el archivo WSGI

En la pestaña **Web**, sección _Code_, clic en el enlace del archivo WSGI.
Borra todo su contenido y déjalo así:

```python
import os
import sys

path = "/home/tuusuario/happypaws"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "happypaws.settings"

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
```

## 8. Mapear archivos estáticos y media

En la pestaña **Web**, sección _Static files_, añade dos filas:

| URL        | Directory                               |
| ---------- | --------------------------------------- |
| `/static/` | `/home/tuusuario/happypaws/staticfiles` |
| `/media/`  | `/home/tuusuario/happypaws/media`       |

## 9. Recargar y probar

Pulsa el botón verde **Reload** en la pestaña Web y abre
`https://tuusuario.pythonanywhere.com`.

Acceso al panel del staff:

- Usuario: `fundacion`
- Contraseña: `happypaws123`

> **Importante:** cambia esa contraseña antes de compartir el enlace con la
> fundación. Entra al panel y actualízala, o crea un usuario nuevo con
> `python manage.py createsuperuser`.

## Actualizar la app después de cambios

Cuando hagas cambios en el código:

```bash
cd ~/happypaws
git pull
source .venv/bin/activate
pip install -r requirements.txt        # solo si cambió requirements.txt
python manage.py migrate               # solo si hay migraciones nuevas
python manage.py collectstatic --noinput
```

Luego pulsa **Reload** en la pestaña Web.

## Notas

- La base de datos es SQLite y vive en el disco persistente de PythonAnywhere:
  los datos no se pierden entre recargas ni reinicios.
- El plan gratuito **no se duerme**: el enlace responde al instante siempre.
- Las fotos que suba el staff quedan en `~/happypaws/media/`, también
  persistente.
