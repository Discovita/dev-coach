---
sidebar_position: 4
---

# Update Identity Affirmation

The `update_identity_affirmation` action updates only the affirmation of an existing [Identity](/docs/database/models/identity).

## Action Details

**Action Type**: `update_identity_affirmation`  
**Enum Value**: `ActionType.UPDATE_IDENTITY_AFFIRMATION`  
**Handler Function**: `update_identity_affirmation()`  
**Models Used**: [Identity](/docs/database/models/identity), [Action](/docs/database/models/action)

## What It Does

Updates only the affirmation field of an existing identity. This is used during the Identity Affirmation phase to add empowering affirmations to identities.

## Parameters

| Parameter     | Type    | Required | Description                      |
| ------------- | ------- | -------- | -------------------------------- |
| `id`          | integer | Yes      | The ID of the identity to update |
| `affirmation` | string  | Yes      | New affirmation for the identity |

## Implementation Steps

1. **Identity Retrieval**: Gets the identity by ID and user
2. **Affirmation Update**: Updates the affirmation field
3. **Save**: Saves the updated identity
4. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "update_identity_affirmation",
  "params": {
    "id": 123,
    "affirmation": "I am a Visionary Entrepreneur who leads with innovation and creates lasting impact in the world."
  }
}
```

## Result

- **Success**: Updates the identity affirmation and returns the updated identity object
- **Logging**: Records the action with result summary: "Updated identity 'Visionary Entrepreneur' affirmation"

## Related Actions

- [Update Identity](update-identity) - Update multiple identity fields
- [Update Identity Visualization](update-identity-visualization) - Update identity visualization
- [Accept Identity Affirmation](accept-identity-affirmation) - Mark affirmation as complete
