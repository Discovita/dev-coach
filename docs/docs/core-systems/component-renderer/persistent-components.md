# Persistent Components

Persistent Components allow component graphics to remain visible in chat history after user interaction, providing visual continuity and context for past coaching interactions.

## Overview

The Persistent Components system extends the standard Component Renderer by storing component configurations directly in chat messages, ensuring that interactive graphics remain visible in chat history even after user interaction.

## How It Works

### Current System (Temporary Components)

1. **Component Creation**: Coach shows component with buttons
2. **User Interaction**: User clicks button → component disappears
3. **Result**: Only text message remains in chat history

### Persistent Components System

1. **Component Creation**: Coach shows component with buttons
2. **User Interaction**: User clicks button → component actions execute
3. **Persistence Action**: Additional action appends component config to message
4. **Result**: Component graphic remains visible in chat history

## Implementation Architecture

### Database Changes

The `ChatMessage` model has been updated to include an optional `component_config` field:

```python
class ChatMessage(models.Model):
    # ... existing fields ...
    component_config = models.JSONField(
        null=True, 
        blank=True,
        help_text="Optional component configuration for persistent rendering"
    )
```

### Backend Flow

1. **Component Display**: Coach performs `SHOW_XXX_COMPONENT` action
2. **Component Config Returned**: Action handler returns `ComponentConfig` with buttons
3. **User Interaction**: User clicks button with multiple actions
4. **Action Execution**: Actions execute in order (persistence action first, then business logic)
5. **Database Update**: Persistence action updates the coach message with component configuration
6. **Result**: Component graphic remains visible in chat history

### Frontend Flow

1. **Component Storage**: Active components stored in TanStack Query cache
2. **Historical Rendering**: Messages with `component_config` render persistent components
3. **Dual Rendering**: Latest message shows interactive component, history shows persistent graphics
4. **Button Handling**: Only latest component has interactive buttons

## Component Action Requirements

### Critical Requirement: All Buttons Must Have Actions

For persistent components to work correctly, **every button must have at least one action attached**. Buttons without actions will not trigger the persistence mechanism.

### Multi-Action Pattern

Each button should have multiple actions with **persistence action first**:

1. **Persistence Action**: Must be first to capture data before business logic changes it
2. **Business Action**: The main business logic (e.g., `COMBINE_IDENTITIES`)

**Critical**: The persistence action must execute first because business actions may modify or delete data that the persistence action needs to capture.

### Example: Combine Identities Component

The "Yes" button has two actions in this specific order:
1. `PERSIST_COMBINE_IDENTITIES` - Captures the two identities before they're modified
2. `COMBINE_IDENTITIES` - Performs the actual combination (deletes one, renames the other)

The "No" button has only the persistence action since no business logic is needed.

## Action Handler Implementation

### Persist Component Action

The `PERSIST_COMBINE_IDENTITIES` action handler:

1. **Receives Parameters**: Gets identity IDs and coach message ID from the action parameters
2. **Fetches Current Data**: Retrieves the current state of both identities before they're modified
3. **Creates Display-Only Component**: Builds a component config with only visual elements (no buttons or actions)
4. **Updates Message**: Saves the display-only component config to the specified coach message

**Display-Only Components**: The persistent component is intentionally stripped of all interactive elements (buttons, actions) to create a pure visual representation that remains in chat history.

The action is designed to capture the current state of identities before the business logic (combining) modifies them. This ensures the persistent component shows the original identities as they appeared when the user made their decision.

## Frontend Implementation

### Serializer Updates

The `ChatMessageSerializer` has been updated to include component configurations:

```python
class ChatMessageSerializer(serializers.ModelSerializer):
    component_config = serializers.JSONField(
        required=False,
        allow_null=True,
        help_text="Optional component configuration for persistent rendering"
    )
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'timestamp', 'component_config']
```

### Rendering Logic

The frontend rendering logic has been updated to handle both active and persistent components:

**Dual Rendering System**: The system supports both active (interactive) and persistent (display-only) components simultaneously.

- **Active Components**: Latest coach messages with `componentConfig` prop render with full interactivity
- **Persistent Components**: Historical messages with `component_config` field render as display-only graphics
- **Automatic Detection**: The system automatically determines which type to render based on the presence of `message.component_config`

**Component Priority**: When a message has both active and persistent components, the persistent component takes priority, ensuring historical accuracy.

### Utility Functions

The system includes utility functions to handle display-only components:

```typescript
// Create a display-only version of a component config
export function createDisplayOnlyComponent(componentConfig: ComponentConfig): ComponentConfig {
  return {
    component_type: componentConfig.component_type,
    texts: componentConfig.texts,
    identities: componentConfig.identities,
    // Explicitly exclude buttons and actions
    buttons: undefined,
  };
}

// Check if a component is display-only
export function isDisplayOnlyComponent(componentConfig: ComponentConfig): boolean {
  return !componentConfig.buttons || componentConfig.buttons.length === 0;
}
```

**Frontend Handling**: Display-only components automatically receive `onSelect={undefined}` to prevent any interaction, ensuring they remain purely visual.

## Development Workflow

### Adding Persistent Component Support

1. **Create Persistence Action**: Add `PERSIST_XXX_COMPONENT` action to action registry
2. **Update Component Actions**: Modify existing component actions to include persistence as first action
3. **Frontend Updates**: Update rendering logic to handle persistent components
4. **Testing**: Verify components persist correctly in chat history

**Key Implementation Steps**:
- Add persistence action to `ActionType` enum
- Create parameter model for persistence action
- Implement persistence action handler
- Update component action to include persistence action first
- Ensure `coach_message_id` is passed to persistence action

### Example: Updating Combine Identities

**Action Order is Critical**: The persistence action must be first in the action list because the business action modifies the data that needs to be captured.

**Yes Button Actions** (in this exact order):
1. `PERSIST_COMBINE_IDENTITIES` - Captures current identity data
2. `COMBINE_IDENTITIES` - Performs the combination (modifies/deletes identities)

**No Button Actions**:
1. `PERSIST_COMBINE_IDENTITIES` - Only persistence needed, no business logic

**Parameter Requirements**: The persistence action requires the `coach_message_id` to know which message to update with the persistent component.

## Benefits

- **Visual Continuity**: Components remain visible in chat history
- **Context Preservation**: Users can see what decisions were made
- **Enhanced UX**: Chat history provides visual context for past interactions
- **Flexible Implementation**: Works with existing component system
- **Backward Compatibility**: Existing components continue to work

## Technical Considerations

### Performance

- **Database Storage**: Component configs stored as JSON in chat messages
- **Frontend Rendering**: Only renders persistent components when needed
- **Memory Usage**: Minimal impact on frontend performance

### Data Integrity

- **Validation**: Component configs validated before persistence
- **Error Handling**: Graceful fallback if persistence fails
- **Cleanup**: No automatic cleanup of persistent components

### Scalability

- **Component Types**: Works with any component type
- **Action Patterns**: Reusable persistence action for all components
- **Future Extensions**: Easy to add new persistent component types

## Related Documentation

- [Component Renderer Overview](overview) - Base component system
- [Action Handler System](../action-handler/overview) - Action execution framework
- [Prompt Manager System](../prompt-manager/overview) - AI prompt management