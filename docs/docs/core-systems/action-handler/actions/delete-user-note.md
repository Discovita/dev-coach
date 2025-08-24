---
sidebar_position: 21
---

# Delete User Note

The `delete_user_note` action removes [UserNote](/docs/database/models/user-note) entries.

> **⚠️ Sentinel Only**: This action is used exclusively by the [Sentinel Memory System](../../sentinel/overview) to remove outdated user information. It is not available for use by the main coaching AI.

## Action Details

**Action Type**: `delete_user_note`  
**Enum Value**: `ActionType.DELETE_USER_NOTE`  
**Handler Function**: `delete_user_note()`  
**Models Used**: [UserNote](/docs/database/models/user-note), [Action](/docs/database/models/action)

## What It Does

Deletes one or more [UserNote](/docs/database/models/user-note) entries by ID.

## Parameters

| Parameter  | Type  | Required | Description                 |
| ---------- | ----- | -------- | --------------------------- |
| `note_ids` | array | Yes      | Array of note IDs to delete |

## Implementation Steps

1. **Note Deletion**: Deletes the specified [UserNote](/docs/database/models/user-note) entries
2. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "delete_user_note",
  "params": {
    "note_ids": [123, 124]
  }
}
```

## Result

- **Success**: Deletes the specified user notes
- **Logging**: Records the action with result summary: "Deleted user notes"

## Related Actions

- [Add User Note](add-user-note) - Create new user notes
- [Update User Note](update-user-note) - Update existing user notes
