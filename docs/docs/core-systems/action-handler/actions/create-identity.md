---
sidebar_position: 1
---

# Create Identity

The `create_identity` action creates a new [Identity](../database/models/identity) for the user.

## Action Details

**Action Type**: `create_identity`  
**Enum Value**: `ActionType.CREATE_IDENTITY`  
**Handler Function**: `create_identity()`  
**Models Used**: [Identity](../database/models/identity), [Action](../database/models/action)

## What It Does

Creates a new identity and links it to the user. The action includes duplicate prevention - if an identity with the same name already exists (case-insensitive), the creation is skipped.

## Parameters

| Parameter  | Type   | Required | Description                                          |
| ---------- | ------ | -------- | ---------------------------------------------------- |
| `name`     | string | Yes      | The name of the identity to create                   |
| `note`     | string | Yes      | Initial note describing the identity                 |
| `category` | string | Yes      | The identity category (e.g., "passions_and_talents") |

## Implementation Steps

1. **Duplicate Check**: Checks if an identity with the same name already exists for the user (case-insensitive)
2. **Identity Creation**: If no duplicate exists, creates a new [Identity](../database/models/identity) with:
   - User association
   - Name
   - Initial notes (as a list)
   - Category
3. **Action Logging**: Records the action in the [Action](../database/models/action) model

## Example Usage

```json
{
  "action": "create_identity",
  "params": {
    "name": "Creative Visionary",
    "note": "Someone who brings innovative ideas to life through artistic expression",
    "category": "passions_and_talents"
  }
}
```

## Result

- **Success**: Creates a new identity and returns the identity object
- **Duplicate**: Returns `None` if an identity with the same name already exists
- **Logging**: Records the action with result summary: "Created identity 'Creative Visionary' in category 'passions_and_talents'"

## Related Actions

- [Update Identity](update-identity) - Modify existing identity details
- [Update Identity Name](update-identity-name) - Change identity name specifically
- [Add Identity Note](add-identity-note) - Add additional notes to an identity
