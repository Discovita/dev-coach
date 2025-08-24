---
sidebar_position: 3
---

# Update Identity Name

The `update_identity_name` action updates only the name of an existing [Identity](../database/models/identity).

## Action Details

**Action Type**: `update_identity_name`  
**Enum Value**: `ActionType.UPDATE_IDENTITY_NAME`  
**Handler Function**: `update_identity_name()`  
**Models Used**: [Identity](../database/models/identity), [Action](../database/models/action)

## What It Does

Updates only the name field of an existing identity. This is a specialized action for when only the name needs to be changed.

## Parameters

| Parameter | Type    | Required | Description                      |
| --------- | ------- | -------- | -------------------------------- |
| `id`      | integer | Yes      | The ID of the identity to update |
| `name`    | string  | Yes      | New name for the identity        |

## Implementation Steps

1. **Identity Retrieval**: Gets the identity by ID and user
2. **Name Update**: Updates the name field
3. **Save**: Saves the updated identity
4. **Action Logging**: Records the action with the old and new names

## Example Usage

```json
{
  "action": "update_identity_name",
  "params": {
    "id": 123,
    "name": "Visionary Entrepreneur"
  }
}
```

## Result

- **Success**: Updates the identity name and returns the updated identity object
- **Logging**: Records the action with result summary: "Updated identity name from 'Creator' to 'Visionary Entrepreneur'"

## Related Actions

- [Update Identity](update-identity) - Update multiple identity fields
- [Create Identity](create-identity) - Create new identities
