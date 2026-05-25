"""
Build the LLM-facing chat history for the coach prompt.

Returns a list of serialized strings (oldest first) so the LLM sees both
plain message text and the bracketed narration for server-injected
components (session videos, breaks). See
`serialize_chat_message_for_prompt` for the narration format.

Default `count` is 10 (raised from 5 in PR 11) because a single session
boundary can fill several slots with video/break/intro bubbles; 5 left no
room for actual session content.
"""

from apps.chat_messages.models import ChatMessage
from apps.coach.utils.serialize_chat_message_for_prompt import (
    serialize_chat_message_for_prompt,
)
from apps.coach_states.models import Break
from apps.users.models import User


def get_recent_chat_messages_for_prompt(
    user: User, count: int = 10
) -> list[str]:
    """
    Return the most recent chat messages as LLM-facing strings.

    Component-bearing rows are rendered into bracketed narrative descriptions
    using `CoachState.shown_videos` and the `Break` table as sources of
    truth for acked/closed status. Plain text rows are returned unchanged.

    Args:
        user: The user whose chat history to read.
        count: How many messages to include (newest `count`, returned in
            chronological order oldest → newest).
    """
    recent_messages = list(
        ChatMessage.objects.filter(user=user).order_by("-timestamp")[:count]
    )
    recent_messages.reverse()  # oldest → newest

    if not recent_messages:
        return []

    shown_videos = set(getattr(user.coach_state, "shown_videos", None) or [])

    message_ids = [m.id for m in recent_messages]
    breaks_by_message_id = {
        b.coach_message_id: b
        for b in Break.objects.filter(coach_message_id__in=message_ids)
    }

    return [
        serialize_chat_message_for_prompt(m, shown_videos, breaks_by_message_id)
        for m in recent_messages
    ]
