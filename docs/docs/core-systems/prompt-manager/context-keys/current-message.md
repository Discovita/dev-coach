---
sidebar_position: 16
---

# Current Message

The `current_message` context key provides the content of the latest user message.

## Context Key Details

**Key Name**: `current_message`  
**Enum Value**: `ContextKey.CURRENT_MESSAGE`  
**Data Source**: ChatMessage model  
**Return Type**: `str`

## What Data It Provides

Returns the content of the most recent user message, or `None` if no user messages exist.

## How It Gets the Data

The function queries the ChatMessage model for the latest message with role "user" for the current user.

## Example Data

```python
# Example return values
"I'm feeling stuck with my career transition"  # Latest user message
"Can you help me with identity brainstorming?"  # Latest user message
None  # No user messages exist
```

## Implementation

```python
def get_current_message_context(coach_state: CoachState) -> str:
    """
    Returns the content of the latest USER message for the user.
    """
    msg = ChatMessage.objects.filter(user=coach_state.user, role="user").order_by("-timestamp").first()
    return msg.content if msg else None
```
