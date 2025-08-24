---
sidebar_position: 17
---

# Update Who You Want to Be

The `update_who_you_want_to_be` action updates the user's aspirational identities in the [CoachState](/docs/database/models/coach-state).

## Action Details

**Action Type**: `update_who_you_want_to_be`  
**Enum Value**: `ActionType.UPDATE_WHO_YOU_WANT_TO_BE`  
**Handler Function**: `update_who_you_want_to_be()`  
**Models Used**: [CoachState](/docs/database/models/coach-state), [Action](/docs/database/models/action)

## What It Does

Updates the `who_you_want_to_be` field in the user's coach state with a complete list of the user's aspirational identities. This action requires the complete list, not just changes.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identities` | array | Yes | Complete list of aspirational identities |

## Implementation Steps

1. **Identity List Update**: Updates the `who_you_want_to_be` field with the complete list of identities
2. **Save**: Saves the updated coach state
3. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "update_who_you_want_to_be",
  "params": {
    "identities": ["Confident Leader", "Inspiring Mentor", "Successful Entrepreneur"]
  }
}
```

## Result

- **Success**: Updates the who_you_want_to_be list and saves the coach state
- **Logging**: Records the action with result summary: "Updated Who You Want to Be identities"

## Related Actions

- [Update Who You Are](update-who-you-are) - Update current self-description identities
- [Update Asked Questions](update-asked-questions) - Track asked questions
