import os
from apps.chat_messages.models import ChatMessage
from enums.message_role import MessageRole
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def add_chat_message(user: User, content: str, role: MessageRole) -> ChatMessage:
    """
    Async: Add a new message to the chat history for the given user.
    """
    return ChatMessage.objects.create(
        user=user,
        content=content,
        role=role,
    )


def get_initial_message() -> str:
    """
    Get the initial bot message for the chat.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    initial_message_path = os.path.join(current_dir, "initial_message.md")
    try:
        with open(initial_message_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        log.error(
            f"Failed to read initial bot message from {initial_message_path}: {e}"
        )
        return ""
