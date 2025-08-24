---
sidebar_position: 3
---

# User Notes

The `user_notes` context key provides the user's personal notes and preferences for personalization in prompts.

## Context Key Details

**Key Name**: `user_notes`  
**Enum Value**: `ContextKey.USER_NOTES`  
**Data Source**: UserNote model  
**Return Type**: `str`

## What Data It Provides

Returns all user notes formatted as a markdown section with numbered entries, or a message indicating no notes exist.

## How It Gets the Data

The function queries the UserNote model for all notes associated with the user, orders them by creation date, and formats them into a numbered list with note IDs.

## Example Data

```python
# Example return values
"## User Notes\n\n**1** (ID: 123): I prefer morning coaching sessions\n**2** (ID: 124): I'm working on improving my communication skills\n"

"## User Notes\n\nNo Notes Yet...\n"
```

## Implementation

```python
def get_user_notes_context(coach_state: CoachState) -> str:
    """
    For a given coach_state, retrieve and format all associated UserNotes for the user.
    Formats these notes into a markdown-friendly string, with a heading.
    """
    user_notes = UserNote.objects.filter(user=coach_state.user).order_by("created_at")
    if user_notes:
        formatted_notes = []
        for i, note in enumerate(user_notes):
            formatted_notes.append(f"**{i+1}** (ID: {note.id}): {note.note}")
        notes_block = "\n".join(formatted_notes)
        return f"## User Notes\n\n{notes_block}\n"
    else:
        return f"## User Notes\n\nNo Notes Yet...\n"
```
