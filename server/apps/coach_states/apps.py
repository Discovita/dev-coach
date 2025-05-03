from django.apps import AppConfig


class CoachStatesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.coach_states"

    def ready(self):
        import apps.coach_states.signals  # noqa
