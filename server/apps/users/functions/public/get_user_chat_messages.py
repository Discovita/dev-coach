"""
Get user chat messages with initial message handling.

This function retrieves chat messages for a user, ensuring the initial
bot message exists if the chat history is empty.
"""

from typing import List

from apps.users.models import User
from apps.chat_messages.models import ChatMessage
from apps.users.utils import ensure_initial_message_exists


def get_user_chat_messages(user: User) -> List[ChatMessage]:
    """
    Get chat messages for a user in chronological order.

    If the chat history is empty, adds the initial bot message first.

    Args:
        user: The user whose chat messages to retrieve

    Returns:
        List of ChatMessage objects in chronological order (oldest first)

    Example:
        >>> messages = get_user_chat_messages(user)
        >>> for msg in messages:
        ...     print(f"{msg.role}: {msg.content}")
    """
    # Ensure initial message exists if chat is empty
    ensure_initial_message_exists(user)

    # Get messages ordered by timestamp (newest first from DB)
    chat_messages_qs = ChatMessage.objects.filter(user=user).order_by("-timestamp")

    # Return in chronological order (oldest first)
    return list(reversed(chat_messages_qs))

