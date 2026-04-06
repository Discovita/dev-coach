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

Appends a single question to the `asked_questions` list in the user's coach state, if it is not already present. This tracks which questions have been asked during the Get To Know You phase to prevent asking the same question twice.

## Parameters

| Parameter        | Type                    | Required | Description                                                     |
| ---------------- | ----------------------- | -------- | --------------------------------------------------------------- |
| `asked_question` | GetToKnowYouQuestions   | Yes      | A single question enum value to add to the asked questions list |

**Valid `GetToKnowYouQuestions` values:**
- `background_upbringing` - Background/upbringing
- `family_structure` - Family structure (siblings, parents, children, etc.)
- `work_living` - Work or what they do for a living
- `hobbies_interests` - Hobbies or interests
- `why_here_hopes` - Why are you here? What do you hope to get out of this coaching?

## Implementation Steps

1. **Enum Conversion**: Converts the enum to its string value for storage
2. **Duplicate Check**: Checks if the question is already in the existing list
3. **Append**: If not already present, appends the question value to the existing `asked_questions` list
4. **Save**: Saves the updated coach state
5. **Action Logging**: Records the action with details (only when a new question was actually added)

## Example Usage

```json
{
  "action": "update_asked_questions",
  "params": {
    "asked_question": "background_upbringing"
  }
}
```

## Result

- **Success**: Appends the question to the asked_questions list and saves the coach state
- **Already Present**: Skips update if the question is already in the list (idempotency protection). No Action row is created.
- **Logging**: Records the action with result summary: "Added question 'background_upbringing' to asked questions list"

## Related Actions

- [Update Who You Are](update-who-you-are) - Update current self-description identities
- [Update Who You Want to Be](update-who-you-want-to-be) - Update aspirational identities
