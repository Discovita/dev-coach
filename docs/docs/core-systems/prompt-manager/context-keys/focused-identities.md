---
sidebar_position: 8
---

# Focused Identities

The `focused_identities` context key provides identities that match the current identity focus category.

## Context Key Details

**Key Name**: `focused_identities`  
**Enum Value**: `ContextKey.FOCUSED_IDENTITIES`  
**Data Source**: Identity model  
**Return Type**: `str`

## What Data It Provides

Returns identities that match the current `identity_focus` category, formatted as markdown text, or a message indicating no identities found or category was skipped.

## How It Gets the Data

The function filters the user's identities by the current focus category and formats them using the `format_identities` utility. It handles cases where the category was skipped or no identities exist.

## Example Data

```python
# Example return values
"## Identities\n\n### Passions & Talents\n- **Creator**: Someone who brings ideas to life through artistic expression\n- **Helper**: Someone who supports others in achieving their goals"

"No identities found for focus: Passions & Talents"

"The category 'Physical Expression' was skipped."

"No identity focus set."
```

## Implementation

```python
def get_focused_identities_context(coach_state: CoachState) -> str:
    """
    Return the user's identities that match the current identity_focus (category).
    If the category is in skipped categories and there are no identities, return a skipped message.
    """
    user = coach_state.user
    identities: List[Identity] = user.identities.all()
    focus = coach_state.identity_focus
    if not focus:
        return "No identity focus set."
    try:
        focus_category = IdentityCategory.from_string(focus)
    except Exception:
        return f"Invalid identity focus: {focus}"
    focused = [i for i in identities if i.category == focus_category.value]
    skipped = coach_state.skipped_identity_categories or []
    if not focused:
        if focus_category.value in skipped:
            return f"The category '{focus_category.label}' was skipped."
        return f"No identities found for focus: {focus_category.label}"
    return format_identities(focused)
```
