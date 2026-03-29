from django.apps import AppConfig


class ChatMessagesConfig(AppConfig):
    """
    Configuration for the chat_messages app.

    Stores conversation history between users and the coaching chatbot.
    Connects a post_save signal that triggers asynchronous user notes
    extraction when a new user message is created.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.chat_messages"
    verbose_name = "Chat Messages"

    def ready(self):
        import apps.chat_messages.signals  # noqa
