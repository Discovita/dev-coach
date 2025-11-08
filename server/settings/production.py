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
STATIC_URL = "/static/"
STATIC_ROOT = ".staticfiles"


# S3 Configuration
# Note: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set in common.py
bucket_name = env("PROD_AWS_STORAGE_BUCKET_NAME", default="discovita-dev-coach-production")
custom_domain = f"{bucket_name}.s3.amazonaws.com"

# Media files configuration
# Django 4.2+ STORAGES format per django-storages documentation
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "bucket_name": bucket_name,
            "region_name": env("AWS_REGION", default="us-east-1"),
            "location": "media",  # Prefix for all files stored in S3
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

MEDIA_URL = f"https://{custom_domain}/media/"


CELERY_BROKER_URL = os.environ["PROD_REDIS_URL"]
CELERY_RESULT_BACKEND = None  # Or 'redis://...' if you want to store results
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = "UTC"

print(f"CELERY_BROKER_URL: {CELERY_BROKER_URL}")
print(f"CELERY_RESULT_BACKEND: {CELERY_RESULT_BACKEND}")
print(f"CELERY_TASK_TRACK_STARTED: {CELERY_TASK_TRACK_STARTED}")
print(f"CELERY_TIMEZONE: {CELERY_TIMEZONE}")
