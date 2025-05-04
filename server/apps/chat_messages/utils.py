from apps.chat_messages.models import ChatMessage
from enums.message_role import MessageRole
from apps.users.models import User


async def add_chat_message_async(user: User, content: str, role: MessageRole) -> ChatMessage:
    """
    Async: Add a new message to the chat history for the given user.
    Args:
        user: The User instance the message belongs to.
        content: The text content of the message.
        role: The role of the sender (MessageRole.USER or MessageRole.COACH).
    Returns:
        The created ChatMessage instance.
    """
    return await ChatMessage.objects.acreate(
        user=user,
        content=content,
        role=role,
    )
