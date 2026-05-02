"""
Django AppConfig for the prompts app.

See: apps/prompts/__init__.py
"""

from django.apps import AppConfig


class PromptsConfig(AppConfig):
    """Configuration for the prompts app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.prompts"
    verbose_name = "Prompts"
