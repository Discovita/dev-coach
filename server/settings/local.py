from settings.common import *

DEBUG = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["LOCAL_DB_NAME"],
        "USER": os.environ["LOCAL_DB_USER"],
        "PASSWORD": os.environ["LOCAL_DB_PASSWORD"],
        "HOST": os.environ["LOCAL_DB_HOST"],
        "PORT": os.environ["LOCAL_DB_PORT"],
    }
}

# Whitenoise configuration for development
WHITENOISE_ROOT = STATIC_ROOT  # Use the same absolute path
WHITENOISE_USE_FINDERS = True
WHITENOISE_INDEX_FILE = True

CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = None  # Or 'redis://...' if you want to store results
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = "UTC"

# S3 Configuration - Local development uses staging bucket
# Note: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set in common.py
bucket_name = env(
    "STAGING_AWS_STORAGE_BUCKET_NAME", default="discovita-dev-coach-staging"
)
custom_domain = f"{bucket_name}.s3.amazonaws.com"
# S3 prefix under which all media is stored. Env-driven for symmetry with
# the deployed environments (defaults to "media" so local behavior is
# unchanged).
s3_location = env("S3_LOCATION_PREFIX", default="media")

# Media files configuration - Use S3 for local development (staging bucket)
# Django 4.2+ STORAGES format per django-storages documentation
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "bucket_name": bucket_name,
            "region_name": env("AWS_REGION", default="us-east-1"),
            "location": s3_location,
            "custom_domain": custom_domain,
            # Note: ACLs are disabled on this bucket. Public access is handled via bucket policy.
            "object_parameters": {
                "CacheControl": "max-age=86400",
            },
            "querystring_auth": False,
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = f"https://{custom_domain}/{s3_location}/"

# Optional: Add debug logging for static files
if DEBUG:
    print(f"Static root path: {STATIC_ROOT}")
    print(f"Base dir: {BASE_DIR}")
    print(f"Database: {DATABASES}")
    print(f"Settings Module: {env('DJANGO_SETTINGS_MODULE')}")
    print("Access the backend here: http://localhost:8000/admin")
