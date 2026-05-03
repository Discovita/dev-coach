"""Settings for ephemeral PR preview environments on Render."""
from settings.common import *

DEBUG = False

# Database — the preview's own ephemeral Postgres, wired by Render's
# fromDatabase ref in render.yaml. The data inside is seeded from a
# pg_dump of the staging DB during the preview's preDeploy step.
# (The seed only runs on PR-spawned previews, gated by RENDER_GIT_PR_NUMBER
# in render.yaml — the base/template service skips it.)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["PREVIEW_DB_NAME"],
        "USER": os.environ["PREVIEW_DB_USER"],
        "PASSWORD": os.environ["PREVIEW_DB_PASSWORD"],
        "HOST": os.environ["PREVIEW_DB_HOST"],
        "PORT": os.environ["PREVIEW_DB_PORT"],
    }
}

# Static files configuration
STATIC_URL = "/static/"
STATIC_ROOT = ".staticfiles"


# S3 Configuration
# Note: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set in common.py
# Reuse the staging bucket — previews share it with staging but are
# scoped into their own per-PR subfolder via S3_LOCATION_PREFIX.
bucket_name = env(
    "STAGING_AWS_STORAGE_BUCKET_NAME", default="discovita-dev-coach-staging"
)
custom_domain = f"{bucket_name}.s3.amazonaws.com"
# Required — the blueprint sets this per preview to something like
# "previews/pr-101/media". No default: silent collisions with staging
# data would be far worse than a hard failure on misconfiguration.
s3_location = os.environ["S3_LOCATION_PREFIX"]

# Media files configuration
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


# Celery — preview's own Redis, wired by Render's fromService ref in render.yaml.
CELERY_BROKER_URL = os.environ["PREVIEW_REDIS_URL"]
CELERY_RESULT_BACKEND = None
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = "UTC"
