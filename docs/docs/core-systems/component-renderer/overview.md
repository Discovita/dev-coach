# Component Renderer System Overview

## Core Concept

The Component Renderer System allows the Coach to dynamically show interactive UI components to users instead of just text messages. The Coach "chooses" which component to show by performing specific actions, giving full control over when and how components are displayed.

## Architecture Approach

### Action-Based Component Selection
- **Coach Control**: The Coach decides to show a component by performing a specific action (e.g., `show_introduction_canned_response_component`)
- **Phase-Based Control**: Each coaching phase can be configured with allowed component actions, controlling what components the Coach can show
- **Parameter Control**: Component actions include parameters that define the component's behavior and appearance

### Component Types & Use Cases

#### CannedResponse Component (Introduction Phase)
- **Action**: `show_introduction_canned_response_component`
- **Use Case**: Pre-written response buttons for user convenience, shown for EVERY question in the Introduction script
- **Example**: 
  ```text
  Does that make sense?
  [Yes] [No] [Tell me more please]
  ```
- **Parameters**: `{ show_introduction_canned_response_component: true }` (no per-button params for this component)
- **Behavior**: Clicking a button sends the button label as the message (no additional actions)

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
- **Single Extras Renderer**: A `CoachMessageWithExtras` component that mirrors `CoachMessage` and renders extras when present
- **Minimal Frontend Impact**: Adding new component types requires minimal/no changes to message list plumbing
- **Flexible Parameters**: Component data structure is a simplified `ComponentConfig`

### Backend Changes
1. **New Component Action**: `SHOW_INTRODUCTION_CANNED_RESPONSE_COMPONENT`
2. **Action Parameters**: `ShowIntroductionCannedResponseComponentParams` with `show_introduction_canned_response_component: boolean`
3. **Phase Configuration**: Allowlist this action in the Introduction phase prompts
4. **Process via Existing Endpoints**: Reuse existing `process-message` endpoints (no new endpoint)
5. **Handler Return Value**: Action handlers return a `ComponentConfig` when a UI should be shown; `apply_actions` collects and returns it

### Frontend Changes
1. **Types**: `CoachResponse` extended with optional `component: ComponentConfig`
2. **Component Config Storage**: 
   - Store only the latest component config in query cache as `componentConfig`
   - ALWAYS set `componentConfig` on every response (either the component or `null`)
   - Query keys: `["user", "componentConfig"]` and `["testScenarioUser", userId, "componentConfig"]`
3. **Hook Integration**: Both `useChatMessages` and `useTestScenarioUserChatMessages` expose `componentConfig`
4. **Message Integration**: In `ChatMessages`, render the last coach bubble using `CoachMessageWithExtras` if `componentConfig` exists and the UI is not processing
5. **Universal Rendering (v1)**: For canned responses, render buttons from `componentConfig.buttons`; clicking sends the `label` as the message via existing send flow

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

### Canned Response Component (Simplified Payload)
```json
{
  "buttons": [
    { "label": "Yes" },
    { "label": "No" },
    { "label": "Tell me more" }
  ]
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

## Component Config Storage & Detection

### Storage Strategy
The frontend uses a "latest-only" approach for component configs:

1. **Query Cache Storage**: Component configs are stored in TanStack Query cache with keys:
   - Regular users: `["user", "componentConfig"]`
   - Test scenario users: `["testScenarioUser", userId, "componentConfig"]`

2. **Always Explicit**: Every API response sets `componentConfig` to either:
   - The component data (when present)
   - `null` (when no component in response)

3. **Automatic Cleanup**: New responses automatically replace/clear previous component configs

### Detection Logic
Components are rendered only when:
- `componentConfig` exists (not null)
- It's the last message in the conversation
- The message is from the coach
- The UI is not currently processing a message

### Implementation Details
```typescript
// In hooks' onSuccess:
queryClient.setQueryData(
  ["user", "componentConfig"],
  response.component || null  // Always set, even if null
);

// In ChatMessages:
const hasComponent = componentConfig && !isProcessingMessage;
const isLastCoachMessage = index === messages.length - 1 && message.role === "coach";

if (isLastCoachMessage && hasComponent) {
  return <CoachMessageWithExtras componentConfig={componentConfig} />
}
```

## Routing Component Interactions

We reuse the existing `process-message` endpoints for all interactions.

- For canned responses, buttons send only the `message` (the button label).
- The request serializer also supports an `actions` array for future components that need it; the payload is forwarded to the Action Handler.

## Naming Convention for Component Actions

- Use `SHOW_XXX_COMPONENT` for any action that instructs the frontend to render a component.
- Example: `SHOW_INTRODUCTION_CANNED_RESPONSE_COMPONENT`.
- Keep these actions phase-scoped via the prompt’s allowed actions.

## Multi-Action Buttons (Optional, Future-Proofing)

Buttons execute one or more actions per click. Standardize on a single request format: an `actions` array. The backend provides the payload, and the frontend posts it unchanged to the same process-message flow.

- Standard payload:
  - `{ "actions": [{ "action": string, "params": object }, ...] }`

### Execution semantics
- Validate every requested action against the current phase’s allowed actions.
- Execute sequentially via the Action Handler registry.
- Recommended: wrap in a transaction and stop on first failure; return an error that includes the index of the failing action.
- Log each action to the `Action` table as usual.

### Request serializer support
- Extend the process-message request to accept either:
  - `message` (existing), or
  - `actions` (array of `{ action, params }`).
- Enforce “exactly one of” these modes.