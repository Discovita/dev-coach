"""
Django AppConfig for the reference_images app.

See: apps/reference_images/__init__.py
"""

from django.apps import AppConfig


class ReferenceImagesConfig(AppConfig):
    """Configuration for the reference_images app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reference_images"
    verbose_name = "Reference Images"
