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
4. **Action Execution**: Primary action (e.g., `COMBINE_IDENTITIES`) executes
5. **Persistence Action**: Secondary action (e.g., `PERSIST_COMPONENT`) appends config to message
6. **Database Update**: Message is updated with component configuration

### Frontend Flow

1. **Component Storage**: Active components stored in TanStack Query cache
2. **Historical Rendering**: Messages with `component_config` render persistent components
3. **Dual Rendering**: Latest message shows interactive component, history shows persistent graphics
4. **Button Handling**: Only latest component has interactive buttons

## Component Action Requirements

### Critical Requirement: All Buttons Must Have Actions

For persistent components to work correctly, **every button must have at least one action attached**. Buttons without actions will not trigger the persistence mechanism.

### Multi-Action Pattern

Each button should have multiple actions:

1. **Primary Action**: The main business logic (e.g., `COMBINE_IDENTITIES`)
2. **Persistence Action**: Appends component config to message (e.g., `PERSIST_COMPONENT`)

### Example: Combine Identities Component

```json
{
  "component_type": "COMBINE_IDENTITIES",
  "identities": [...],
  "buttons": [
    {
      "label": "Yes",
      "actions": [
        {
          "action": "COMBINE_IDENTITIES",
          "params": {
            "identity_id_a": "uuid-1",
            "identity_id_b": "uuid-2"
          }
        },
        {
          "action": "PERSIST_COMPONENT",
          "params": {
            "component_type": "COMBINE_IDENTITIES",
            "identities": [...]
          }
        }
      ]
    },
    {
      "label": "No",
      "actions": [
        {
          "action": "PERSIST_COMPONENT",
          "params": {
            "component_type": "COMBINE_IDENTITIES",
            "identities": [...]
          }
        }
      ]
    }
  ]
}
```

## Action Handler Implementation

### Persist Component Action

The `PERSIST_COMPONENT` action handler:

1. **Receives Component Config**: Gets the component configuration to persist
2. **Updates Message**: Appends component config to the current chat message
3. **Removes Buttons**: Creates display-only version without interactive elements
4. **Database Save**: Updates the message record with persistent component

```python
def persist_component(
    coach_state: CoachState, 
    params: PersistComponentParams, 
    user_message: ChatMessage
):
    """
    Persist a component configuration to a chat message for historical display.
    Creates a display-only version without buttons.
    """
    # Get the coach message that triggered this component
    coach_message = ChatMessage.objects.filter(
        user=coach_state.user,
        role=MessageRole.COACH
    ).order_by('-timestamp').first()
    
    if coach_message:
        # Create display-only component config
        display_config = ComponentConfig(
            component_type=params.component_type,
            identities=params.identities,
            # No buttons - display only
        )
        
        # Update the coach message with persistent component
        coach_message.component_config = display_config.model_dump()
        coach_message.save(update_fields=['component_config'])
```

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

```typescript
// In ChatMessages component
const hasActiveComponent = componentConfig && !isProcessingMessage;
const hasPersistentComponent = message.component_config && !isProcessingMessage;
const isLastCoachMessage = index === messages.length - 1 && message.role === "coach";

if (isLastCoachMessage && hasActiveComponent) {
  // Render interactive component for latest message
  return <CoachMessageWithComponent componentConfig={componentConfig} />;
} else if (hasPersistentComponent) {
  // Render persistent component for historical messages
  return <CoachMessageWithComponent componentConfig={message.component_config} />;
} else {
  // Render standard message
  return <CoachMessage>{message.content}</CoachMessage>;
}
```

## Development Workflow

### Adding Persistent Component Support

1. **Create Persistence Action**: Add `PERSIST_COMPONENT` action to action registry
2. **Update Component Actions**: Modify existing component actions to include persistence
3. **Frontend Updates**: Update rendering logic to handle persistent components
4. **Testing**: Verify components persist correctly in chat history

### Example: Updating Combine Identities

```python
# In show_combine_identities action
buttons = [
    ComponentButton(
        label="Yes",
        actions=[
            ComponentAction(
                action=ActionType.COMBINE_IDENTITIES.value,
                params={
                    "identity_id_a": params.identity_id_a,
                    "identity_id_b": params.identity_id_b,
                }
            ),
            ComponentAction(
                action=ActionType.PERSIST_COMPONENT.value,
                params={
                    "component_type": ComponentType.COMBINE_IDENTITIES.value,
                    "identities": component_identities,
                }
            )
        ],
    ),
    ComponentButton(
        label="No",
        actions=[
            ComponentAction(
                action=ActionType.PERSIST_COMPONENT.value,
                params={
                    "component_type": ComponentType.COMBINE_IDENTITIES.value,
                    "identities": component_identities,
                }
            )
        ],
    ),
]
```

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