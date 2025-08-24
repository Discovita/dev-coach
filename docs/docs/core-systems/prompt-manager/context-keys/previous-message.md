---
sidebar_position: 17
---

# Previous Message

The `previous_message` context key provides the content of the previous coach message before the latest user message.

## Context Key Details

**Key Name**: `previous_message`  
**Enum Value**: `ContextKey.PREVIOUS_MESSAGE`  
**Data Source**: ChatMessage model  
**Return Type**: `str`

## What Data It Provides

Returns the content of the most recent coach message that occurred before the latest user message, or `None` if no such message exists.

## How It Gets the Data

The function finds the latest user message, then queries for the most recent coach message with a timestamp before that user message.

## Example Data

```python
# Example return values
"Let's explore your identity as a Creator. What does that mean to you?"  # Previous coach message
"Great! Now let's move on to the next identity category."              # Previous coach message
None  # No previous coach message exists
```

## Implementation

```python
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
```
