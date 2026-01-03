"""
Ensure initial chat message exists for a user.

This utility checks if a user has any chat messages and adds the initial
bot message if the chat history is empty.
"""

from apps.users.models import User
from apps.chat_messages.models import ChatMessage
from apps.chat_messages.utils import get_initial_message, add_chat_message
from enums.message_role import MessageRole


def ensure_initial_message_exists(user: User) -> bool:
    """
    Ensure the user has at least the initial bot message in their chat history.

    If the user has no chat messages, this function will add the initial
    bot message (if one is configured).

    Args:
        user: The user to check/update

    Returns:
        True if a message was added, False if chat already had messages
        or no initial message is configured

    Example:
        >>> added = ensure_initial_message_exists(user)
        >>> if added:
        ...     print("Initial message was added")
    """
    chat_messages = ChatMessage.objects.filter(user=user)

    if chat_messages.exists():
        return False

    initial_message = get_initial_message()
    if initial_message:
        add_chat_message(user, initial_message, MessageRole.COACH)
        return True

    return False

