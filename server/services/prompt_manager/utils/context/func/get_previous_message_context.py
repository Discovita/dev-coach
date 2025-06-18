from apps.chat_messages.models import ChatMessage
from apps.coach_states.models import CoachState

def get_previous_message_context(coach_state: CoachState) -> str:
    """
    Returns the content of the previous COACH message before the latest USER message for the user.
    """
    user_msg = ChatMessage.objects.filter(user=coach_state.user, role="user").order_by("-timestamp").first()
    if not user_msg:
        return None
    prev_msg = ChatMessage.objects.filter(
        user=coach_state.user, role="coach", timestamp__lt=user_msg.timestamp
    ).order_by("-timestamp").first()
    return prev_msg.content if prev_msg else None 