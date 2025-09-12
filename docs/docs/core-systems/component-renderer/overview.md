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
- **Behavior**: Clicking a button sends the button's `actions` array to the backend

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
3. **Hook Integration**: Both `useChatMessages` and `useTestScenarioChatMessages` expose `componentConfig`
4. **Message Integration**: In `ChatMessages`, render the last coach bubble using `CoachMessageWithExtras` if `componentConfig` exists and the UI is not processing
5. **Universal Rendering (v1)**: For canned responses, render buttons from `componentConfig.buttons`; clicking sends the button's `actions` array via existing send flow

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
```json
{
  "buttons": [
    { 
      "label": "Yes",
      "actions": [
        { "action": "send_message", "params": { "message": "Yes" } }
      ]
    },
    { 
      "label": "No",
      "actions": [
        { "action": "send_message", "params": { "message": "No" } }
      ]
    },
    { 
      "label": "Tell me more",
      "actions": [
        { "action": "send_message", "params": { "message": "Tell me more" } }
      ]
    }
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

- **Component Button Clicks**: Send the button's `actions` array directly
- **Request Format**: `{ "actions": [{ "action": "send_message", "params": { "message": "Yes" } }] }`
- **Backend Processing**: Actions are processed through the existing `apply_actions` system
- **Multi-Action Support**: Each button can perform multiple actions in sequence

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