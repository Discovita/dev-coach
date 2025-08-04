from typing import List
from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from datetime import datetime


def get_recent_messages_context(coach_state: CoachState, num_messages: int = 5) -> str:
    """
    Retrieves the most recent chat messages for the user associated with the given coach_state.
    Also includes all actions taken by the coach that occurred between messages to provide timeline context.
    Formats these messages into a markdown-friendly string, with a heading.

    Output format:
    ## Recent conversation
    **Role:**
    Content
    **Action:**
    [Action description with details]
    ...
    """
    user = coach_state.user
    recent_messages: List[ChatMessage] = user.chat_messages.all().order_by(
        "-timestamp"
    )[:num_messages]

    # Get all actions for this user that are linked to recent messages
    recent_message_ids = [msg.id for msg in recent_messages]
    recent_actions: List[Action] = (
        Action.objects.filter(user=user, coach_message__id__in=recent_message_ids)
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
            formatted_messages.append(f"**{msg.role.capitalize()}:**\n{msg.content}")
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
