from settings.common import *

DEBUG = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["LOCAL_AGENT_DB_NAME"],
        "USER": os.environ["LOCAL_AGENT_DB_USER"],
        "PASSWORD": os.environ["LOCAL_AGENT_DB_PASSWORD"],
        "HOST": os.environ["LOCAL_AGENT_DB_HOST"],
        "PORT": os.environ["LOCAL_AGENT_DB_PORT"],
    },
    "langgraph": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["LOCAL_LANGGRAPH_DB_NAME"],
        "USER": os.environ["LOCAL_AGENT_DB_USER"],
        "PASSWORD": os.environ["LOCAL_AGENT_DB_PASSWORD"],
        "HOST": os.environ["LOCAL_AGENT_DB_HOST"],
        "PORT": os.environ["LOCAL_AGENT_DB_PORT"],
    },
}

# Whitenoise configuration for development
WHITENOISE_ROOT = STATIC_ROOT  # Use the same absolute path
WHITENOISE_USE_FINDERS = True
WHITENOISE_INDEX_FILE = True

CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = None  # Or 'redis://...' if you want to store results
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = "UTC"

# Optional: Add debug logging for static files
if DEBUG:
    print(f"Static root path: {STATIC_ROOT}")
    print(f"Base dir: {BASE_DIR}")
    print(f"Database: {DATABASES}")
    print(f"Settings Module: {env('DJANGO_SETTINGS_MODULE')}")
    print(f"Access the backend here: http://localhost:8000/admin")
