"""
Utility to add the coach's response to the chat history.

After the AI generates a response, we need to save it to the chat history
so it becomes part of the permanent conversation record.
"""
from apps.chat_messages.models import ChatMessage
from apps.chat_messages.utils import add_chat_message
from apps.users.models import User
from enums.message_role import MessageRole


def add_coach_message_to_history(user: User, coach_message: str) -> ChatMessage:
    """
    Add the coach's response message to the user's chat history.

    This saves the coach's response so it becomes part of the conversation
    history that can be referenced in future interactions.

    Args:
        user: The user receiving the coach's message
        coach_message: The message content from the coach

    Returns:
        The ChatMessage object that was created and saved
    """
    return add_chat_message(user, coach_message, MessageRole.COACH)

