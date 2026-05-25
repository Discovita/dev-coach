"""
LLM-facing serialization for ChatMessage rows.

Coaching Phase Videos relies on the LLM having narrative continuity across
session boundaries even though videos and breaks are server-injected and the
LLM has no awareness of them. Each `ChatMessage` row carrying a
`component_config` (SESSION_VIDEO, SESSION_BREAK) is rendered into a
bracketed description that the LLM reads as plain text in chat history. The
DB row is unchanged — only the LLM-facing string differs.

Sources of truth at serialization time:
- `CoachState.shown_videos`: which session videos the user has acknowledged.
- `Break` table: open vs closed status of break component rows.

Format conventions (taken verbatim from the spec):
- Acked video:   `[Showed user the "<video_name>" video. User watched it.]`
- Unacked video: `[Showed user the "<video_name>" video. User has not watched it yet.]`
- Closed break:  `[Offered user a break. User took it and returned when ready.]`
- Open break:    `[Offered user a break. User has not returned yet.]`

Coach messages that carry BOTH text and a component_config (the common case
for transition turns — LLM speaks + outro card attaches) are rendered with
the text first, then the bracket on a new line.
"""

from typing import Dict, Optional
from uuid import UUID

from apps.chat_messages.models import ChatMessage
from apps.coach_states.constants.session_videos import SESSION_VIDEOS
from apps.coach_states.models import Break
from enums.component_type import ComponentType


def serialize_chat_message_for_prompt(
    msg: ChatMessage,
    shown_videos: set[str],
    breaks_by_message_id: Dict[UUID, Break],
) -> str:
    """
    Return the LLM-facing string for one `ChatMessage`.

    Args:
        msg: The chat message to render.
        shown_videos: The user's current `CoachState.shown_videos` as a set
            for O(1) membership checks.
        breaks_by_message_id: Map of `ChatMessage.id` → `Break` row for
            messages anchoring a SESSION_BREAK component. Pre-fetched by the
            caller so this helper doesn't issue per-row queries. Messages
            without an entry are treated as not anchoring a break.
    """
    bracket = _render_component_bracket(msg, shown_videos, breaks_by_message_id)
    if not bracket:
        return msg.content
    if msg.content:
        return f"{msg.content}\n{bracket}"
    return bracket


def _render_component_bracket(
    msg: ChatMessage,
    shown_videos: set[str],
    breaks_by_message_id: Dict[UUID, Break],
) -> Optional[str]:
    """Return the bracketed component description, or None if no component."""
    cfg = msg.component_config
    if not cfg:
        return None

    component_type = cfg.get("component_type")

    if component_type == ComponentType.SESSION_VIDEO.value:
        video_key = cfg.get("video_key")
        if not video_key or video_key not in SESSION_VIDEOS:
            # Defensive: a SESSION_VIDEO row without a recognizable key
            # shouldn't crash the prompt. Skip the bracket entirely.
            return None
        video_name = SESSION_VIDEOS[video_key]["name"]
        if video_key in shown_videos:
            return f'[Showed user the "{video_name}" video. User watched it.]'
        return f'[Showed user the "{video_name}" video. User has not watched it yet.]'

    if component_type == ComponentType.SESSION_BREAK.value:
        break_row = breaks_by_message_id.get(msg.id)
        if break_row is not None and break_row.ended_at is None:
            return "[Offered user a break. User has not returned yet.]"
        return "[Offered user a break. User took it and returned when ready.]"

    # Other component types (combine identities, etc.) don't need bracket
    # narration — the LLM already knows about them via its own actions.
    return None
