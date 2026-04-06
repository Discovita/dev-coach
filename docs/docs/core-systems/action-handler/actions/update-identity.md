---
sidebar_position: 2
---

# Update Identity

The `update_identity` action updates multiple fields of an existing [Identity](/docs/database/models/identity).

## Action Details

**Action Type**: `update_identity`  
**Enum Value**: `ActionType.UPDATE_IDENTITY`  
**Handler Function**: `update_identity()`  
**Models Used**: [Identity](/docs/database/models/identity), [Action](/docs/database/models/action)

## What It Does

Updates specified fields of an existing identity. Only fields provided (not None) in the parameters will be updated. Notes are appended to the existing notes list, not replaced.

> **⚠️ Recommendation**: Use more narrowly focused update functions when possible. LLMs tend to get carried away and update more fields than intended when using this general-purpose action. Consider using [Update Identity Name](update-identity-name), [Update "I Am" Statement](update-i-am-statement), or [Update Identity Visualization](update-identity-visualization) for specific field updates.

## Parameters

| Parameter       | Type           | Required | Description                                       |
| --------------- | -------------- | -------- | ------------------------------------------------- |
| `id`            | string (UUID)  | Yes      | The UUID of the identity to update                |
| `name`          | string         | Yes      | New name for the identity                         |
| `i_am_statement`| string         | Yes      | New "I Am" Statement for the identity             |
| `visualization` | string         | Yes      | New visualization for the identity                |
| `state`         | IdentityState  | Yes      | New state for the identity                        |
| `notes`         | array          | Yes      | Additional notes to append (not replace existing) |
| `category`      | IdentityCategory | Yes    | New category for the identity                     |

> **Note**: The Pydantic model (`UpdateIdentityParams`) marks all fields as required. However, the handler checks each field for `is not None` before applying updates, so the LLM must provide all fields even if only some need changing.

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
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Visionary Entrepreneur",
    "i_am_statement": "I am a visionary entrepreneur who leads with innovation",
    "visualization": "Standing confidently at a whiteboard mapping out big ideas",
    "state": "refinement_complete",
    "notes": [
      "The name 'Visionary Entrepreneur' reflects their desire to lead with vision and impact."
    ],
    "category": "work_and_professional"
  }
}
```

## Result

- **Success**: Updates the identity and returns the updated identity object
- **Logging**: Records the action with result summary: "Updated identity 'Visionary Entrepreneur' fields: name, notes, state"

## Related Actions

- [Create Identity](create-identity) - Create new identities
- [Update Identity Name](update-identity-name) - Update only the name
- [Update "I Am" Statement](update-i-am-statement) - Update only the "I Am" Statement
- [Update Identity Visualization](update-identity-visualization) - Update only the visualization
