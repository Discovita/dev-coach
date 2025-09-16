# Component Renderer System Overview

## Core Concept

The Component Renderer System allows the Coach to dynamically show interactive UI components to users instead of just text messages. The Coach "chooses" which component to show by performing specific actions controlled by the [Action Handler](/docs/core-systems/action-handler/overview), giving full control over when and how components are displayed.

## Architecture Approach

### How it works

- The developer [adds an action](/docs/how-to/how-to-add-a-new-coach-action) to the [Action Handler](/docs/core-systems/action-handler/overview) that will be used to show a component. This action will function just like any other action. It's parameters could be as simple as a boolean or could contain more complex parms such as an identity object or id.
- This action is added to the prompt in the Allowed Actions list.
- Instructions for how and when to use the action are added to the prompt. The Coach will need context on when to show the component and what parameters to pass to the action.
- When the Coach decides to show the component, this action will be handled by the [Action Handler](/docs/core-systems/action-handler/overview). The actual function associated with this action will construct a [ComponentConfig](/docs/core-systems/component-renderer/component-config) object that will be returned to the frontend and rendered by the [CoachMessageWithComponent](/docs/core-systems/component-renderer/coach-message-with-component) component.
- Every component render will have a list of buttons that the user can choose from. At a bare minimum, these buttons will pass their `label` to the backend and the contents of that label will be sent as the `message` to the backend.
  - This functionality is baked into the CoachMessageWithComponent and does not need to be explicitly handled by the developer.
- The ComponentConfig can also accept a list of actions for each button that will be executed when the button is clicked. For flexibility, the buttons can accept more than one action.
- When the button is clicked, a [CoachRequest](/docs/frontend/types/coach-request) object is assembled on the front end and sent to the backend. Depending on the [ComponentConfig](/docs/core-systems/component-renderer/component-config), the `message` and/or `actions` will be sent to the backend.
- The backend will parse this request and execute the receiving of the message and if there are any component actions to perform, it will pass those to the [Action Handler](/docs/core-systems/action-handler/overview) to be executed via the `apply_component_actions` function.
- Therefore, each component action will require two or more actions - one to allow the Coach to show the actual component to the user and any actions needed to support the desired behavior of the component.
  - It is possible with this framework to allow the Coach to create the ComponentConfig directly (or certain parts of it). For example, you could allow the Coach to choose the button lables while the actions are hardcoded in the action function. You could potentially allow the Coach to choose the button labels and the actions from a list of options. This is not currently implemented and each current component action hardcodes the button labels and actions.

## Implementation Details

### Backend Implementation

The component system is built on top of the existing [Action Handler](/docs/core-systems/action-handler/overview) system:

1. **Action Registration**: Component actions are registered in the `ACTION_REGISTRY` just like any other action
2. **Handler Functions**: Each component action has a handler function that returns a `ComponentConfig` object
3. **Response Integration**: The `apply_coach_actions` function collects `ComponentConfig` objects and includes them in the API response under the `component` field
4. **Component Actions Processing**: The `apply_component_actions` function handles button clicks by executing the actions defined in the component buttons

### Frontend Implementation

The frontend uses a "latest-only" approach for component rendering:

1. **Type Definitions**: `CoachResponse` includes an optional `component: ComponentConfig` field
2. **State Management**: Component configs are stored in TanStack Query cache with key `["user", "componentConfig"]`
3. **Rendering Logic**: Components are only rendered on the last coach message when not processing
4. **Button Handling**: The `CoachMessageWithComponent` component automatically handles button clicks

## Benefits

- **Coach Control**: LLM decides when to show components based on context
- **Phase Management**: Control component availability per coaching phase
- **Flexible Parameters**: Each component can be customized via action parameters
- **Consistent Architecture**: Leverages existing action handler system
- **Type Safety**: Component actions are typed and validated like other actions
- **Minimal Frontend Complexity**: Single component and API endpoint for all interactions
- **Scalable Design**: Adding new component types requires no frontend changes
- **Universal Interface**: All components use the same interaction pattern
- **Clean State Management**: `componentConfig` is always explicit (component or null), no stale configs
- **Latest-Only Rendering**: Components only appear on the most recent coach message, keeping history clean

