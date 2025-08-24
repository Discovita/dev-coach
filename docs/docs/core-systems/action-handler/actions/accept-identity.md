---
sidebar_position: 6
---

# Accept Identity

The `accept_identity` action marks an [Identity](../database/models/identity) as accepted by setting its state to 'accepted'.

## Action Details

**Action Type**: `accept_identity`  
**Enum Value**: `ActionType.ACCEPT_IDENTITY`  
**Handler Function**: `accept_identity()`  
**Models Used**: [Identity](../database/models/identity), [Action](../database/models/action)

## What It Does

Sets the state of the specified identity to 'accepted', indicating that the user has fully embraced and accepted this identity.

## Parameters

| Parameter | Type    | Required | Description                      |
| --------- | ------- | -------- | -------------------------------- |
| `id`      | integer | Yes      | The ID of the identity to accept |

## Implementation Steps

1. **State Update**: Updates the identity's state to `IdentityState.ACCEPTED`
2. **Identity Retrieval**: Gets the updated identity for logging
3. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "accept_identity",
  "params": {
    "id": 123
  }
}
```

## Result

- **Success**: Updates the identity state to 'accepted'
- **Logging**: Records the action with result summary: "Accepted identity 'Visionary Entrepreneur'"

## Related Actions

- [Accept Identity Refinement](accept-identity-refinement) - Mark refinement as complete
- [Accept Identity Affirmation](accept-identity-affirmation) - Mark affirmation as complete
- [Accept Identity Visualization](accept-identity-visualization) - Mark visualization as complete
