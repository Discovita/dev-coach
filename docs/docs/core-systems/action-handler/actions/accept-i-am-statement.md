---
sidebar_position: 8
---

# Accept "I Am" Statement

The `accept_i_am_statement` action marks an [Identity](/docs/database/models/identity) as i_am_complete.

## Action Details

**Action Type**: `accept_i_am_statement`  
**Enum Value**: `ActionType.ACCEPT_I_AM_STATEMENT`  
**Handler Function**: `accept_i_am_statement()`  
**Models Used**: [Identity](/docs/database/models/identity), [Action](/docs/database/models/action)

## What It Does

Sets the state of the specified identity to 'i_am_complete', indicating that the "I Am" Statement has been successfully created during the I Am Statements phase.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | The ID of the identity to mark as i_am_complete |

## Implementation Steps

1. **State Update**: Updates the identity's state to `IdentityState.I_AM_COMPLETE`
2. **Identity Retrieval**: Gets the updated identity for logging
3. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "accept_i_am_statement",
  "params": {
    "id": 123
  }
}
```

## Result

- **Success**: Updates the identity state to 'i_am_complete'
- **Logging**: Records the action with result summary: "Accepted identity 'Visionary Entrepreneur' "I Am" Statement"

## Related Actions

- [Accept Identity](accept-identity) - Mark identity as accepted
- [Accept Identity Refinement](accept-identity-refinement) - Mark refinement as complete
- [Accept Identity Visualization](accept-identity-visualization) - Mark visualization as complete
