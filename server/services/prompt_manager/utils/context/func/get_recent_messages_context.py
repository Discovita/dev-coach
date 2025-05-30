from typing import List
from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage


def get_recent_messages_context(coach_state: CoachState, num_messages: int = 5) -> str:
    """
    Retrieves the most recent chat messages for the user associated with the given coach_state.
    Formats these messages into a markdown-friendly string, with a heading.

    Output format:
    ## Recent conversation
    **Role:**
    Content
    ...
    """
    user = coach_state.user
    recent_messages: List[ChatMessage] = user.chat_messages.all().order_by(
        "-timestamp"
    )[:num_messages]
    formatted_messages = []
    for msg in reversed(recent_messages):
        formatted_messages.append(f"**{msg.role.capitalize()}:**\n{msg.content}")
    messages_block = "\n".join(formatted_messages)
    return f"## Recent conversation\n\n{messages_block}\n"
