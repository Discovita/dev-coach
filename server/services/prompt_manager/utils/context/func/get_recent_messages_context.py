from typing import List

from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from apps.coach_states.models import Break, CoachState

# Local import to avoid a circular dependency:
# `apps.coach.utils.__init__` imports `build_coach_prompt`, which imports
# `services.prompt_manager.manager`, which transitively imports this module.
# Defer the import to the function body.



def get_recent_messages_context(coach_state: CoachState, num_messages: int = 10) -> str:
    """
    Retrieves the most recent chat messages for the user associated with the
    given coach_state and renders them into a markdown block suitable for
    inclusion in the coach prompt.

    Component-bearing rows (SESSION_VIDEO, SESSION_BREAK — added by Coaching
    Phase Videos) are rendered into bracketed narrative descriptions so the
    LLM has continuity across server-injected boundaries even though it
    never sees video/break events as actions. See
    `serialize_chat_message_for_prompt` for the format.

    Also includes all actions taken by the coach that occurred between
    messages to provide timeline context.

    Default `num_messages` was raised from 5 → 10 in PR 11 because a single
    session boundary can fill several slots with video/break/intro bubbles.

    Output format:
    ## Recent conversation
    **Role:**
    Content
    [Bracketed component narration on a new line if the row carries one]
    **Action:**
    [Action description with details]
    ...
    """
    from apps.coach.utils.serialize_chat_message_for_prompt import (
        serialize_chat_message_for_prompt,
    )

    user = coach_state.user
    recent_messages: List[ChatMessage] = list(
        user.chat_messages.all().order_by("-timestamp")[:num_messages]
    )

    shown_videos = set(coach_state.shown_videos or [])
    message_ids = [m.id for m in recent_messages]
    breaks_by_message_id = {
        b.coach_message_id: b
        for b in Break.objects.filter(coach_message_id__in=message_ids)
    }

    # Get all actions for this user that are linked to recent messages
    recent_actions: List[Action] = (
        Action.objects.filter(user=user, coach_message__id__in=message_ids)
        .select_related("coach_message")
        .order_by("timestamp")
    )

    # Create a timeline of events (messages and actions)
    timeline_events = []

    # Add messages to timeline
    for msg in recent_messages:
        timeline_events.append(
            {"type": "message", "timestamp": msg.timestamp, "data": msg}
        )

    # Add actions to timeline - place them right after their triggering message
    for action in recent_actions:
        # Use action timestamp, but if it's very close to the message timestamp,
        # we'll place it after the message in the timeline
        timeline_events.append(
            {
                "type": "action",
                "timestamp": action.timestamp,
                "data": action,
                "message_id": action.coach_message.id,  # For sorting purposes
            }
        )

    # Sort timeline by timestamp (oldest first), and for actions, place them after their message
    timeline_events.sort(key=lambda x: (x["timestamp"], x.get("type") == "action"))

    # Format the timeline events
    formatted_messages = []
    for event in timeline_events:
        if event["type"] == "message":
            msg = event["data"]
            rendered = serialize_chat_message_for_prompt(
                msg, shown_videos, breaks_by_message_id
            )
            formatted_messages.append(f"**{msg.role.capitalize()}:**\n{rendered}")
        elif event["type"] == "action":
            action = event["data"]
            action_description = _format_action_description(action)
            formatted_messages.append(f"**Action:**\n{action_description}")

    messages_block = "\n".join(formatted_messages)
    return f"## Recent conversation\n\n{messages_block}\n"


def _format_action_description(action: Action) -> str:
    """
    Format an action into a human-readable description.
    Provides a fallback if the result_summary isn't available for whatever reason
    """
    if action.result_summary:
        return action.result_summary

    action_type = action.action_type
    return f"Performed {action_type.replace('_', ' ')} action"
