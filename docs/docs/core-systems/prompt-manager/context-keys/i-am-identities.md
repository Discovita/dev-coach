---
sidebar_position: 10
---

# "I Am" Statements Identities

The `i_am_identities` context key provides identities that still need an "I Am" Statement.

## Context Key Details

**Key Name**: `i_am_identities`  
**Enum Value**: `ContextKey.I_AM_IDENTITIES`  
**Data Source**: Identity model  
**Return Type**: `str`

## What Data It Provides

Returns identities that are NOT i_am_complete, formatted as markdown text, or a message indicating it's time to move to the next phase.

## How It Gets the Data

The function filters identities to exclude those with `I_AM_COMPLETE` state and formats them using the `format_identities` utility.

## Example Data

```python
# Example return values
"## Identities\n\n### Passions & Talents\n- **Creator**: Someone who brings ideas to life through artistic expression\n- **Helper**: Someone who supports others in achieving their goals"

"No more identities left to create an 'I Am' Statement - time to move to the Identity Visualization phase"
```

## Implementation

```python
def get_i_am_identities_context(coach_state: CoachState) -> str:
    """
    Get the User's Identities that are NOT i_am_complete and format them for insertion into a prompt.
    This provides a "to do" list of identities that still need an "I Am" Statement.
    Each Identity is formatted into a markdown-compatible string.
    If no identities remain to create an "I Am" Statement, returns instructions to move to the next phase.
    """
    user = coach_state.user
    # Filter to only show identities that are NOT i_am_complete
    identities: List[Identity] = user.identities.exclude(state=IdentityState.I_AM_COMPLETE)

    # Check if there are any identities left to create an "I Am" Statement
    if identities.count() == 0:
        return "No more identities left to create an 'I Am' Statement - time to move to the Identity Visualization phase"
    
    return format_identities(identities)
```
