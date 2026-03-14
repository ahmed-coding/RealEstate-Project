from .base import *

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


INSTALLED_APPS = [
    # "semantic_admin",
    # "semantic_forms",
    "admin_interface",
    "colorfield",
    # 'jet.dashboard',
    # 'jet',
    "import_export",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # internal apps
    "apps",
    "apps.search",
    # # external apps
    "mptt",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "user_agents",
    "drf_spectacular",
    "schema_graph",
    "corsheaders",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "../db.sqlite3",
    }
}

# Use InMemoryChannelLayer for local development (no Redis needed)
# In production, use Redis channel layer via FastAPI
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# Override REST_FRAMEWORK to use only TokenAuthentication for API
# This avoids CSRF errors since SessionAuthentication enforces CSRF checks
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}
