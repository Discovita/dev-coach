"""
Django AppConfig for the user_notes app.
"""

from django.apps import AppConfig


class UserNotesConfig(AppConfig):
    """Configuration for the user_notes app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.user_notes"
    verbose_name = "User Notes"
