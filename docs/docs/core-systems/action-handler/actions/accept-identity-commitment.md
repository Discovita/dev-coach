---
sidebar_position: 6.5
---

# Accept Identity Commitment

The `accept_identity_commitment` action marks an [Identity](/docs/database/models/identity) as commitment complete by setting its state to 'commitment_complete'.

## Action Details

**Action Type**: `accept_identity_commitment`  
**Enum Value**: `ActionType.ACCEPT_IDENTITY_COMMITMENT`  
**Handler Function**: `accept_identity_commitment()`  
**Models Used**: [Identity](/docs/database/models/identity), [Action](/docs/database/models/action), [CoachState](/docs/database/models/coach-state)

## What It Does

Sets the state of the specified identity to 'commitment_complete', indicating that the user has committed to this identity and wants to advance to the I Am Statement Phase with it. After marking the identity as commitment complete, the action automatically updates the coach state's current identity to the next pending commitment identity (if one exists).

## Parameters

| Parameter | Type   | Required | Description                                    |
| --------- | ------ | -------- | ---------------------------------------------- |
| `id`      | string | Yes      | The UUID of the identity to mark as committed |

## Implementation Steps

1. **State Update**: Updates the identity's state to `IdentityState.COMMITMENT_COMPLETE`
2. **Identity Retrieval**: Gets the updated identity for logging
3. **Current Identity Update**: Sets the coach state's current identity to the next (oldest) identity that needs commitment, excluding commitment_complete and archived identities
4. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "accept_identity_commitment",
  "params": {
    "id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

## Result

- **Success**: Updates the identity state to 'commitment_complete' and updates current identity
- **Logging**: Records the action with result summary: "Accepted commitment for identity 'Visionary Entrepreneur'"

## Behavior

- **State Transition**: The identity moves from its current state to `COMMITMENT_COMPLETE`
- **Current Identity Update**: After marking an identity as commitment complete, the coach state's `current_identity` is automatically updated to the next oldest identity that:
  - Is not already `COMMITMENT_COMPLETE`
  - Is not `ARCHIVED`
  - Belongs to the same user
- **Workflow Advancement**: Commitment complete identities are ready to advance to the I Am Statement Phase

## Related Actions

- [Accept Identity](accept-identity) - Mark an identity as accepted
- [Archive Identity](archive-identity) - Archive an identity instead of committing
- [Nest Identity](nest-identity) - Nest an identity under another instead of committing
- [Accept "I Am" Statement](accept-i-am-statement) - Mark "I Am" Statement as complete (next phase)

