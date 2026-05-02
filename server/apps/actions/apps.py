from django.apps import AppConfig


class ActionsConfig(AppConfig):
    """
    Configuration for the actions app.

    The actions app records coach-triggered actions as an audit trail.
    Action rows are created by the action_handler service and read
    through UserViewSet / TestUserViewSet.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.actions"
    verbose_name = "Actions"
