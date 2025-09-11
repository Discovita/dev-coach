# Component Renderer System Overview

## Core Concept

The Component Renderer System allows the Coach to dynamically show interactive UI components to users instead of just text messages. The Coach "chooses" which component to show by performing specific actions, giving full control over when and how components are displayed.

## Architecture Approach

### Action-Based Component Selection
- **Coach Control**: The Coach decides to show a component by performing a specific action (e.g., `show_button_group`, `show_identity_acceptance`)
- **Phase-Based Control**: Each coaching phase can be configured with allowed component actions, controlling what components the Coach can show
- **Parameter Control**: Component actions include parameters that define the component's behavior and appearance

### Component Types & Use Cases

#### CannedResponse Component
- **Action**: `show_canned_response`
- **Use Case**: Pre-written response buttons for user convenience
- **Example**: 
  ```text
  Does that make sense?
  [Yes] [No] [Tell me more please]
  ```
- **Parameters**: `{ buttons: [{ label: string, message: string, id: string }] }`
- **Behavior**: Clicking a button sends the message as if the user typed it

#### IdentityAcceptance Component  
- **Action**: `show_identity_acceptance`
- **Use Case**: Accept/decline proposed identities
- **Parameters**: `{ identity: Identity, actions: { accept: string, decline: string } }`

#### ChoiceSelector Component
- **Action**: `show_choice_selector` 
- **Use Case**: Select from multiple options (categories, identities, etc.)
- **Parameters**: `{ options: Array<{label, value}>, multiSelect?: boolean }`

## Implementation Strategy

### Universal Component Architecture
- **Single Frontend Component**: One `UniversalComponent` that handles all component types
- **Universal API Endpoint**: Single `/coach/component-action/` endpoint for all component interactions
- **Minimal Frontend Impact**: Adding new component types requires no frontend changes
- **Flexible Parameters**: Component data structure can be anything the backend needs

### Backend Changes
1. **New Component Actions**: Add actions like `show_canned_response`, `show_identity_acceptance`, etc.
2. **Action Parameters**: Each component action includes parameters defining the component's props
3. **Phase Configuration**: Configure which component actions are allowed per coaching phase
4. **Universal Component API**: Single endpoint that handles all component interactions
5. **Component Action Handler**: Process component interactions and route to appropriate logic

### Frontend Changes
1. **Universal Component**: Single component that renders based on `component_type`
2. **Component Detection**: Detect component actions in coach responses and render accordingly
3. **Universal Submit**: All component interactions go through one API endpoint
4. **Message Integration**: Components appear alongside coach messages when present

## Benefits
- **Coach Control**: LLM decides when to show components based on context
- **Phase Management**: Control component availability per coaching phase  
- **Flexible Parameters**: Each component can be customized via action parameters
- **Consistent Architecture**: Leverages existing action handler system
- **Type Safety**: Component actions are typed and validated like other actions
- **Minimal Frontend Complexity**: Single component and API endpoint for all interactions
- **Scalable Design**: Adding new component types requires no frontend changes
- **Universal Interface**: All components use the same interaction pattern

## Component Data Structure Examples

### Canned Response Component
```json
{
  "component_type": "canned_response",
  "component_data": {
    "buttons": [
      { "label": "Yes", "message": "Yes, that makes sense", "id": "yes_001" },
      { "label": "No", "message": "No, I need more explanation", "id": "no_001" },
      { "label": "Tell me more", "message": "Can you tell me more about that?", "id": "more_001" }
    ]
  }
}
```

### Identity Acceptance Component
```json
{
  "component_type": "identity_acceptance", 
  "component_data": {
    "identity": { "id": 123, "name": "Artist", "description": "..." },
    "actions": {
      "accept": "accept_identity",
      "decline": "decline_identity"
    }
  }
}
```

## Routing Component Interactions

Two viable options exist for handling user interactions triggered by components:

- Reuse existing process-message endpoints (recommended):
  - Extend the request to optionally include `{ action, params }` in addition to `message`.
  - Validate via the Action Handler and execute through the existing registry.
  - Benefits: single execution path, consistent logging, phase allowlisting.

- Universal component endpoint (alternative):
  - Single endpoint that accepts `{ action, params }` and routes to the same Action Handler.
  - Useful if you prefer to keep component payloads fully separate from typed message requests.

In both approaches, component actions should be regular actions in the Action Handler, and components should carry typed actions/params from the backend to minimize frontend logic.

## Naming Convention for Component Actions

- Use `SHOW_XXX_COMPONENT` for any action that instructs the frontend to render a component.
- Examples: `SHOW_CANNED_RESPONSE_COMPONENT`, `SHOW_IDENTITY_ACCEPTANCE_COMPONENT`.
- Keep these actions phase-scoped via the prompt’s allowed actions.