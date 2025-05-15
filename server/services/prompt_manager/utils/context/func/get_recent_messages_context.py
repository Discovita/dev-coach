from typing import List
from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage


def get_recent_messages_context(coach_state: CoachState) -> str:
    """
    Retrieves the 5 most recent chat messages for the user associated with the given coach_state.
    Formats these messages into a markdown-friendly string.

    Each message is formatted as:
    **Role:**
    Content
    """
    user = coach_state.user
    recent_messages: List[ChatMessage] = user.chat_messages.all().order_by("-timestamp")[:5]
    formatted_messages = []
    for msg in reversed(recent_messages):
        formatted_messages.append(f"**{msg.role.capitalize()}:**\n{msg.content}")
    return "\n".join(formatted_messages)

