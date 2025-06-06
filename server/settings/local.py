from settings.common import *
from django.core.exceptions import ImproperlyConfigured

DEBUG = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
]

try:
    DATABASES = {
        "default": env.db("DJANGO_LOCAL_DATABASE_URL"),
    }
except ImproperlyConfigured:
    raise ImproperlyConfigured(
        "You're trying to connect to the local database from your local environment. DJANGO_LOCAL_DATABASE_URL is not set. Please set it before running the server."
    )

# Whitenoise configuration for development
WHITENOISE_ROOT = STATIC_ROOT  # Use the same absolute path
WHITENOISE_USE_FINDERS = True
WHITENOISE_INDEX_FILE = True

# Optional: Add debug logging for static files
if DEBUG:
    print(f"Static root path: {STATIC_ROOT}")
    print(f"Base dir: {BASE_DIR}")
    print(f"Database: {DATABASES}")
    print(f"Settings Module: {env('DJANGO_SETTINGS_MODULE')}")
    print(f"Access the backend here: http://localhost:8000/admin")
