---
sidebar_position: 16
---

# Update Who You Are

The `update_who_you_are` action updates the user's self-description identities in the [CoachState](../database/models/coach-state).

## Action Details

**Action Type**: `update_who_you_are`  
**Enum Value**: `ActionType.UPDATE_WHO_YOU_ARE`  
**Handler Function**: `update_who_you_are()`  
**Models Used**: [CoachState](../database/models/coach-state), [Action](../database/models/action)

## What It Does

Updates the `who_you_are` field in the user's coach state with a complete list of the user's current self-description identities. This action requires the complete list, not just changes.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identities` | array | Yes | Complete list of current self-description identities |

## Implementation Steps

1. **Identity List Update**: Updates the `who_you_are` field with the complete list of identities
2. **Save**: Saves the updated coach state
3. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "update_who_you_are",
  "params": {
    "identities": ["Creative", "Caring", "Determined", "Problem Solver"]
  }
}
```

## Result

- **Success**: Updates the who_you_are list and saves the coach state
- **Logging**: Records the action with result summary: "Updated Who You Are identities"

## Related Actions

- [Update Who You Want to Be](update-who-you-want-to-be) - Update aspirational identities
- [Update Asked Questions](update-asked-questions) - Track asked questions
