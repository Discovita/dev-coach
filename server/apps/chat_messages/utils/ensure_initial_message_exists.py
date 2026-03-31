"""
Ensure a user's chat history starts with the initial welcome message.

Used by:
    - apps.users.views.user_viewset.UserViewSet (me endpoint)
    - apps.users.views.test_user_viewset.TestUserViewSet (detail endpoint)
    - apps.users.functions.public.get_user_chat_messages
    - apps.users.functions.public.reset_user_coaching_data
    - apps.coach.services.coach_service.functions.process_message
"""

from apps.chat_messages.constants import INITIAL_MESSAGE
from apps.chat_messages.models import ChatMessage
from apps.chat_messages.utils.add_chat_message import add_chat_message
from apps.users.models import User
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
    """
    if ChatMessage.objects.filter(user=user).exists():
        return False

    if INITIAL_MESSAGE:
        add_chat_message(user, INITIAL_MESSAGE, MessageRole.COACH)
        return True

    return False
