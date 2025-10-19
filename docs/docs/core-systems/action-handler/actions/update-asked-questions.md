---
sidebar_position: 18
---

# Update Asked Questions

The `update_asked_questions` action updates the list of questions asked during the Get To Know You phase in the [CoachState](/docs/database/models/coach-state).

## Action Details

**Action Type**: `update_asked_questions`  
**Enum Value**: `ActionType.UPDATE_ASKED_QUESTIONS`  
**Handler Function**: `update_asked_questions()`  
**Models Used**: [CoachState](/docs/database/models/coach-state), [Action](/docs/database/models/action)

## What It Does

Updates the `asked_questions` field in the user's coach state with a complete list of questions that have been asked during the Get To Know You phase. This action requires the complete list, not just changes.

## Parameters

| Parameter   | Type  | Required | Description                                 |
| ----------- | ----- | -------- | ------------------------------------------- |
| `questions` | array | Yes      | Complete list of asked question enum values |

## Implementation Steps

1. **Enum Conversion**: Converts enum objects to their string values for storage
2. **Duplicate Check**: Ensures no duplicates (idempotency protection for React Strict Mode)
3. **Change Detection**: Only updates if there are actual changes to prevent unnecessary saves
4. **Questions List Update**: Updates the `asked_questions` field with the complete list of questions
5. **Save**: Saves the updated coach state
6. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "update_asked_questions",
  "params": {
    "questions": ["biggest_challenge", "success_looks_like", "core_values"]
  }
}
```

## Result

- **Success**: Updates the asked_questions list and saves the coach state
- **No Change**: Skips update if questions list is unchanged (idempotency protection)
- **Logging**: Records the action with result summary: "Updated asked questions list with X questions"

## Related Actions

- [Update Who You Are](update-who-you-are) - Update current self-description identities
- [Update Who You Want to Be](update-who-you-want-to-be) - Update aspirational identities
