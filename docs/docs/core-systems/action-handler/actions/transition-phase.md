---
sidebar_position: 11
---

# Transition Phase

The `transition_phase` action updates the current coaching phase in the [CoachState](../database/models/coach-state).

## Action Details

**Action Type**: `transition_phase`  
**Enum Value**: `ActionType.TRANSITION_PHASE`  
**Handler Function**: `transition_phase()`  
**Models Used**: [CoachState](../database/models/coach-state), [Action](../database/models/action)

## What It Does

Updates the `current_phase` field of the user's coach state to move between coaching phases (e.g., from "identity_brainstorming" to "identity_refinement").

## Parameters

| Parameter  | Type   | Required | Description                                |
| ---------- | ------ | -------- | ------------------------------------------ |
| `to_phase` | string | Yes      | The target coaching phase to transition to |

## Implementation Steps

1. **Phase Update**: Updates the `current_phase` field in the [CoachState](../database/models/coach-state)
2. **Save**: Saves the updated coach state
3. **Action Logging**: Records the action with old and new phase labels

## Example Usage

```json
{
  "action": "transition_phase",
  "params": {
    "to_phase": "identity_refinement"
  }
}
```

## Result

- **Success**: Updates the coaching phase and saves the coach state
- **Logging**: Records the action with result summary: "Transitioned from 'Identity Brainstorming' to 'Identity Refinement'"

## Related Actions

- [Select Identity Focus](select-identity-focus) - Set identity category focus for the new phase
- [Set Current Identity](set-current-identity) - Set current identity for refinement phase
