from apps.chat_messages.models import ChatMessage
from apps.users.models import User
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def get_previous_coach_message(user: User, user_msg: ChatMessage) -> ChatMessage:
    """
    For a given `user` message, fetches the `coach` message preceding it
    """
    prev = (
        ChatMessage.objects.filter(
            user=user, role="coach", timestamp__lt=user_msg.timestamp
        )
        .order_by("-timestamp")
        .first()
    )
    log.info(f"Previous Message: {prev}")
    return prev
