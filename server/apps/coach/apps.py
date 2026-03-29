from django.apps import AppConfig


class CoachConfig(AppConfig):
    """
    Configuration for the coach app.

    Exposes API endpoints for processing user messages through the
    coaching chatbot. Business logic lives in the coach_service;
    views are thin request/response handlers.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.coach"
    verbose_name = "Coach"
