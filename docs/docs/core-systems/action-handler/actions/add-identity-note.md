---
sidebar_position: 10
---

# Add Identity Note

The `add_identity_note` action adds a note to an existing [Identity](../database/models/identity).

## Action Details

**Action Type**: `add_identity_note`  
**Enum Value**: `ActionType.ADD_IDENTITY_NOTE`  
**Handler Function**: `add_identity_note()`  
**Models Used**: [Identity](../database/models/identity), [Action](../database/models/action)

## What It Does

Adds a note to an existing identity. Notes are appended to the existing notes list, not replaced.

## Parameters

| Parameter | Type    | Required | Description                             |
| --------- | ------- | -------- | --------------------------------------- |
| `id`      | integer | Yes      | The ID of the identity to add a note to |
| `note`    | string  | Yes      | The note to add to the identity         |

## Implementation Steps

1. **Identity Retrieval**: Gets the identity by ID and user
2. **Note Addition**: Appends the new note to the existing notes list
3. **Save**: Saves the updated identity
4. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "add_identity_note",
  "params": {
    "id": 123,
    "note": "This identity emerged from their passion for creative problem-solving"
  }
}
```

## Result

- **Success**: Adds the note to the identity and returns the updated identity object
- **Logging**: Records the action with result summary: "Added note to identity 'Visionary Entrepreneur'"

## Related Actions

- [Update Identity](update-identity) - Update multiple identity fields including notes
- [Create Identity](create-identity) - Create new identities with initial notes
