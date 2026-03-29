from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuration for the core app.

    The core app holds project-wide infrastructure: middleware,
    management commands, pagination, serializer helpers, and
    utility ViewSets (e.g., the enums endpoint).
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"
