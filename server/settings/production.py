from settings.common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["PROD_DB_NAME"],
        "USER": os.environ["PROD_DB_USER"],
        "PASSWORD": os.environ["PROD_DB_PASSWORD"],
        "HOST": os.environ["PROD_DB_HOST"],
        "PORT": os.environ["PROD_DB_PORT"],
    }
}

# Static files configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_URL = "/static/"
STATIC_ROOT = ".staticfiles"


# S3 Configuration
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env("PROD_AWS_STORAGE_BUCKET_NAME", default="discovita-dev-coach-production")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_DEFAULT_ACL = "public-read"
AWS_QUERYSTRING_AUTH = False

# Media files configuration
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"


CELERY_BROKER_URL = os.environ["PROD_REDIS_URL"]
CELERY_RESULT_BACKEND = None  # Or 'redis://...' if you want to store results
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = "UTC"

print(f"CELERY_BROKER_URL: {CELERY_BROKER_URL}")
print(f"CELERY_RESULT_BACKEND: {CELERY_RESULT_BACKEND}")
print(f"CELERY_TASK_TRACK_STARTED: {CELERY_TASK_TRACK_STARTED}")
print(f"CELERY_TIMEZONE: {CELERY_TIMEZONE}")
