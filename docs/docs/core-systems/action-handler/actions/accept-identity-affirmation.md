---
sidebar_position: 8
---

# Accept Identity Affirmation

The `accept_identity_affirmation` action marks an [Identity](../database/models/identity) as affirmation_complete.

## Action Details

**Action Type**: `accept_identity_affirmation`  
**Enum Value**: `ActionType.ACCEPT_IDENTITY_AFFIRMATION`  
**Handler Function**: `accept_identity_affirmation()`  
**Models Used**: [Identity](../database/models/identity), [Action](../database/models/action)

## What It Does

Sets the state of the specified identity to 'affirmation_complete', indicating that the identity has been successfully affirmed during the Identity Affirmation phase.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | The ID of the identity to mark as affirmation complete |

## Implementation Steps

1. **State Update**: Updates the identity's state to `IdentityState.AFFIRMATION_COMPLETE`
2. **Identity Retrieval**: Gets the updated identity for logging
3. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "accept_identity_affirmation",
  "params": {
    "id": 123
  }
}
```

## Result

- **Success**: Updates the identity state to 'affirmation_complete'
- **Logging**: Records the action with result summary: "Accepted identity 'Visionary Entrepreneur' affirmation"

## Related Actions

- [Accept Identity](accept-identity) - Mark identity as accepted
- [Accept Identity Refinement](accept-identity-refinement) - Mark refinement as complete
- [Accept Identity Visualization](accept-identity-visualization) - Mark visualization as complete
