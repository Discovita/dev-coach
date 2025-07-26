from typing import List
from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.identities.models import Identity
from datetime import datetime


def get_recent_messages_context(coach_state: CoachState, num_messages: int = 5) -> str:
    """
    Retrieves the most recent chat messages for the user associated with the given coach_state.
    Also includes identity creation actions that occurred between messages to provide timeline context.
    Formats these messages into a markdown-friendly string, with a heading.

    Output format:
    ## Recent conversation
    **Role:**
    Content
    **Action:**
    Created identity: "[Identity Name]" in [Category] category
    ...
    """
    user = coach_state.user
    recent_messages: List[ChatMessage] = user.chat_messages.all().order_by(
        "-timestamp"
    )[:num_messages]
    
    # Get all user identities
    user_identities: List[Identity] = user.identities.all().order_by("created_at")
    
    # Create a timeline of events (messages and identity creations)
    timeline_events = []
    
    # Add messages to timeline
    for msg in recent_messages:
        timeline_events.append({
            'type': 'message',
            'timestamp': msg.timestamp,
            'data': msg
        })
    
    # Add identity creation events to timeline
    for identity in user_identities:
        timeline_events.append({
            'type': 'identity_creation',
            'timestamp': identity.created_at,
            'data': identity
        })
    
    # Sort timeline by timestamp (oldest first)
    timeline_events.sort(key=lambda x: x['timestamp'])
    
    # Filter to only include events that are within the time range of recent messages
    if timeline_events:
        # Get the earliest timestamp from recent messages
        earliest_message_time = min(msg.timestamp for msg in recent_messages)
        
        # Only include events that happened after or at the same time as the earliest message
        filtered_events = [
            event for event in timeline_events 
            if event['timestamp'] >= earliest_message_time
        ]
    else:
        filtered_events = []
    
    # Format the timeline events
    formatted_messages = []
    for event in filtered_events:
        if event['type'] == 'message':
            msg = event['data']
            formatted_messages.append(f"**{msg.role.capitalize()}:**\n{msg.content}")
        elif event['type'] == 'identity_creation':
            identity = event['data']
            formatted_messages.append(
                f"**Action:**\nCreated identity: \"{identity.name}\" in {identity.get_category_display()} category (ID: {identity.id})"
            )
    
    messages_block = "\n".join(formatted_messages)
    return f"## Recent conversation\n\n{messages_block}\n"
