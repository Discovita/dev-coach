---
sidebar_position: 9.6
---

# Nest Identity

The `nest_identity` action nests one identity under a parent identity by copying notes and archiving the nested identity.

## Action Details

**Action Type**: `nest_identity`  
**Enum Value**: `ActionType.NEST_IDENTITY`  
**Handler Function**: `nest_identity()`  
**Models Used**: [Identity](/docs/database/models/identity), [Action](/docs/database/models/action)

## What It Does

Nests an identity under a parent identity by copying all notes from the nested identity to the parent, then archiving the nested identity. No name changes are made to either identity. This is useful during the Identity Commitment phase when a user wants to keep a concept as flavor/context under another identity rather than as a standalone identity.

## Parameters

| Parameter            | Type   | Required | Description                                                      |
| ------------------- | ------ | -------- | ---------------------------------------------------------------- |
| `nested_identity_id` | string | Yes      | The UUID of the identity to nest (will be archived)             |
| `parent_identity_id` | string | Yes      | The UUID of the parent identity to nest under (will be kept)     |

## Implementation Steps

1. **Validation**: Ensures the two identity IDs are different and both exist for the user
2. **Parent Note**: Adds a note to the parent identity indicating the nested identity was nested under it: `"Nested '{nested_name}' identity under this identity."`
3. **Notes Copying**: Copies all notes from the nested identity to the parent identity with prefix: `"[from {nested_name}]: {note}"`
4. **Parent Update**: Saves the parent identity with the combined notes
5. **Archiving**: Archives the nested identity:
   - Adds a note indicating it was nested under the parent identity
   - Sets the identity state to `ARCHIVED`
   - Preserves the identity in the database for historical reference
6. **Action Logging**: Records the action with details including number of notes copied

## Example Usage

```json
{
  "action": "nest_identity",
  "params": {
    "nested_identity_id": "550e8400-e29b-41d4-a716-446655440000",
    "parent_identity_id": "660e8400-e29b-41d4-a716-446655440001"
  }
}
```

## Result

- **Success**: Copies notes and archives the nested identity, returns `None`
- **Validation Error**: Raises `ValueError` if IDs are the same or identities don't exist
- **Logging**: Records the action with result summary: "Nested identity 'Chef' under 'Magical Healer'. Copied 3 notes to parent identity."

## Behavior

- **No Name Changes**: Both identities keep their original names
- **Parent Identity Notes**: The parent identity receives:
  - A note indicating the nested identity was nested: `"Nested '{nested_name}' identity under this identity."`
  - All notes from the nested identity with prefix: `"[from {nested_name}]: {note}"`
- **Archived Identity**: The nested identity:
  - Remains in the database with all its original data
  - Is marked with state `ARCHIVED`
  - Has a note added: `"[Nested under {parent_name}]: This identity was nested under '{parent_name}'."`
  - Is excluded from active coaching workflows (commitment lists, I Am Statements, etc.)
  - Can still be accessed via direct ID lookup or with `?include_archived=true` query parameter
- **Parent Identity**: The parent identity:
  - Keeps its original name
  - Receives all notes from the nested identity appended to its existing notes
  - Remains active and continues through coaching workflows

## Use Cases

- **Identity Commitment Phase**: When a user decides an identity should be kept as context/flavor under another identity rather than as a standalone focus
- **Example**: Nesting "Chef" under "Magical Healer" - recognizing that cooking is an expression of the healer identity, not a separate identity

## Related Actions

- [Combine Identities](combine-identities) - Merge two identities with name combination and note merging
- [Archive Identity](archive-identity) - Archive a single identity without nesting
- [Accept Identity Commitment](accept-identity-commitment) - Mark an identity as committed to advance to I Am Statements

