"""
Create a chat message record.

Used by:
    - apps.coach.services.coach_service.functions.process_message
    - apps.coach.services.coach_service.utils.add_coach_message_to_history
    - apps.chat_messages.utils.ensure_initial_message_exists
"""

from apps.chat_messages.models import ChatMessage
from apps.users.models import User
from enums.message_role import MessageRole


def add_chat_message(user: User, content: str, role: MessageRole) -> ChatMessage:
    """
    Add a new message to the chat history for the given user.

    Args:
        user: The user this message belongs to.
        content: The message text.
        role: The role of the sender (USER or COACH).

    Returns:
        The newly created ChatMessage instance.
    """
    return ChatMessage.objects.create(
        user=user,
        content=content,
        role=role,
    )
