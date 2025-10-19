---
sidebar_position: 1
---

# Show Introduction Canned Response Component

The `show_introduction_canned_response_component` action displays a UI component with pre-written response buttons during the introduction phase.

## Action Details

**Action Type**: `show_introduction_canned_response_component`  
**Enum Value**: `ActionType.SHOW_INTRODUCTION_CANNED_RESPONSE_COMPONENT`  
**Handler Function**: `show_introduction_canned_response_component()`  
**Models Used**: [Action](/docs/database/models/action), ComponentConfig

## What It Does

Creates and returns a component configuration that renders interactive buttons on the frontend, providing users with convenient pre-written responses during the introduction phase.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| None | - | - | This action currently takes no parameters |

## Implementation Steps

1. **Component Building**: Creates a ComponentConfig with predefined buttons
2. **Button Configuration**: Sets up standard response options (Yes, No, Tell me more)
3. **Action Integration**: Configures buttons with test actions for demonstration
4. **Action Logging**: Records the action with component details

## Example Usage

```json
{
  "action": "show_introduction_canned_response_component",
  "params": {}
}
```

## Result

- **Success**: Returns a ComponentConfig object with buttons
- **Component Type**: `ComponentType.INTRO_CANNED_RESPONSE`
- **Buttons**: Pre-configured response options
- **Logging**: Records the action with result summary: "Showed canned response component with 3 buttons"

## Component Structure

The returned component includes:
- **Component Type**: Introduction canned response
- **Buttons**: 
  - "Yes" (with test action)
  - "No" 
  - "Tell me more"

## Related Actions

- [Show Accept I Am Component](show-accept-i-am-component) - Display identity acceptance component
- [Show Combine Identities](show-combine-identities) - Display identity combination component
