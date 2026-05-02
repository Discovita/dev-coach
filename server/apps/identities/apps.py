from django.apps import AppConfig


class IdentitiesConfig(AppConfig):
    """
    Configuration for the identities app.

    Manages user identity definitions, image generation chat sessions,
    and PDF export of identity cards.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.identities"
    verbose_name = "Identities"
