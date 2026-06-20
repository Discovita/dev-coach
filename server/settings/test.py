"""
Test settings for Django test suite.

Extends common settings with test-specific configurations.
"""

import os

# common.py reads the AWS_SES_* settings from the environment with no defaults,
# so it raises ImproperlyConfigured at import time when no .env is present (e.g.
# running the suite outside the Docker container). Provide harmless dummy values
# BEFORE importing common so auth tests run anywhere. Real email sends are mocked
# at the service seam (send_password_reset_email / send_verification_email).
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access-key-id")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret-access-key")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("AWS_SES_REGION_NAME", "us-east-1")
os.environ.setdefault("AWS_SES_REGION_ENDPOINT", "email.us-east-1.amazonaws.com")
os.environ.setdefault("AWS_SES_SOURCE_EMAIL", "noreply@neovita.ai")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")

from settings.common import *

# Never hit a real mail provider in tests; collect messages in memory instead.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Use a separate test database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("TEST_DB_NAME", "test_local_dev_coach"),
        "USER": os.environ.get("LOCAL_DB_USER", "dev_coach_database_user"),
        "PASSWORD": os.environ.get("LOCAL_DB_PASSWORD", "dev_coach_database_password"),
        "HOST": os.environ.get("LOCAL_DB_HOST", "db"),
        "PORT": os.environ.get("LOCAL_DB_PORT", "5432"),
    }
}

# Disable migrations for faster tests (optional - comment out if you need migrations)
# PASSWORD_HASHERS = [
#     "django.contrib.auth.hashers.MD5PasswordHasher",
# ]

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable logging during tests (optional)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["console"],
    },
}

# Disable Celery during tests
CELERY_BROKER_URL = "redis://redis:6379/0"  # Local Redis instance
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
