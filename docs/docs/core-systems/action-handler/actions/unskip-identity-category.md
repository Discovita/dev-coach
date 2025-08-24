---
sidebar_position: 15
---

# Unskip Identity Category

The `unskip_identity_category` action removes an identity category from the skipped categories list in the [CoachState](../database/models/coach-state).

## Action Details

**Action Type**: `unskip_identity_category`  
**Enum Value**: `ActionType.UNSKIP_IDENTITY_CATEGORY`  
**Handler Function**: `unskip_identity_category()`  
**Models Used**: [CoachState](../database/models/coach-state), [Action](../database/models/action)

## What It Does

Removes an identity category from the `skipped_identity_categories` list in the user's coach state, indicating that the user wants to revisit a previously skipped category.

## Parameters

| Parameter  | Type   | Required | Description                                                   |
| ---------- | ------ | -------- | ------------------------------------------------------------- |
| `category` | string | Yes      | The identity category to unskip (e.g., "physical_expression") |

## Implementation Steps

1. **Category Removal**: Removes the category from the `skipped_identity_categories` list
2. **Save**: Saves the updated coach state
3. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "unskip_identity_category",
  "params": {
    "category": "physical_expression"
  }
}
```

## Result

- **Success**: Removes the category from skipped list and saves the coach state
- **Logging**: Records the action with result summary: "Unskipped identity category 'physical_expression'"

## Related Actions

- [Skip Identity Category](skip-identity-category) - Add category to skipped list
- [Create Identity](create-identity) - Create identity for unskipped category
