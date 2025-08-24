---
sidebar_position: 11
---

# Visualization Identities

The `visualization_identities` context key provides identities that still need visualization.

## Context Key Details

**Key Name**: `visualization_identities`  
**Enum Value**: `ContextKey.VISUALIZATION_IDENTITIES`  
**Data Source**: Identity model  
**Return Type**: `str`

## What Data It Provides

Returns identities that are NOT visualization_complete, formatted as markdown text, or a message indicating it's time to move to the next phase.

## How It Gets the Data

The function filters identities to exclude those with `VISUALIZATION_COMPLETE` state and formats them using the `format_identities` utility.

## Example Data

```python
# Example return values
"## Identities\n\n### Passions & Talents\n- **Creator**: Someone who brings ideas to life through artistic expression\n- **Helper**: Someone who supports others in achieving their goals"

"No more identities left to visualize - time to move to the next phase!"
```

## Implementation

```python
def get_visualization_identities_context(coach_state: CoachState) -> str:
    """
    Get the User's Identities that are NOT visualization_complete and format them for insertion into a prompt.
    This provides a "to do" list of identities that still need visualization.
    Each Identity is formatted into a markdown-compatible string.
    If no identities remain to be visualized, returns instructions to move to the next phase.
    """
    user = coach_state.user
    # Filter to only show identities that are NOT visualization_complete
    identities: List[Identity] = user.identities.exclude(state=IdentityState.VISUALIZATION_COMPLETE)

    # Check if there are any identities left to visualize
    if identities.count() == 0:
        return "No more identities left to visualize - time to move to the next phase!"
    
    return format_identities(identities)
```
