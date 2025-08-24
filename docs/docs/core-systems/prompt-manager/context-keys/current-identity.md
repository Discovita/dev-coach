---
sidebar_position: 7
---

# Current Identity

The `current_identity` context key provides detailed information about the identity currently being refined.

## Context Key Details

**Key Name**: `current_identity`  
**Enum Value**: `ContextKey.CURRENT_IDENTITY`  
**Data Source**: CoachState  
**Return Type**: `str`

## What Data It Provides

Returns detailed markdown-formatted information about the current identity including name, ID, state, category, and notes, or `None` if no current identity is set.

## How It Gets the Data

The function retrieves the `current_identity` from the coach state and formats it into a detailed markdown section with all identity properties.

## Example Data

```python
# Example return values
"#### Creator\n**ID:** 123\n**State:** refinement_in_progress\n**Category:** passions_and_talents\n**Notes:**\n- Working on creative projects\n- Building confidence in artistic expression"

None  # No current identity set
```

## Implementation

```python
def get_current_identity_context(coach_state: CoachState) -> str:
    """
    Get the current identity being refined in the Identity Refinement Phase.
    Returns the name of the current identity if one is set, otherwise returns None.
    """
    identity = coach_state.current_identity
    if identity:
        current_identity_str = f"#### {identity.name}\n"
        current_identity_str += f"**ID:** {identity.id}\n"
        current_identity_str += f"**State:** {identity.state if identity.state else 'None'}\n"
        current_identity_str += f"**Category:** {identity.category if identity.category else 'None'}\n"
        if identity.notes:
            notes_str = "\n".join([f"- {note}" for note in identity.notes])
            current_identity_str += f"**Notes:**\n{notes_str}\n"
        return current_identity_str
    return None
```
