from django.apps import AppConfig


class ChatMessagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.chat_messages"

    def ready(self):
        import apps.chat_messages.signals  # noqa
