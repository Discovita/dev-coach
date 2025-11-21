---
sidebar_position: 9.5
---

# Archive Identity

The `archive_identity` action archives an [Identity](/docs/database/models/identity) by setting its state to 'archived'.

## Action Details

**Action Type**: `archive_identity`  
**Enum Value**: `ActionType.ARCHIVE_IDENTITY`  
**Handler Function**: `archive_identity()`  
**Models Used**: [Identity](/docs/database/models/identity), [Action](/docs/database/models/action)

## What It Does

Sets the state of the specified identity to 'archived'. Archived identities are excluded from active coaching workflows but remain in the database for historical reference. They are automatically filtered out of default list queries but can still be accessed via direct ID retrieval or by using query parameters.

## Parameters

| Parameter | Type   | Required | Description                        |
| --------- | ------ | -------- | ---------------------------------- |
| `id`      | string | Yes      | The UUID of the identity to archive |

## Implementation Steps

1. **State Update**: Updates the identity's state to `IdentityState.ARCHIVED`
2. **Identity Retrieval**: Gets the updated identity for logging
3. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "archive_identity",
  "params": {
    "id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

## Result

- **Success**: Updates the identity state to 'archived'
- **Logging**: Records the action with result summary: "Archived identity 'Visionary Entrepreneur'"

## Behavior

- **Exclusion from Workflows**: Archived identities are automatically excluded from:
  - Default identity list queries
  - Context functions that retrieve identities for prompts
  - Active coaching phase workflows
- **Preservation**: The identity remains in the database with all its data intact
- **Access**: Archived identities can still be:
  - Retrieved by direct ID lookup
  - Included in queries using `?include_archived=true` parameter
  - Viewed using `?archived_only=true` parameter

## Related Actions

- [Accept Identity](accept-identity) - Mark an identity as accepted
- [Accept Identity Commitment](accept-identity-commitment) - Mark commitment as complete
- [Add Identity Note](add-identity-note) - Add notes before archiving if needed
