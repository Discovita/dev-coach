---
sidebar_position: 2
---

# Show Accept I Am Component

The `show_accept_i_am_component` action displays a UI component that allows users to accept or continue working on an "I Am" Statement.

## Action Details

**Action Type**: `show_accept_i_am_component`  
**Enum Value**: `ActionType.SHOW_ACCEPT_I_AM_COMPONENT`  
**Handler Function**: `show_accept_i_am_component()`  
**Models Used**: [Action](/docs/database/models/action), ComponentConfig

## What It Does

Creates and returns a component configuration that renders two choice buttons for "I Am" Statement acceptance. The "I love it!" button triggers both "I Am" Statement update and acceptance actions, while "Let's keep working on it" sends the label back as a user message.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | The ID of the identity being "I Am" Statements |
| `i_am_statement` | string | Yes | The "I Am" Statement text to be accepted |

## Implementation Steps

1. **Component Building**: Creates a ComponentConfig with two choice buttons
2. **Action Configuration**: Sets up the "I love it!" button with multiple actions:
   - Updates identity "I Am" Statement
   - Accepts the identity "I Am" Statement
3. **Alternative Option**: Provides "Let's keep working on it" as alternative
4. **Action Logging**: Records the action with component details

## Example Usage

```json
{
  "action": "show_accept_i_am_component",
  "params": {
    "id": 123,
    "i_am_statement": "I am a creative visionary who brings innovative ideas to life"
  }
}
```

## Result

- **Success**: Returns a ComponentConfig object with choice buttons
- **Component Type**: `ComponentType.ACCEPT_I_AM`
- **Buttons**: 
  - "I love it!" (triggers "I Am" Statement update and acceptance)
  - "Let's keep working on it" (sends label as user message)
- **Logging**: Records the action with result summary: "Showed Accept I Am component"

## Component Structure

The returned component includes:
- **Component Type**: Accept I Am
- **Buttons**: 
  - "I love it!" with actions:
    - `UPDATE_I_AM_STATEMENT` with id and "I Am" Statement
    - `ACCEPT_I_AM_STATEMENT` with id
  - "Let's keep working on it" (no actions)

## Related Actions

- [Update "I Am" Statement](update-i-am-statement) - Update "I Am" Statement text
- [Accept "I Am" Statement](accept-i-am-statement) - Mark "I Am" Statement as complete
- [Show Introduction Canned Response Component](show-introduction-canned-response-component) - Display introduction component
