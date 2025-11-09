# Component Renderer System Overview

## Core Concept

The Component Renderer System allows the Coach to dynamically show interactive UI components to users instead of just text messages. The Coach "chooses" which component to show by performing specific actions controlled by the [Action Handler](/docs/core-systems/action-handler/overview), giving full control over when and how components are displayed.

## How It Works

### Backend Flow

1. **Action Registration**: Component actions are registered in the `ACTION_REGISTRY` in `server/services/action_handler/handler.py` as regualr actions.
2. **Prompt Integration**: The action is added to the prompt's Allowed Actions list with instructions on when to use it
3. **Component Creation**: When the Coach decides to show a component, it performs the action that will send the required information to the frontend to render the component (e.g., `SHOW_COMBINE_IDENTITIES`)
4. **Handler Execution**: The action handler function constructs a `ComponentConfig` object and returns it
5. **Response Integration**: The `apply_coach_actions` function collects the `ComponentConfig` and includes it in the API response under the `component` field

### Frontend Flow

1. **Component Storage**: Component configs are stored in TanStack Query cache with key `["user", "componentConfig"]`
2. **Component Type Mapping**: Each `component_type` in the config maps to a specific React component
3. **Latest-Only Rendering**: Components are only rendered on the last coach message when not processing
4. **Button Handling**: The `CoachMessageWithComponent` component automatically handles button clicks
5. **Request Assembly**: When a button is clicked, a `CoachRequest` object is assembled and sent to the backend

### Component Interaction

- Every component has buttons that users can click
- Buttons can have actions that execute when clicked, or just send the button label as a message
- When clicked, the frontend sends both the button label as `message` and any `actions` to the backend
- The backend processes the message and executes any component actions via `apply_component_actions`

## Implementation Details

### Backend Implementation

The component system is built on top of the existing [Action Handler](/docs/core-systems/action-handler/overview) system:

1. **Action Registration**: Component actions are registered in the `ACTION_REGISTRY` in `server/services/action_handler/handler.py`
2. **Handler Functions**: Each component action has a handler function that returns a `ComponentConfig` object
3. **Response Integration**: The `apply_coach_actions` function collects `ComponentConfig` objects and includes them in the API response under the `component` field
4. **Component Actions Processing**: The `apply_component_actions` function handles button clicks by executing the actions defined in the component buttons

### Frontend Implementation

The frontend uses a "latest-only" approach for component rendering:

1. **Type Definitions**: `CoachResponse` includes an optional `component: ComponentConfig` field
2. **State Management**: Component configs are stored in TanStack Query cache with key `["user", "componentConfig"]`
3. **Component Type Mapping**: Each `component_type` maps to a specific React component:
   - `COMBINE_IDENTITIES` → `CombineIdentitiesConfirmation`
   - `INTRO_CANNED_RESPONSE` → `IntroCannedResponseComponent`
   - Additional component types can be added by extending the switch statement
4. **Rendering Logic**: Components are only rendered on the last coach message when not processing
5. **Button Handling**: The `CoachMessageWithComponent` component automatically handles button clicks

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

## Component Config Storage & Detection

### Storage Strategy

The frontend uses a "latest-only" approach for component configs:

1. **Query Cache Storage**: Component configs are stored in TanStack Query cache with key `["user", "componentConfig"]` so that we can store the component config for the last coach message and use it to render the component.
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

// In CoachMessageWithComponent - component type mapping:
switch (componentConfig.component_type) {
  case ComponentType.COMBINE_IDENTITIES:
    return <CombineIdentitiesConfirmation {...props} />;
  case ComponentType.INTRO_CANNED_RESPONSE:
    return <IntroCannedResponseComponent {...props} />;
  default:
    return null;
}
```


## Architectural Decision: Actions in Component Config

### Why Actions Are Included in Component Configs

We chose to include `action` and `params` directly in the component button configuration rather than using a centralized button ID registry. This decision was made for several key reasons:

#### **1. Component Isolation**

- Each action handler (e.g., `show_combine_identities`) is responsible for its own component config
- All logic for that component type lives in one place
- Easy to find and modify component behavior without hunting through registries

#### **2. AI Flexibility**

- The AI can potentially customize button labels and actions based on context
  - We are not currently doing this, but it is possible to do so in the future.
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

## Naming Convention for Component Actions

- Use `SHOW_XXX_COMPONENT` for any action that instructs the frontend to render a component.
- Example: `SHOW_COMBINE_IDENTITIES`, `SHOW_INTRODUCTION_CANNED_RESPONSE_COMPONENT`.
- Keep these actions phase-scoped via the prompt's allowed actions.

## Development Workflow

### Adding a New Component Type

1. **Create Action Handler**: Add a new action handler function that returns a `ComponentConfig`
2. **Register Action**: Add the action to `ActionType` enum and `ACTION_REGISTRY`
3. **Add Parameters**: Create parameter model for the action (if needed)
4. **Update Prompts**: Add the action to the appropriate phase's allowed actions list
5. **Add Instructions**: Update prompt instructions to tell the Coach when and how to use the action
6. **Create Frontend Component**: Add a new React component for the component type
7. **Update Component Mapping**: Add the new component type to the switch statement in `CoachMessageWithComponent`

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
