from settings.common import *
import os

DEBUG = True

# Static files configuration - use absolute path from BASE_DIR
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".staticfiles"))

# Whitenoise configuration for development
WHITENOISE_ROOT = STATIC_ROOT  # Use the same absolute path
WHITENOISE_USE_FINDERS = True
WHITENOISE_INDEX_FILE = True

# Optional: Add debug logging for static files
if DEBUG:
    print(f"Static root path: {STATIC_ROOT}")
    print(f"Base dir: {BASE_DIR}")
    print(f"Database: {DATABASES}")


CELERY_BROKER_URL = "redis://red-d18irs8dl3ps738eim30:6379"
CELERY_RESULT_BACKEND = None  # Or 'redis://...' if you want to store results
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = "UTC"
