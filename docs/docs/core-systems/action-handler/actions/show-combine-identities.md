---
sidebar_position: 3
---

# Show Combine Identities

The `show_combine_identities` action displays a UI component that allows users to choose whether to combine two specific identities.

## Action Details

**Action Type**: `show_combine_identities`  
**Enum Value**: `ActionType.SHOW_COMBINE_IDENTITIES`  
**Handler Function**: `show_combine_identities()`  
**Models Used**: [Identity](/docs/database/models/identity), [Action](/docs/database/models/action), ComponentConfig

## What It Does

Creates and returns a component configuration that displays two identities and provides Yes/No buttons for combining them. The Yes button triggers the combine_identities action with both identity IDs.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identity_id_a` | integer | Yes | The ID of the first identity to display |
| `identity_id_b` | integer | Yes | The ID of the second identity to display |

## Implementation Steps

1. **Identity Retrieval**: Fetches both identities from the database
2. **Component Building**: Creates ComponentIdentity objects for display
3. **Button Configuration**: Sets up Yes/No choice buttons
4. **Action Integration**: Configures Yes button to trigger combine_identities action
5. **Action Logging**: Records the action with identity details

## Example Usage

```json
{
  "action": "show_combine_identities",
  "params": {
    "identity_id_a": 123,
    "identity_id_b": 456
  }
}
```

## Result

- **Success**: Returns a ComponentConfig object with identity display and choice buttons
- **Component Type**: `ComponentType.COMBINE_IDENTITIES`
- **Identities**: Display objects for both identities (id, name, category)
- **Buttons**: 
  - "Yes" (triggers combine_identities action)
  - "No" (no action)
- **Logging**: Records the action with result summary: "Showed combine identities component for identities 123 and 456"

## Component Structure

The returned component includes:
- **Component Type**: Combine Identities
- **Identities**: Array of ComponentIdentity objects with id, name, and category
- **Buttons**: 
  - "Yes" with action: `COMBINE_IDENTITIES` with both identity IDs
  - "No" (no actions)

## Related Actions

- [Combine Identities](combine-identities) - Actually merge the two identities
- [Create Identity](create-identity) - Create new identities
- [Show Accept I Am Component](show-accept-i-am-component) - Display identity acceptance component
