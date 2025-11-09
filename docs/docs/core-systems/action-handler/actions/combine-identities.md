---
sidebar_position: 1
---

# Combine Identities

The `combine_identities` action merges two existing [Identity](/docs/database/models/identity) records into a single identity.

## Action Details

**Action Type**: `combine_identities`  
**Enum Value**: `ActionType.COMBINE_IDENTITIES`  
**Handler Function**: `combine_identities()`  
**Models Used**: [Identity](/docs/database/models/identity), [Action](/docs/database/models/action)

## What It Does

Combines two identities into one by merging their names and notes, then deletes the second identity. The combination follows specific rules based on identity categories.

## Parameters

| Parameter      | Type   | Required | Description                    |
| -------------- | ------ | -------- | ------------------------------ |
| `identity_id_a` | integer | Yes      | The ID of the first identity  |
| `identity_id_b` | integer | Yes      | The ID of the second identity |

## Implementation Steps

1. **Validation**: Ensures the two identity IDs are different and both exist for the user
2. **Category Rules**: Applies combination rules based on identity categories:
   - If exactly one is "Passions and Talents" → delete that one, keep the other
   - If neither or both are "Passions and Talents" → keep A, delete B
3. **Name Combination**: Creates combined name as "NameA/NameB"
4. **Notes Merging**: Merges notes from deleted identity into kept identity with source markers
5. **Cleanup**: Deletes the second identity
6. **Action Logging**: Records the action with result summary

## Example Usage

```json
{
  "action": "combine_identities",
  "params": {
    "identity_id_a": 123,
    "identity_id_b": 456
  }
}
```

## Result

- **Success**: Merges the identities and returns `None`
- **Validation Error**: Raises `ValueError` if IDs are the same or identities don't exist
- **Logging**: Records the action with result summary: "Combined identities into 'Creative Visionary/Artistic Soul'. Deleted 'Artistic Soul' (456)."

## Related Actions

- [Create Identity](create-identity) - Create new identities
- [Update Identity](update-identity) - Modify existing identity details
- [Show Combine Identities](show-combine-identities) - Display UI component for combining identities
