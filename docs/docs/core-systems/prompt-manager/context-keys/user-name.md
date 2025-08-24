---
sidebar_position: 2
---

# User Name

The `user_name` context key provides the user's name for personalization in prompts.

## Context Key Details

**Key Name**: `user_name`  
**Enum Value**: `ContextKey.USER_NAME`  
**Data Source**: User model  
**Return Type**: `str`

## What Data It Provides

Returns the user's full name if available, otherwise falls back to their email address.

## How It Gets the Data

The function accesses the user through the `CoachState` and calls Django's `get_full_name()` method, which combines `first_name` and `last_name` fields. If no full name is set, it returns the user's email address.

## Example Data

```python
# Example return values
"John Smith"  # if first_name="John" and last_name="Smith"
"jane@example.com"  # if no full name is set
```

## Implementation

```python
def get_user_name_context(coach_state: CoachState) -> str:
    """
    Get the user's name context.
    """
    user = coach_state.user
    return user.get_full_name() or user.email
```
