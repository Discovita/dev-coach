---
sidebar_position: 13
---

# Who You Are

The `who_you_are` context key provides the user's self-description identities.

## Context Key Details

**Key Name**: `who_you_are`  
**Enum Value**: `ContextKey.WHO_YOU_ARE`  
**Data Source**: CoachState  
**Return Type**: `str`

## What Data It Provides

Returns the user's "Who You Are" identities as a comma-separated string, or a message indicating no identities are defined yet.

## How It Gets the Data

The function retrieves the `who_you_are` list from the coach state and joins the values with commas.

## Example Data

```python
# Example return values
"Creative, Caring, Determined"  # Multiple identities
"Problem Solver"               # Single identity
"No Who You Are identities defined yet."  # No identities set
```

## Implementation

```python
def get_who_you_are(coach_state: CoachState) -> str:
    """
    Get the user's "Who You Are" identities as a comma-separated string.
    """
    who_you_are = coach_state.who_you_are
    if not who_you_are:
        return "No Who You Are identities defined yet."
    return ", ".join(who_you_are)
```
