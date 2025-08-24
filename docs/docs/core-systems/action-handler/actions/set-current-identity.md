---
sidebar_position: 13
---

# Set Current Identity

The `set_current_identity` action sets the current identity being refined in the [CoachState](../database/models/coach-state).

## Action Details

**Action Type**: `set_current_identity`  
**Enum Value**: `ActionType.SET_CURRENT_IDENTITY`  
**Handler Function**: `set_current_identity()`  
**Models Used**: [CoachState](../database/models/coach-state), [Identity](../database/models/identity), [Action](../database/models/action)

## What It Does

Sets the `current_identity` field of the user's coach state to point to a specific [Identity](../database/models/identity) for targeted refinement during the Identity Refinement phase.

## Parameters

| Parameter     | Type    | Required | Description                              |
| ------------- | ------- | -------- | ---------------------------------------- |
| `identity_id` | integer | Yes      | The ID of the identity to set as current |

## Implementation Steps

1. **Identity Validation**: Verifies the identity exists
2. **Current Identity Update**: Updates the `current_identity` field in the [CoachState](../database/models/coach-state)
3. **Save**: Saves the updated coach state
4. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "set_current_identity",
  "params": {
    "identity_id": 123
  }
}
```

## Result

- **Success**: Sets the current identity and saves the coach state
- **Error**: Raises ValueError if identity doesn't exist
- **Logging**: Records the action with result summary: "Set current identity to 'Visionary Entrepreneur'"

## Related Actions

- [Select Identity Focus](select-identity-focus) - Set identity category focus
- [Update Identity](update-identity) - Update the current identity details
