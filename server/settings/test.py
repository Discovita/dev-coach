"""
Test settings for Django test suite.

Extends common settings with test-specific configurations.
"""

from settings.common import *
import os

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
CELERY_BROKER_URL = "redis://redis:6379/0" # Local Redis instance
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
