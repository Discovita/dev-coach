---
sidebar_position: 6
---

# Identity Focus

The `identity_focus` context key provides the currently focused identity category as a human-readable label.

## Context Key Details

**Key Name**: `identity_focus`  
**Enum Value**: `ContextKey.IDENTITY_FOCUS`  
**Data Source**: CoachState  
**Return Type**: `str`

## What Data It Provides

Returns the human-readable label of the currently focused identity category, or an empty string if no focus is set.

## How It Gets the Data

The function retrieves the `identity_focus` value from the coach state and converts it to a human-readable label using the `IdentityCategory` enum.

## Example Data

```python
# Example return values
"Passions & Talents"  # Current focus category
"Maker of Money"      # Current focus category
""                    # No focus set
"Invalid Category"    # Fallback for invalid values
```

## Implementation

```python
def get_identity_focus_context(coach_state: CoachState) -> str:
    """
    Get the user's identity focus context as a human-readable label.
    This function retrieves the identity_focus value from the coach_state,
    converts it to an IdentityCategory enum member, and returns its label.
    """
    identity_focus_value = coach_state.identity_focus
    if identity_focus_value:
        try:
            identity_category_member = IdentityCategory.from_string(identity_focus_value)
            return identity_category_member.label
        except ValueError:
            return identity_focus_value
    return ""
```
