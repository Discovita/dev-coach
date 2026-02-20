---
description: Instructions for how to add a new Persistent Component to the app
globs: 
alwaysApply: false
---

# How to add a new Persistent Component

Persistent Components allow component graphics to remain visible in chat history after user interaction. This guide walks through adding a new persistent component type (e.g., "nest identities", "combine identities").

## Overview

A persistent component requires:
1. **Component Type**: Enum value for the component type
2. **Show Component Action**: Displays the component with interactive buttons
3. **Persist Component Action**: Saves component config to message for historical display
4. **Frontend Component**: React component to render the component

## Backend Implementation

### 1. Add the component type to the `ComponentType` enum in `server/enums/component_type.py`.

   ```python
   YOUR_COMPONENT_TYPE = "your_component_type", "Your Component Type"
   ```

### 2. Add two action types to the `ActionType` enum in `server/enums/action_type.py`.

   - `SHOW_YOUR_COMPONENT = "show_your_component", "Show Your Component"`
   - `PERSIST_YOUR_COMPONENT = "persist_your_component", "Persist Your Component"`

   Add these in the appropriate sections (component actions and persistent component actions).

### 3. Create Pydantic parameter models in `server/services/action_handler/models/params.py`.

   Create two parameter models:

   ```python
   class ShowYourComponentParams(BaseParamsModel):
       # Add fields needed to display the component
       # Example: identity_id_a: str = Field(..., description="...")
       pass

   class PersistYourComponentParams(BaseParamsModel):
       # Include all fields from ShowYourComponentParams
       # PLUS add:
       coach_message_id: str = Field(
           ..., description="ID of the coach message to persist the component to"
       )
   ```

   **Important**: The persist params must include `coach_message_id` and all fields needed to reconstruct the component display.

### 4. Create Pydantic action models in `server/services/action_handler/models/actions.py`.

   ```python
   class ShowYourComponentAction(BaseActionModel):
       params: ShowYourComponentParams = Field(
           ..., description="Parameters for showing the your component component."
       )

   class PersistYourComponentAction(BaseActionModel):
       params: PersistYourComponentParams = Field(
           ..., description="Parameters for persisting the your component component."
       )
   ```

### 5. Update `server/services/action_handler/models/__init__.py`.

   - Add your parameter models to imports from `.params`
   - Add your action models to imports from `.actions`
   - Add both to the `__all__` list

### 6. Add actions to `ACTION_PARAMS` in `server/services/action_handler/utils/action_instructions.py`.

   ```python
   ActionType.SHOW_YOUR_COMPONENT: {
       "description": "Show a component that displays...",
       "model": ShowYourComponentAction,
   },
   ActionType.PERSIST_YOUR_COMPONENT: {
       "description": "Persist the your component component configuration to the chat message for historical display.",
       "model": PersistYourComponentAction,
   },
   ```

   Make sure to import your action models at the top of the file.

### 7. Add actions to `ACTION_TYPE_TO_MODEL` in `server/services/action_handler/utils/dynamic_schema.py`.

   ```python
   ActionType.SHOW_YOUR_COMPONENT: ShowYourComponentAction,
   ActionType.PERSIST_YOUR_COMPONENT: PersistYourComponentAction,
   ```

   Make sure to import your action models at the top of the file.

### 8. Create the `show_your_component` handler in `server/services/action_handler/actions/components/show_your_component.py`.

   This function:
   - Fetches any data needed for display (e.g., identities, user data)
   - Creates `ComponentIdentity` or other display objects
   - Creates `ComponentButton` objects with actions
   - **CRITICAL**: The persistence action must be FIRST in the button's action list if the business action modifies data
   - Returns a `ComponentConfig` object
   - Logs the action to the Action table

   Example structure:

   ```python
   def show_your_component(
       coach_state: CoachState,
       params: ShowYourComponentParams,
       coach_message: ChatMessage,
   ):
       # Fetch data needed for display
       # Create ComponentIdentity or other display objects
       
       buttons = [
           ComponentButton(
               label="Yes",
               actions=[
                   ComponentAction(
                       action=ActionType.PERSIST_YOUR_COMPONENT.value,
                       params={
                           # Include all params from ShowYourComponentParams
                           "coach_message_id": str(coach_message.id),
                       },
                   ),
                   ComponentAction(
                       action=ActionType.YOUR_BUSINESS_ACTION.value,
                       params={
                           # Business action params
                       },
                   ),
               ],
           ),
           ComponentButton(label="No"),
       ]

       component = ComponentConfig(
           component_type=ComponentType.YOUR_COMPONENT_TYPE.value,
           # Add identities, texts, or other display data
           buttons=buttons,
       )

       # Log the action
       Action.objects.create(...)

       return component
   ```

   **Key Points**:
   - The persistence action must execute FIRST to capture data before business logic modifies it
   - Pass `coach_message.id` to the persistence action
   - Return the `ComponentConfig` object

