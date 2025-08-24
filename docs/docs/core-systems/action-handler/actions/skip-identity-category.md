---
sidebar_position: 14
---

# Skip Identity Category

The `skip_identity_category` action adds an identity category to the skipped categories list in the [CoachState](../database/models/coach-state).

## Action Details

**Action Type**: `skip_identity_category`  
**Enum Value**: `ActionType.SKIP_IDENTITY_CATEGORY`  
**Handler Function**: `skip_identity_category()`  
**Models Used**: [CoachState](../database/models/coach-state), [Action](../database/models/action)

## What It Does

Adds an identity category to the `skipped_identity_categories` list in the user's coach state, indicating that the user has chosen to skip this category during the Identity Brainstorming phase.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | Yes | The identity category to skip (e.g., "physical_expression") |

## Implementation Steps

1. **Duplicate Check**: Checks if the category is already in the skipped list
2. **Category Addition**: Appends the category to the `skipped_identity_categories` list if not already present
3. **Save**: Saves the updated coach state
4. **Action Logging**: Records the action with details

## Example Usage

```json
{
  "action": "skip_identity_category",
  "params": {
    "category": "physical_expression"
  }
}
```

## Result

- **Success**: Adds the category to skipped list and saves the coach state
- **Duplicate**: No action if category is already skipped
- **Logging**: Records the action with result summary: "Skipped identity category 'physical_expression'"

## Related Actions

- [Unskip Identity Category](unskip-identity-category) - Remove category from skipped list
- [Select Identity Focus](select-identity-focus) - Move to next category
