---
sidebar_position: 10
---

# Affirmation Identities

The `affirmation_identities` context key provides identities that still need affirmation.

## Context Key Details

**Key Name**: `affirmation_identities`  
**Enum Value**: `ContextKey.AFFIRMATION_IDENTITIES`  
**Data Source**: Identity model  
**Return Type**: `str`

## What Data It Provides

Returns identities that are NOT affirmation_complete, formatted as markdown text, or a message indicating it's time to move to the next phase.

## How It Gets the Data

The function filters identities to exclude those with `AFFIRMATION_COMPLETE` state and formats them using the `format_identities` utility.

## Example Data

```python
# Example return values
"## Identities\n\n### Passions & Talents\n- **Creator**: Someone who brings ideas to life through artistic expression\n- **Helper**: Someone who supports others in achieving their goals"

"No more identities left to affirm - time to move to the Identity Visualization phase"
```

## Implementation

```python
def get_affirmation_identities_context(coach_state: CoachState) -> str:
    """
    Get the User's Identities that are NOT affirmation_complete and format them for insertion into a prompt.
    This provides a "to do" list of identities that still need affirmation.
    Each Identity is formatted into a markdown-compatible string.
    If no identities remain to be affirmed, returns instructions to move to the next phase.
    """
    user = coach_state.user
    # Filter to only show identities that are NOT affirmation_complete
    identities: List[Identity] = user.identities.exclude(state=IdentityState.AFFIRMATION_COMPLETE)

    # Check if there are any identities left to affirm
    if identities.count() == 0:
        return "No more identities left to affirm - time to move to the Identity Visualization phase"
    
    return format_identities(identities)
```