### 9. Create the `persist_your_component` handler in `server/services/action_handler/actions/persistent_components/persist_your_component.py`.

   This function:
   - Fetches current data needed for display (before any modifications)
   - Creates a display-only `ComponentConfig` (no buttons or actions)
   - Updates the coach message's `component_config` field
   - Logs the action to the Action table
   - Returns `None`

   Example structure:

   ```python
   def persist_your_component(
       coach_state: CoachState,
       params: PersistYourComponentParams,
       user_message: ChatMessage,
   ):
       # Fetch current data (before modifications)
       # Create ComponentIdentity or other display objects
       
       display_component = ComponentConfig(
           component_type=ComponentType.YOUR_COMPONENT_TYPE.value,
           # Add identities, texts, or other display data
           # DO NOT include buttons or actions
       )

       # Get the coach message and update it
       try:
           coach_message = ChatMessage.objects.get(
               id=params.coach_message_id,
               user=coach_state.user,
               role="coach"
           )
           coach_message.component_config = display_component.model_dump()
           coach_message.save(update_fields=['component_config'])
       except ChatMessage.DoesNotExist:
           log.warning(...)

       # Log the action
       Action.objects.create(...)

       return None
   ```

   **Key Points**:
   - Create display-only component (no buttons/actions)
   - Update the coach message's `component_config` field
   - This runs BEFORE business logic that might modify data

### 10. Update `server/services/action_handler/actions/__init__.py`.

   - Import `show_your_component` from `.components.show_your_component`
   - Import `persist_your_component` from `.persistent_components.persist_your_component`
   - Add both to `__all__` list

### 11. Register actions in `server/services/action_handler/handler.py`.

   Add entries to the `ACTION_REGISTRY` dictionary:

   ```python
   ActionType.SHOW_YOUR_COMPONENT.value: show_your_component,
   ActionType.PERSIST_YOUR_COMPONENT.value: persist_your_component,
   ```

   Make sure to import both functions at the top.

### 12. Update `CoachChatResponse` model in `server/models/CoachChatResponse.py`.

   - Import your action models
   - Add optional fields:

   ```python
   show_your_component: Optional[ShowYourComponentAction] = Field(
       default=None, description="Show the your component component."
   )
   persist_your_component: Optional[PersistYourComponentAction] = Field(
       default=None, description="Persist the your component component for historical display."
   )
   ```

## Frontend Implementation

### 13. Add component type to `client/src/enums/componentType.ts`.

   ```typescript
   YOUR_COMPONENT_TYPE = "your_component_type",
   ```

### 14. Add action types to `client/src/enums/actionType.ts`.

   ```typescript
   SHOW_YOUR_COMPONENT = "show_your_component",
   PERSIST_YOUR_COMPONENT = "persist_your_component",
   ```

### 15. Create the React component in `client/src/pages/chat/components/coach-message-with-component/YourComponentConfirmation.tsx`.

   This component should:
   - Accept `coachMessage`, `config`, `onSendUserMessageToCoach`, and `disabled` props
   - Display the component data (identities, text, etc.)
   - Render buttons if `config.buttons` exists
   - Handle button clicks by calling `onSendUserMessageToCoach` with button actions

   Example structure:

   ```typescript
   export const YourComponentConfirmation: React.FC<{
     coachMessage: React.ReactNode;
     config: ComponentConfig;
     onSendUserMessageToCoach: (request: CoachRequest) => void;
     disabled: boolean;
   }> = ({ coachMessage, config, onSendUserMessageToCoach, disabled }) => {
     // Extract data from config
     const identities = (config.identities || []) as ComponentIdentity[];
     
     const hasButtons = config.buttons && config.buttons.length > 0;

     return (
       <div className="...">
         {/* Render coach message */}
         {/* Render component display (identities, etc.) */}
         
         {/* Render buttons if they exist */}
         {config.buttons && config.buttons.length > 0 && (
           <div className="...">
             {config.buttons.map((button, index) => (
               <button
                 key={index}
                 onClick={() => {
                   onSendUserMessageToCoach({
                     message: button.label,
                     actions: button.actions,
                   });
                 }}
                 disabled={disabled}
                 className="..."
               >
                 {button.label}
               </button>
             ))}
           </div>
         )}
       </div>
     );
   };
   ```

   **Key Points**:
   - Use the same styling patterns as existing components
   - Handle both interactive (with buttons) and display-only (persistent) components
   - Buttons should pass their actions to `onSendUserMessageToCoach`

### 16. Update `CoachMessageWithComponent.tsx` to handle the new component type.

   - Import your new component
   - Add a case in the switch statement:

   ```typescript
   case ComponentType.YOUR_COMPONENT_TYPE:
     return (
       <YourComponentConfirmation
         coachMessage={children}
         config={componentConfig}
         onSendUserMessageToCoach={onSendUserMessageToCoach}
         disabled={disabled}
       />
     );
   ```

## Testing Checklist

- [ ] Component displays correctly when shown
- [ ] Buttons trigger correct actions
- [ ] Persistence action executes before business action
- [ ] Component persists in chat history after interaction
- [ ] Persistent component displays without buttons (display-only)
- [ ] All actions are logged to the Action table
- [ ] Frontend component handles both interactive and persistent states

## Important Notes

1. **Action Order**: The persistence action MUST be first in button actions if the business action modifies data that needs to be captured.

2. **Display-Only Components**: Persistent components should NOT include buttons or actions - they are purely visual.

3. **Data Capture**: The persist action should capture data in its current state before any business logic modifies it.

4. **Component Config**: Both show and persist actions create `ComponentConfig` objects, but persist actions create display-only versions.

5. **Message Updates**: The persist action updates the coach message's `component_config` field, which the frontend uses to render historical components.
