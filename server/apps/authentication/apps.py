from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Configuration for the authentication app.

    Provides registration, login, and password-reset endpoints.
    Email verification and password-reset emails are sent via AWS SES.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.authentication"
    verbose_name = "Authentication"
