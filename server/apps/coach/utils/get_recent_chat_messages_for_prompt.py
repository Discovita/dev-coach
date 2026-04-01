"""
Utility to get recent chat messages for prompt context.

The coach needs to see recent conversation history to maintain context
and provide coherent responses that follow the conversation flow.
"""

from apps.chat_messages.models import ChatMessage
from apps.users.models import User


def get_recent_chat_messages_for_prompt(
    user: User, count: int = 5
) -> list[ChatMessage]:
    """
    Get the most recent chat messages for use in the AI prompt.

    Returns:
        List of ChatMessage objects, ordered from oldest to newest
    """
    recent_messages = ChatMessage.objects.filter(user=user).order_by("-timestamp")[
        :count
    ]
    return list(reversed(recent_messages))
