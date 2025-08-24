---
sidebar_position: 14
---

# Who You Want to Be

The `who_you_want_to_be` context key provides the user's aspirational identities.

## Context Key Details

**Key Name**: `who_you_want_to_be`  
**Enum Value**: `ContextKey.WHO_YOU_WANT_TO_BE`  
**Data Source**: CoachState  
**Return Type**: `str`

## What Data It Provides

Returns the user's "Who You Want to Be" identities as a comma-separated string, or a message indicating no identities are defined yet.

## How It Gets the Data

The function retrieves the `who_you_want_to_be` list from the coach state and joins the values with commas.

## Example Data

```python
# Example return values
"Confident Leader, Inspiring Mentor, Successful Entrepreneur"  # Multiple identities
"Authentic Communicator"                                      # Single identity
"No Who You Want To Be identities defined yet."              # No identities set
```

## Implementation

```python
def get_who_you_want_to_be(coach_state: CoachState) -> str:
    """
    Get the user's "Who You Are" identities as a comma-separated string.
    """
    who_you_want_to_be = coach_state.who_you_want_to_be
    if not who_you_want_to_be:
        return "No Who You Want To Be identities defined yet."
    return ", ".join(who_you_want_to_be)
```
