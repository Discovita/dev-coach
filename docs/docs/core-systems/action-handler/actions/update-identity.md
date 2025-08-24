---
sidebar_position: 2
---

# Update Identity

The `update_identity` action updates multiple fields of an existing [Identity](../database/models/identity).

## Action Details

**Action Type**: `update_identity`  
**Enum Value**: `ActionType.UPDATE_IDENTITY`  
**Handler Function**: `update_identity()`  
**Models Used**: [Identity](../database/models/identity), [Action](../database/models/action)

## What It Does

Updates specified fields of an existing identity. Only fields provided (not None) in the parameters will be updated. Notes are appended to the existing notes list, not replaced.

> **⚠️ Recommendation**: Use more narrowly focused update functions when possible. LLMs tend to get carried away and update more fields than intended when using this general-purpose action. Consider using [Update Identity Name](update-identity-name), [Update Identity Affirmation](update-identity-affirmation), or [Update Identity Visualization](update-identity-visualization) for specific field updates.

## Parameters

| Parameter       | Type    | Required | Description                                       |
| --------------- | ------- | -------- | ------------------------------------------------- |
| `id`            | integer | Yes      | The ID of the identity to update                  |
| `name`          | string  | No       | New name for the identity                         |
| `affirmation`   | string  | No       | New affirmation for the identity                  |
| `visualization` | string  | No       | New visualization for the identity                |
| `state`         | string  | No       | New state for the identity                        |
| `category`      | string  | No       | New category for the identity                     |
| `notes`         | array   | No       | Additional notes to append (not replace existing) |

## Implementation Steps

1. **Field Preparation**: Creates a dictionary of fields to update, skipping any that are None
2. **Bulk Update**: Updates all fields except notes using Django's bulk update
3. **Notes Handling**: If notes are provided, appends them to the existing notes list
4. **Action Logging**: Records the action with details of what was updated

## Example Usage

```json
{
  "action": "update_identity",
  "params": {
    "id": 123,
    "name": "Visionary Entrepreneur",
    "notes": [
      "The name 'Visionary Entrepreneur' reflects their desire to lead with vision and impact."
    ],
    "state": "refinement_complete"
  }
}
```

## Result

- **Success**: Updates the identity and returns the updated identity object
- **Logging**: Records the action with result summary: "Updated identity 'Visionary Entrepreneur' fields: name, notes, state"

## Related Actions

- [Create Identity](create-identity) - Create new identities
- [Update Identity Name](update-identity-name) - Update only the name
- [Update Identity Affirmation](update-identity-affirmation) - Update only the affirmation
- [Update Identity Visualization](update-identity-visualization) - Update only the visualization
