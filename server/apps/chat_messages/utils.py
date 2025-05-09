from apps.chat_messages.models import ChatMessage
from enums.message_role import MessageRole
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def add_chat_message(user: User, content: str, role: MessageRole) -> ChatMessage:
    """
    Async: Add a new message to the chat history for the given user.
    Args:
        user: The User instance the message belongs to.
        content: The text content of the message.
        role: The role of the sender (MessageRole.USER or MessageRole.COACH).
    Returns:
        The created ChatMessage instance.
    """
    return ChatMessage.objects.create(
        user=user,
        content=content,
        role=role,
    )
