---
sidebar_position: 12
---

# Current Phase

The `current_phase` context key provides the current coaching phase for the user.

## Context Key Details

**Key Name**: `current_phase`  
**Enum Value**: `ContextKey.CURRENT_PHASE`  
**Data Source**: CoachState  
**Return Type**: `str`

## What Data It Provides

Returns the current coaching phase as a string value from the coach state.

## How It Gets the Data

The function directly returns the `current_phase` field from the coach state.

## Example Data

```python
# Example return values
"identity_brainstorming"  # Current phase
"identity_refinement"     # Current phase
"i_am_statement"    # Current phase
"identity_visualization"  # Current phase
"get_to_know_you"        # Current phase
```

## Implementation

```python
def get_current_phase_context(coach_state: CoachState) -> str:
    """
    Returns the current coaching phase for the user as a string.
    """
    return coach_state.current_phase
```
