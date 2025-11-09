---
sidebar_position: 7
---

# Accept Identity Refinement

 The `accept_identity_refinement` action marks an [Identity](/docs/database/models/identity) as refinement_complete.

## Action Details

**Action Type**: `accept_identity_refinement`  
**Enum Value**: `ActionType.ACCEPT_IDENTITY_REFINEMENT`  
**Handler Function**: `accept_identity_refinement()`  
**Models Used**: [Identity](/docs/database/models/identity), [Action](/docs/database/models/action)

## What It Does

Sets the state of the specified identity to 'refinement_complete', indicating that the identity has been successfully refined during the Identity Refinement phase.

## Parameters

| Parameter | Type    | Required | Description                                           |
| --------- | ------- | -------- | ----------------------------------------------------- |
| `id`      | integer | Yes      | The ID of the identity to mark as refinement complete |

## Implementation Steps

1. **State Update**: Updates the identity's state to `IdentityState.REFINEMENT_COMPLETE`
2. **Identity Retrieval**: Gets the updated identity for logging
3. **Current Identity Update**: Sets the current identity to the next pending refinement
4. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "accept_identity_refinement",
  "params": {
    "id": 123
  }
}
```

## Result

- **Success**: Updates the identity state to 'refinement_complete'
- **Logging**: Records the action with result summary: "Accepted identity 'Visionary Entrepreneur' refinement"

## Related Actions

- [Accept Identity](accept-identity) - Mark identity as accepted
- [Accept "I Am" Statement](accept-i-am-statement) - Mark "I Am" Statement as complete
- [Accept Identity Visualization](accept-identity-visualization) - Mark visualization as complete
