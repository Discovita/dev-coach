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

1. **Questions List Update**: Updates the `asked_questions` field with the complete list of questions
2. **Save**: Saves the updated coach state
3. **Action Logging**: Records the action with details

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
- **Logging**: Records the action with result summary: "Updated asked questions"

## Related Actions

- [Update Who You Are](update-who-you-are) - Update current self-description identities
- [Update Who You Want to Be](update-who-you-want-to-be) - Update aspirational identities
