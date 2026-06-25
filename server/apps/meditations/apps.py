"""
Django AppConfig for the meditations app.
"""

from django.apps import AppConfig


class MeditationsConfig(AppConfig):
    """Configuration for the meditations app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.meditations"
    verbose_name = "Meditations"
