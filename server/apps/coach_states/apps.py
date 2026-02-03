from django.apps import AppConfig


class CoachStatesConfig(AppConfig):
    """
    App configuration for CoachStates app.
    
    Registers signal handlers when the app is ready.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.coach_states"
    verbose_name = "Coach States"

    def ready(self):
        """Import signal handlers when the app is ready."""
        import apps.coach_states.signals  # noqa: F401
