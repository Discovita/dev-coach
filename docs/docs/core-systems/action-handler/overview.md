---
sidebar_position: 1
---

# Action Handler System

The Action Handler System processes and executes actions returned by the AI service. It serves as the bridge between AI responses and system state changes, ensuring that coaching interactions result in meaningful updates to user data and coaching progress.

## System Overview

The Action Handler System consists of:

1. **Action Registry**: Maps action types to their handler functions
2. **Action Handlers**: Individual functions that perform specific operations
3. **Action Models**: Pydantic models that define action parameters
4. **Action Logging**: Records all actions for audit and debugging purposes

## Core Components

### Action Registry

The system uses a registry pattern to map action types to their corresponding handler functions:

```python
ACTION_REGISTRY = {
    ActionType.CREATE_IDENTITY.value: create_identity,
    ActionType.UPDATE_IDENTITY.value: update_identity,
    ActionType.TRANSITION_PHASE.value: transition_phase,
    # ... additional mappings
}
```

### Action Processing Flow

1. **AI Response Parsing**: The AI service returns a structured response containing actions
2. **Action Validation**: Each action is validated against its parameter model
3. **Handler Execution**: The appropriate handler function is called with validated parameters
4. **State Updates**: Database models are updated according to the action logic
5. **Action Logging**: All actions are logged to the [Action](../database/models/action) model

## Integration with Prompt Manager

The Action Handler System works closely with the [Prompt Manager](../prompt-manager/overview) to:

1. **Control Available Actions**: The Prompt Manager specifies which actions are allowed for each coaching phase
2. **Generate Response Schemas**: Dynamic schemas are created based on allowed actions
3. **Validate AI Responses**: Ensures AI responses contain properly formatted action data

## Action Logging

Every action is logged with:

- **User**: The user who triggered the action
- **Action Type**: The specific action performed
- **Parameters**: The parameters passed to the action
- **Result Summary**: Human-readable description of what was accomplished
- **Coach Message**: The message that triggered the action
- **Test Scenario**: Associated test scenario (if applicable)

## Error Handling

The system includes comprehensive error handling:

- **Parameter Validation**: Ensures all required parameters are present and valid
- **Database Integrity**: Maintains referential integrity across related models
- **Graceful Degradation**: Continues processing other actions if one fails
- **Detailed Logging**: Records errors for debugging and monitoring
