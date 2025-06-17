from settings.common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": env.db("DJANGO_DATABASE_PROD_URL", default=""),
}

# Static files configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_URL = "/static/"
STATIC_ROOT = ".staticfiles"


# S3 Configuration
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="")
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


CELERY_URL = "redis://red-d18irs8dl3ps738eim30:6379"
