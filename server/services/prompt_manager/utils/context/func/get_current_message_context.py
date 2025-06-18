from apps.chat_messages.models import ChatMessage
from apps.coach_states.models import CoachState

def get_current_message_context(coach_state: CoachState) -> str:
    """
    Returns the content of the latest USER message for the user.
    """
    msg = ChatMessage.objects.filter(user=coach_state.user, role="user").order_by("-timestamp").first()
    return msg.content if msg else None 