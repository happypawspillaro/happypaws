import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = os.getenv("SECRET_KEY")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sitemaps",
    "django_htmx",
    "easy_thumbnails",
    "accounts",
    "animals",
    "adoptions",
    "medical_cases",
    "reports",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "happypaws.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "happypaws.wsgi.application"

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es"
TIME_ZONE = "America/Guayaquil"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
# Para evitar perder los datos importados de otros proyectos cuando montamos un volumen,
# creamos una nueva carpeta interna para tal fin que tan bien se sirve en el static
DATA_DIR = (BASE_DIR.parent / "internal_static").resolve()
STATICFILES_DIRS = [BASE_DIR / "static", DATA_DIR]  # noqa: F405
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR.parent / "media"

# easy-thumbnails: derivados livianos para no transmitir las fotos originales
# (fotos de celular de hasta 3 MB) a quien visita desde el celular.
# - 'card': listados con muchas fotos a la vez (catálogo, casos médicos,
#   reportes) y las miniaturas de la galería en las vistas de detalle.
#   Formato cuadrado (1:1): la mayoría de fotos que sube la comunidad son
#   cuadradas o verticales, un recorte horizontal les corta al animal (#71).
# - 'detalle': la foto grande de las vistas de un solo registro y la imagen
#   de OpenGraph. Sin recorte, solo la achica para que entre en 1200x1200 y
#   nunca la agranda (#72). WhatsApp no muestra la vista previa de un link si
#   la imagen pesa demasiado, por eso tampoco se usa el original en og:image.
#   'replace_alpha' convierte a JPG los PNG con transparencia (hay fotos de
#   celular guardadas así) que si no seguirían pesando más de 1 MB.
# Cada derivado pesa una fracción del original, así que no ocupa mucho más
# espacio en el VPS. Se genera bajo demanda en la primera visita y se guarda
# junto al original en MEDIA_ROOT (lo sirve nginx igual que los originales).
THUMBNAIL_ALIASES = {
    "": {
        "card": {"size": (320, 320), "crop": "smart"},
        "detalle": {"size": (1200, 1200), "quality": 80, "replace_alpha": "white"},
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "core:home"

MESSAGE_TAGS = {
    10: "secondary",  # DEBUG
    20: "info",  # INFO
    25: "success",  # SUCCESS
    30: "warning",  # WARNING
    40: "danger",  # ERROR
}

# Modo INFO por defecto en Django
DJANGO_LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO")

# Usar 'verbose' en DEBUG para ver los threads, 'simple' para producción
LOG_FORMATTER = "verbose" if DJANGO_LOG_LEVEL == "DEBUG" else "simple"

# Configuraciones de logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            # Added {threadName} and {thread} (Thread ID)
            "format": "{levelname} {asctime} [{threadName} (ID: {thread})] {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": DJANGO_LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": LOG_FORMATTER,  # Dynamically switches formatters
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": DJANGO_LOG_LEVEL,
            "propagate": False,  # Changed to False to prevent duplicate logs in root
        },
    },
    "root": {  # Root is a top-level key, not inside "loggers"
        "handlers": ["console"],
        "level": DJANGO_LOG_LEVEL,
    },
}
