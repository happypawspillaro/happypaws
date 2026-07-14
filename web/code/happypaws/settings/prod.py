# No comprobar en ciertas líneas F403 y F405 para compartir las configuraciones del base.py
import os

from .base import *  # noqa: F403

DEBUG = False
ADMINS = [("Happy Paws", "happypaws.pillaro@gmail.com")]
# Permitir usar contenedor nginx
ALLOWED_HOSTS += ["nginx"]  # noqa: F405
STATIC_ROOT = BASE_DIR / "static"  # noqa: F405
STATICFILES_DIRS = [
    BASE_DIR / "staticfiles",  # noqa: F405
]

# Endurecimiento solo en producción. El proxy de PythonAnywhere/Render
# termina el TLS y reenvía la petición por HTTP con esta cabecera.
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Orígenes de confianza para CSRF. En producción bajo HTTPS Django exige
# declararlos o los formularios (login, adopciones, reportes) fallan con 403.
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")


# Abrir y leer el Docker Secrets file
def get_docker_secrets(passwd_file: str) -> str:
    with open(passwd_file, "r", encoding="utf-8") as i_file:
        passwd = i_file.read()
    return passwd.strip()


# PostgreSQL en producción
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": 5432,
        "PASSWORD": get_docker_secrets(os.getenv("POSTGRES_PASSWORD_FILE")),
    }
}