## Component Data Structure Examples

### Canned Response Component (With Actions)

Note: `actions` on a button are optional. If omitted, the UI still sends a `message` equal to the button label when clicked.

```json
{
  "buttons": [
    {
      "label": "Yes",
      "actions": [
        { "action": "test_action", "params": { "test_param": "test_value" } }
      ]
    },
    {
      "label": "No"
    },
    {
      "label": "Tell me more"
    }
  ]
}
```


## Component Config Storage & Detection

### Storage Strategy

The frontend uses a "latest-only" approach for component configs:

1. **Query Cache Storage**: Component configs are stored in TanStack Query cache with key `["user", "componentConfig"]`
2. **Always Explicit**: Every API response sets `componentConfig` to either the component data (when present) or `null`
3. **Automatic Cleanup**: New responses automatically replace/clear previous component configs

### Detection Logic

Components are rendered only when:
- `componentConfig` exists (not null)
- It's the last message in the conversation
- The message is from the coach
- The UI is not currently processing a message

### Implementation Details

```typescript
// In useChatMessages hook onSuccess:
queryClient.setQueryData(
  ["user", "componentConfig"],
  response.component || null // Always set, even if null
);

// In ChatMessages component:
const hasComponent = componentConfig && !isProcessingMessage;
const isLastCoachMessage = index === messages.length - 1 && message.role === "coach";

if (isLastCoachMessage && hasComponent) {
  return <CoachMessageWithComponent componentConfig={componentConfig} />;
}
```


## Architectural Decision: Actions in Component Config

### Why Actions Are Included in Component Configs

We chose to include `action` and `params` directly in the component button configuration rather than using a centralized button ID registry. This decision was made for several key reasons:

#### **1. Component Isolation**

- Each action handler (`show_introduction_canned_response_component`) is responsible for its own component config
- All logic for that component type lives in one place
- Easy to find and modify component behavior without hunting through registries

#### **2. AI Flexibility**

- The AI can potentially customize button labels and actions based on context
- Future components could have dynamic parameters based on user state
- No need to predefine every possible button configuration

#### **3. Developer Experience**

- No need to maintain a separate registry of button IDs
- No risk of mismatched button IDs between frontend and backend
- Clear, self-contained component definitions

#### **4. Scalability**

- Adding new component types is straightforward - just create a new action handler
- Each component can have its own unique button structure and behavior
- No centralized configuration to maintain

### Alternative Approaches Considered

**Option A: Button ID Registry**

- **Pros**: More secure, less data transfer
- **Cons**: Centralized complexity, harder to maintain, less flexible for AI customization

**Option B: Direct Action Execution**

- **Pros**: Simpler frontend
- **Cons**: Less flexible, harder to customize per component

**Chosen Approach: Actions in Config**

- **Pros**: Component isolation, AI flexibility, developer experience, scalability
- **Cons**: Slightly more data transfer (minimal impact)

## Naming Convention for Component Actions

- Use `SHOW_XXX_COMPONENT` for any action that instructs the frontend to render a component.
- Example: `SHOW_INTRODUCTION_CANNED_RESPONSE_COMPONENT`.
- Keep these actions phase-scoped via the prompt's allowed actions.

## Development Workflow

### Adding a New Component Type

1. **Create Action Handler**: Add a new action handler function that returns a `ComponentConfig`
2. **Register Action**: Add the action to `ActionType` enum and `ACTION_REGISTRY`
3. **Add Parameters**: Create parameter model for the action (if needed)
4. **Update Prompts**: Add the action to the appropriate phase's allowed actions list
5. **Add Instructions**: Update prompt instructions to tell the Coach when and how to use the action

### Request Format & Processing

The process-message request accepts `message` and/or `actions` (at least one must be provided). When component buttons are clicked:

- **Request Format**:
  - With actions: `{"message": "<button label>", "actions": [{ "action": string, "params": object }]}`
  - Without actions: `{"message": "<button label>"}`
- **Backend Processing**:
  - The `message` field is processed normally (added to chat history)
  - The `actions` array (if present) is processed by `apply_component_actions`
  - Any new `ComponentConfig` returned by action handlers is included in the response
- **Multi-Action Support**: Each button can perform multiple actions in sequence
