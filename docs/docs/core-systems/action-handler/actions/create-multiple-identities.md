---
sidebar_position: 2
---

# Create Multiple Identities

The `create_multiple_identities` action creates multiple new [Identity](/docs/database/models/identity) records for the user in a single operation.

## Action Details

**Action Type**: `create_multiple_identities`  
**Enum Value**: `ActionType.CREATE_MULTIPLE_IDENTITIES`  
**Handler Function**: `create_multiple_identities()`  
**Models Used**: [Identity](/docs/database/models/identity), [Action](/docs/database/models/action)

## What It Does

Creates multiple identities and links them to the user. Includes duplicate prevention - if an identity with the same name already exists (case-insensitive), that creation is skipped while others proceed.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identities` | array | Yes | Array of identity objects to create |

Each identity object in the array should contain:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | The name of the identity |
| `note` | string | Yes | Initial note describing the identity |
| `category` | string | Yes | The identity category |

## Implementation Steps

1. **Batch Processing**: Iterates through each identity in the list
2. **Duplicate Check**: For each identity, checks if one with the same name already exists (case-insensitive)
3. **Selective Creation**: Creates only identities that don't already exist
4. **Tracking**: Maintains lists of created and skipped identities
5. **Action Logging**: Records a single action with summary of all operations

## Example Usage

```json
{
  "action": "create_multiple_identities",
  "params": {
    "identities": [
      {
        "name": "Creative Visionary",
        "note": "Someone who brings innovative ideas to life",
        "category": "passions_and_talents"
      },
      {
        "name": "Community Builder",
        "note": "Someone who connects and supports others",
        "category": "relationships"
      }
    ]
  }
}
```

## Result

- **Success**: Returns array of created identity objects
- **Partial Success**: Creates available identities, skips duplicates
- **Logging**: Records the action with result summary: "Created 2 identities: Creative Visionary, Community Builder. Skipped 1 duplicates: Existing Identity"

## Related Actions

- [Create Identity](create-identity) - Create a single identity
- [Update Identity](update-identity) - Modify existing identity details
