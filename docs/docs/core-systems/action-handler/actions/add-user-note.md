---
sidebar_position: 19
---

# Add User Note

The `add_user_note` action creates new [UserNote](/docs/database/models/user-note) entries for the user.

> **⚠️ Sentinel Only**: This action is used exclusively by the [Sentinel Memory System](../../sentinel/overview) to store user information extracted from chat messages. It is not available for use by the main coaching AI.

## Action Details

**Action Type**: `add_user_note`  
**Enum Value**: `ActionType.ADD_USER_NOTE`  
**Handler Function**: `add_user_note()`  
**Models Used**: [UserNote](/docs/database/models/user-note)

## What It Does

Creates separate [UserNote](/docs/database/models/user-note) entries for each note in the provided list. This action is used by the Sentinel system to store important facts or context about the user.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `notes` | array | Yes | List of notes to create |

## Implementation Steps

1. **Note Creation**: Creates a separate [UserNote](/docs/database/models/user-note) entry for each note in the list
2. **User Association**: Links each note to the user
3. **Note Processing**: Strips whitespace from each note

## Example Usage

```json
{
  "action": "add_user_note",
  "params": {
    "notes": [
      "Prefers morning coaching sessions",
      "Working on improving communication skills",
      "Has a background in software development"
    ]
  }
}
```

## Result

- **Success**: Creates multiple [UserNote](/docs/database/models/user-note) entries
- **Note**: This action does not log to the [Action](/docs/database/models/action) model as it's used by the Sentinel system

## Related Actions

- [Update User Note](update-user-note) - Update existing user notes
- [Delete User Note](delete-user-note) - Remove user notes
