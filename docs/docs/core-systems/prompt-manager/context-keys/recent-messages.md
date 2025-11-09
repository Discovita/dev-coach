---
sidebar_position: 18
---

# Recent Messages

The `recent_messages` context key provides a timeline of recent conversation messages and actions.

## Context Key Details

**Key Name**: `recent_messages`  
**Enum Value**: `ContextKey.RECENT_MESSAGES`  
**Data Source**: ChatMessage model  
**Return Type**: `str`

## What Data It Provides

Returns a markdown-formatted timeline of recent messages and actions, including both user and coach messages along with any actions taken by the coach.

## How It Gets the Data

The function retrieves the most recent messages (default 5), finds associated actions, creates a chronological timeline, and formats everything into a markdown section.

## Example Data

```python
# Example return values
"## Recent conversation\n\n**User:**\nI'm feeling stuck with my career transition\n**Coach:**\nLet's explore your identity as a Creator. What does that mean to you?\n**Action:**\nCreated new identity 'Creator' in Passions & Talents category\n**User:**\nI think being a Creator means bringing ideas to life\n**Coach:**\nThat's beautiful! How does that Creator energy show up in your work?"

"## Recent conversation\n\n**User:**\nCan you help me with identity brainstorming?\n**Coach:**\nAbsolutely! Let's start with your Passions & Talents. What activities make you lose track of time?"
```

## Implementation

```python
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
    recent_messages: List[ChatMessage] = user.chat_messages.all().order_by("-timestamp")[:num_messages]

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
        timeline_events.append({"type": "message", "timestamp": msg.timestamp, "data": msg})

    # Add actions to timeline - place them right after their triggering message
    for action in recent_actions:
        # Use action timestamp, but if it's very close to the message timestamp,
        # we'll place it after the message in the timeline
        timeline_events.append({
            "type": "action",
            "timestamp": action.timestamp,
            "data": action,
            "message_id": action.coach_message.id,  # For sorting purposes
        })

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
```
