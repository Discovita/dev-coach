---
sidebar_position: 20
---

# Update User Note

The `update_user_note` action updates existing [UserNote](../database/models/user-note) entries.

> **⚠️ Sentinel Only**: This action is used exclusively by the [Sentinel Memory System](../../sentinel/overview) to update user information extracted from chat messages. It is not available for use by the main coaching AI.

## Action Details

**Action Type**: `update_user_note`  
**Enum Value**: `ActionType.UPDATE_USER_NOTE`  
**Handler Function**: `update_user_note()`  
**Models Used**: [UserNote](../database/models/user-note), [Action](../database/models/action)

## What It Does

Updates one or more existing [UserNote](../database/models/user-note) entries by ID. Each object in the notes array must have an ID and the new note text.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `notes` | array | Yes | Array of objects with `id` and `note` fields |

## Implementation Steps

1. **Note Updates**: Updates each [UserNote](../database/models/user-note) with the new text
2. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "update_user_note",
  "params": {
    "notes": [
      {
        "id": 123,
        "note": "Updated preference for morning coaching sessions"
      },
      {
        "id": 124,
        "note": "Updated communication skills progress"
      }
    ]
  }
}
```

## Result

- **Success**: Updates the specified user notes
- **Logging**: Records the action with result summary: "Updated user notes"

## Related Actions

- [Add User Note](add-user-note) - Create new user notes
- [Delete User Note](delete-user-note) - Remove user notes
