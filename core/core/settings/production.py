from .base import *

# Security: Use environment variable for allowed hosts, with sensible defaults
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Override CORS settings for production
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = os.environ.get(
    "CORS_ORIGIN_WHITELIST", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")


INSTALLED_APPS = [
    "admin_interface",
    "colorfield",
    "import_export",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # internl apps
    "apps",
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

# Use PostgreSQL in production - get DATABASE_URL from environment
# Fall back to SQLite if DATABASE_URL is not set (for development)
DATABASE_URL = os.environ.get("DATABASE_URL", "")

if DATABASE_URL:
    try:
        import dj_database_url

        DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
    except ImportError:
        # Fallback if dj_database_url is not installed
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.environ.get("DB_NAME", "realestate"),
                "USER": os.environ.get("DB_USER", "postgres"),
                "PASSWORD": os.environ.get("DB_PASSWORD", ""),
                "HOST": os.environ.get("DB_HOST", "localhost"),
                "PORT": os.environ.get("DB_PORT", "5432"),
            }
        }
else:
    # Development fallback
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "../db.sqlite3",
        }
    }

# Media Files

# Note: WebSocket functionality is now handled by FastAPI service
# Channel layers are no longer needed for Django
