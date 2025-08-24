---
sidebar_position: 9
---

# Accept Identity Visualization

The `accept_identity_visualization` action marks an [Identity](/docs/database/models/identity) as visualization_complete.

## Action Details

**Action Type**: `accept_identity_visualization`  
**Enum Value**: `ActionType.ACCEPT_IDENTITY_VISUALIZATION`  
**Handler Function**: `accept_identity_visualization()`  
**Models Used**: [Identity](/docs/database/models/identity), [Action](/docs/database/models/action)

## What It Does

Sets the state of the specified identity to 'visualization_complete', indicating that the identity has been successfully visualized during the Identity Visualization phase.

## Parameters

| Parameter | Type    | Required | Description                                              |
| --------- | ------- | -------- | -------------------------------------------------------- |
| `id`      | integer | Yes      | The ID of the identity to mark as visualization complete |

## Implementation Steps

1. **State Update**: Updates the identity's state to `IdentityState.VISUALIZATION_COMPLETE`
2. **Identity Retrieval**: Gets the updated identity for logging
3. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "accept_identity_visualization",
  "params": {
    "id": 123
  }
}
```

## Result

- **Success**: Updates the identity state to 'visualization_complete'
- **Logging**: Records the action with result summary: "Accepted identity 'Visionary Entrepreneur' visualization"

## Related Actions

- [Accept Identity](accept-identity) - Mark identity as accepted
- [Accept Identity Refinement](accept-identity-refinement) - Mark refinement as complete
- [Accept Identity Affirmation](accept-identity-affirmation) - Mark affirmation as complete
