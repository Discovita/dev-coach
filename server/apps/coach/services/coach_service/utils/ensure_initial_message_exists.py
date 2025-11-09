"""
Utility to ensure a user's chat history starts with an initial welcome message.

This function checks if the user has any chat messages. If they don't have any,
it adds the initial welcome message from the coach to start the conversation.
"""
from apps.chat_messages.models import ChatMessage
from apps.chat_messages.utils import add_chat_message, get_initial_message
from apps.users.models import User
from enums.message_role import MessageRole


def ensure_initial_message_exists(user: User) -> None:
    """
    Ensure the user's chat history contains an initial welcome message.

    If the user has no chat messages, this adds the initial welcome message
    from the coach to start their conversation.

    Args:
        user: The user whose chat history should be initialized
    """
    has_chat_history = ChatMessage.objects.filter(user=user).exists()
    if not has_chat_history:
        initial_message = get_initial_message()
        if initial_message:
            add_chat_message(user, initial_message, MessageRole.COACH)

