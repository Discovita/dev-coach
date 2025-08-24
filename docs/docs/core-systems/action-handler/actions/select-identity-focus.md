---
sidebar_position: 12
---

# Select Identity Focus

The `select_identity_focus` action updates the identity category focus in the [CoachState](/docs/database/models/coach-state).

## Action Details

**Action Type**: `select_identity_focus`  
**Enum Value**: `ActionType.SELECT_IDENTITY_FOCUS`  
**Handler Function**: `select_identity_focus()`  
**Models Used**: [CoachState](/docs/database/models/coach-state), [Action](/docs/database/models/action)

## What It Does

Updates the `identity_focus` field of the user's coach state to specify which identity category to focus on during the current coaching phase.

## Parameters

| Parameter   | Type   | Required | Description                                                      |
| ----------- | ------ | -------- | ---------------------------------------------------------------- |
| `new_focus` | string | Yes      | The identity category to focus on (e.g., "passions_and_talents") |

## Implementation Steps

1. **Focus Update**: Updates the `identity_focus` field in the [CoachState](/docs/database/models/coach-state)
2. **Save**: Saves the updated coach state
3. **Action Logging**: Records the action with old and new focus labels

## Example Usage

```json
{
  "action": "select_identity_focus",
  "params": {
    "new_focus": "passions_and_talents"
  }
}
```

## Result

- **Success**: Updates the identity focus and saves the coach state
- **Logging**: Records the action with result summary: "Changed identity category focus from 'Maker of Money' to 'Passions & Talents'"

## Related Actions

- [Transition Phase](transition-phase) - Move between coaching phases
- [Set Current Identity](set-current-identity) - Set specific identity for focus
