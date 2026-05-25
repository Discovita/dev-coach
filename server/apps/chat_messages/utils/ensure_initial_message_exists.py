"""
Ensure a user's chat history starts with the initial welcome message.

Used by:
    - apps.users.views.user_viewset.UserViewSet (me endpoint)
    - apps.users.views.test_user_viewset.TestUserViewSet (detail endpoint)
    - apps.users.functions.public.get_user_chat_messages
    - apps.users.functions.public.reset_user_coaching_data
    - apps.coach.functions.public.process_message
"""

from django.conf import settings

from apps.chat_messages.constants import INITIAL_MESSAGE
from apps.chat_messages.models import ChatMessage
from apps.chat_messages.utils.add_chat_message import add_chat_message
from apps.users.models import User
from enums.message_role import MessageRole
from enums.component_type import ComponentType
from models.components.ComponentConfig import ComponentConfig

WELCOME_VIDEO_KEY = "welcome_session_intro"


def ensure_initial_message_exists(user: User) -> bool:
    """
    Ensure the user has at least the initial bot message in their chat history.

    If the user already has any chat messages, returns False (no-op).

    When `settings.COACHING_PHASE_VIDEOS_ENABLED` is True, seeds a coach
    message with `content=""` carrying a SESSION_VIDEO(welcome_session_intro)
    component_config. The LLM speaks for the first time only after the user
    clicks Continue on the welcome video.

    When the flag is False, preserves today's behavior: seed the
    `INITIAL_MESSAGE` text (the constant lives in
    `apps.chat_messages.constants.initial_messages` — PR 24 deletes it).

    Returns:
        True if a message was added, False otherwise.
    """
    if ChatMessage.objects.filter(user=user).exists():
        return False

    if settings.COACHING_PHASE_VIDEOS_ENABLED:
        component_config = ComponentConfig(
            component_type=ComponentType.SESSION_VIDEO.value,
            video_key=WELCOME_VIDEO_KEY,
        )
        message = add_chat_message(user, "", MessageRole.COACH)
        message.component_config = component_config.model_dump()
        message.save(update_fields=["component_config"])
        return True

    if INITIAL_MESSAGE:
        add_chat_message(user, INITIAL_MESSAGE, MessageRole.COACH)
        return True

    return False
