# Configuración para el despliegue gratuito en PythonAnywhere.
# Hereda de base.py y usa SQLite (el plan gratuito no tiene Postgres ni Docker).
import os

from .base import *  # noqa: F403

DEBUG = False

# En PythonAnywhere el dominio es <usuario>.pythonanywhere.com.
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", ".pythonanywhere.com").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS", "https://*.pythonanywhere.com"
).split(",")

# Estáticos: collectstatic vuelca aquí; esta ruta es la que se mapea en la
# pestaña Web (sección Static files).
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
STATICFILES_DIRS = [BASE_DIR / "static"]  # noqa: F405

# SQLite en el disco persistente de PythonAnywhere.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR.parent / "db.sqlite3",  # noqa: F405
    }
}
