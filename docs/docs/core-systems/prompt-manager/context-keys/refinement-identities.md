---
sidebar_position: 9
---

# Refinement Identities

The `refinement_identities` context key provides identities that still need refinement.

## Context Key Details

**Key Name**: `refinement_identities`  
**Enum Value**: `ContextKey.REFINEMENT_IDENTITIES`  
**Data Source**: Identity model  
**Return Type**: `str`

## What Data It Provides

Returns identities that are NOT refinement_complete, formatted as a numbered list with chronological ordering instructions, or a message indicating it's time to move to the next phase.

## How It Gets the Data

The function filters identities to exclude those with `REFINEMENT_COMPLETE` state, sorts them by creation date (oldest first), and formats them using the `format_identities_needing_refinement` utility.

The formatting utility creates a numbered list with:
- A clear heading "## Identities Needing Refinement"
- Important instructions about chronological ordering
- Numbered list of identities with their category display names
- Emphasis that identities must be refined in the exact order shown

## Example Data

```python
# Example return values
"## Identities Needing Refinement\n\n**IMPORTANT: These identities are listed in chronological order (oldest first) and MUST be refined in the exact order shown. Always work from the top of the list to the bottom.**\n\n1. **Creator** (Passions & Talents)\n2. **Helper** (Passions & Talents)\n3. **Connector** (Maker of Money)"

"No more identities left to refine - time to move to the next phase!"
```

## Implementation

```python
def get_refinement_identities_context(coach_state: CoachState) -> str:
    """
    Get the User's Identities that are NOT refinement_complete and format them for insertion into a prompt.
    This provides a "to do" list of identities that still need refinement.
    Each Identity is formatted into a markdown-compatible string.
    If no identities remain to be refined, returns instructions to move to the next phase.
    """
    user = coach_state.user
    # Filter to only show identities that are NOT refinement_complete, sorted by oldest first
    identities: List[Identity] = user.identities.exclude(state=IdentityState.REFINEMENT_COMPLETE).order_by('created_at')

    # Check if there are any identities left to refine
    if identities.count() == 0:
        return "No more identities left to refine - time to move to the next phase!"
    
    return format_identities_needing_refinement(identities)
```
