"""
Utility to add a user's message to their chat history.

This function records what the user said so it becomes part of the conversation
history that the coach can reference in future responses.
"""
from apps.chat_messages.models import ChatMessage
from apps.chat_messages.utils import add_chat_message
from apps.users.models import User
from enums.message_role import MessageRole


def add_user_message_to_history(user: User, message: str) -> ChatMessage:
    """
    Add the user's message to their chat history.

    Args:
        user: The user who sent the message
        message: The message content the user wants to send to the coach

    Returns:
        The ChatMessage object that was created and saved
    """
    return add_chat_message(user, message, MessageRole.USER)

