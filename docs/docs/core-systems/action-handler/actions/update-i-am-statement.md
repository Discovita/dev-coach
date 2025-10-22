---
sidebar_position: 4
---

# Update "I Am" Statement

The `update_i_am_statement` action updates only the "I Am" Statement of an existing [Identity](/docs/database/models/identity).

## Action Details

**Action Type**: `update_i_am_statement`  
**Enum Value**: `ActionType.UPDATE_I_AM_STATEMENT`  
**Handler Function**: `update_i_am_statement()`  
**Models Used**: [Identity](/docs/database/models/identity), [Action](/docs/database/models/action)

## What It Does

Updates only the "I Am" Statement field of an existing identity. This is used during the I Am Statements phase to add empowering "I Am" Statements to identities.

## Parameters

| Parameter        | Type    | Required | Description                           |
| ---------------- | ------- | -------- | ------------------------------------- |
| `id`             | integer | Yes      | The ID of the identity to update      |
| `i_am_statement` | string  | Yes      | New 'I Am' statement for the identity |

## Implementation Steps

1. **Identity Retrieval**: Gets the identity by ID and user
2. **"I Am" Statement Update**: Updates the "I Am" Statement field
3. **Save**: Saves the updated identity
4. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "update_i_am_statement",
  "params": {
    "id": 123,
    "i_am_statement": "I am a Visionary Entrepreneur who leads with innovation and creates lasting impact in the world."
  }
}
```

## Result

- **Success**: Updates the identity "I Am" Statement and returns the updated identity object
- **Logging**: Records the action with result summary: "Updated identity 'Visionary Entrepreneur' "I Am" Statement"

## Related Actions

- [Update Identity](update-identity) - Update multiple identity fields
- [Update Identity Visualization](update-identity-visualization) - Update identity visualization
- [Accept "I Am" Statement](accept-i-am-statement) - Mark "I Am" Statement as complete
