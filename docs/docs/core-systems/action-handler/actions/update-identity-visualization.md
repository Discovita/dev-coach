---
sidebar_position: 5
---

# Update Identity Visualization

The `update_identity_visualization` action updates only the visualization of an existing [Identity](/docs/database/models/identity).

## Action Details

**Action Type**: `update_identity_visualization`  
**Enum Value**: `ActionType.UPDATE_IDENTITY_VISUALIZATION`  
**Handler Function**: `update_identity_visualization()`  
**Models Used**: [Identity](/docs/database/models/identity), [Action](/docs/database/models/action)

## What It Does

Updates only the visualization field of an existing identity. This is used during the Identity Visualization phase to add visual elements and imagery to identities.

## Parameters

| Parameter       | Type    | Required | Description                        |
| --------------- | ------- | -------- | ---------------------------------- |
| `id`            | integer | Yes      | The ID of the identity to update   |
| `visualization` | string  | Yes      | New visualization for the identity |

## Implementation Steps

1. **Identity Retrieval**: Gets the identity by ID and user
2. **Visualization Update**: Updates the visualization field
3. **Save**: Saves the updated identity
4. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "update_identity_visualization",
  "params": {
    "id": 123,
    "visualization": "I see myself standing confidently in a modern office, surrounded by a team of inspired professionals. I'm presenting innovative ideas on a large screen, and the energy in the room is electric with possibility."
  }
}
```

## Result

- **Success**: Updates the identity visualization and returns the updated identity object
- **Logging**: Records the action with result summary: "Updated identity 'Visionary Entrepreneur' visualization"

## Related Actions

- [Update Identity](update-identity) - Update multiple identity fields
- [Update Identity Affirmation](update-identity-affirmation) - Update identity affirmation
- [Accept Identity Visualization](accept-identity-visualization) - Mark visualization as complete
