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
| `identity_id_a` | string (UUID) | Yes | The UUID of the first identity to display |
| `identity_id_b` | string (UUID) | Yes | The UUID of the second identity to display |

## Implementation Steps

1. **Identity Retrieval**: Fetches both identities from the database
2. **Component Building**: Creates ComponentIdentity objects for display
3. **Button Configuration**: Sets up Yes/No choice buttons
4. **Action Integration**: Configures Yes button to trigger `persist_combine_identities` first (to capture identity data before mutation), then `combine_identities`
5. **Action Logging**: Records the action with identity details

## Example Usage

```json
{
  "action": "show_combine_identities",
  "params": {
    "identity_id_a": "550e8400-e29b-41d4-a716-446655440000",
    "identity_id_b": "660e8400-e29b-41d4-a716-446655440001"
  }
}
```

## Result

- **Success**: Returns a ComponentConfig object with identity display and choice buttons
- **Component Type**: `ComponentType.COMBINE_IDENTITIES`
- **Identities**: Display objects for both identities (id, name, category)
- **Buttons**: 
  - "Yes" (triggers `persist_combine_identities` then `combine_identities`)
  - "No" (no action)
- **Logging**: Records the action with result summary: "Showed combine identities component for identities 550e8400-... and 660e8400-..."

## Component Structure

The returned component includes:
- **Component Type**: Combine Identities
- **Identities**: Array of ComponentIdentity objects with id, name, and category
- **Buttons**: 
  - "Yes" with actions (in order): `PERSIST_COMBINE_IDENTITIES` (captures identity data before mutation), then `COMBINE_IDENTITIES` with both identity IDs
  - "No" (no actions)

## Related Actions

- [Combine Identities](combine-identities) - Actually merge the two identities
- [Create Identity](create-identity) - Create new identities
- [Show Accept I Am Component](show-accept-i-am-component) - Display identity acceptance component
