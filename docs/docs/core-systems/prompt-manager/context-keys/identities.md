---
sidebar_position: 4
---

# Identities

The `identities` context key provides all of the user's identities formatted for prompt insertion.

## Context Key Details

**Key Name**: `identities`  
**Enum Value**: `ContextKey.IDENTITIES`  
**Data Source**: Identity model  
**Return Type**: `str`

## What Data It Provides

Returns all user identities formatted as markdown-compatible text, including a section listing any skipped identity categories.

## How It Gets the Data

The function retrieves all identities for the user and formats them using the `format_identities` utility. It also includes any skipped identity categories from the coach state.

## Example Data

```python
# Example return values
"## Identities\n\n### Passions & Talents\n- **Creator**: Someone who brings ideas to life through artistic expression\n- **Helper**: Someone who supports others in achieving their goals\n\n### Maker of Money\n- **Connector**: Someone who builds relationships that generate income\n\n## Skipped Categories\n- Physical Expression\n- Spiritual"

"## Identities\n\nNo identities created yet.\n"
```

## Implementation

```python
def get_identities_context(coach_state: CoachState) -> str:
    """
    Get the User's Identities and format them for insertion into a prompt.
    Each Identity is formatted into a markdown-compatible string.
    Also includes a section listing skipped identity categories (if any).
    """
    user = coach_state.user
    identities: List[Identity] = user.identities.all()
    skipped = coach_state.skipped_identity_categories or []

    identities_section = format_identities(identities)
    skipped_section = format_skipped_categories(skipped)

    return identities_section + skipped_section
```
