from typing import List, Tuple, Optional
from enums.action_type import ActionType
from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from models.CoachChatResponse import CoachChatResponse
from models.components.ComponentConfig import ComponentConfig, ComponentAction
from services.action_handler.actions import *
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")

# Registry mapping ActionType values to their handler functions
# This eliminates the need for the large if-elif chain and makes adding new actions automatic
ACTION_REGISTRY = {
    ActionType.CREATE_IDENTITY.value: create_identity,
    ActionType.UPDATE_IDENTITY.value: update_identity,
    ActionType.UPDATE_IDENTITY_NAME.value: update_identity_name,
    ActionType.UPDATE_IDENTITY_AFFIRMATION.value: update_identity_affirmation,
    ActionType.UPDATE_IDENTITY_VISUALIZATION.value: update_identity_visualization,
    ActionType.ACCEPT_IDENTITY.value: accept_identity,
    ActionType.ACCEPT_IDENTITY_REFINEMENT.value: accept_identity_refinement,
    ActionType.ACCEPT_IDENTITY_AFFIRMATION.value: accept_identity_affirmation,
    ActionType.ACCEPT_IDENTITY_VISUALIZATION.value: accept_identity_visualization,
    ActionType.ADD_IDENTITY_NOTE.value: add_identity_note,
    ActionType.TRANSITION_PHASE.value: transition_phase,
    ActionType.SELECT_IDENTITY_FOCUS.value: select_identity_focus,
    ActionType.SET_CURRENT_IDENTITY.value: set_current_identity,
    ActionType.SKIP_IDENTITY_CATEGORY.value: skip_identity_category,
    ActionType.UNSKIP_IDENTITY_CATEGORY.value: unskip_identity_category,
    ActionType.UPDATE_WHO_YOU_ARE.value: update_who_you_are,
    ActionType.UPDATE_WHO_YOU_WANT_TO_BE.value: update_who_you_want_to_be,
    ActionType.UPDATE_ASKED_QUESTIONS.value: update_asked_questions,
    ActionType.ADD_USER_NOTE.value: add_user_note,  # Sentinel actions
    ActionType.UPDATE_USER_NOTE.value: update_user_note,  # Sentinel actions
    ActionType.DELETE_USER_NOTE.value: delete_user_note,  # Sentinel actions
    ActionType.SHOW_INTRODUCTION_CANNED_RESPONSE_COMPONENT.value: show_introduction_canned_response_component,
}


def apply_coach_actions(
    coach_state: CoachState, response: CoachChatResponse, coach_message: ChatMessage
) -> Tuple[CoachState, List[str], Optional[ComponentConfig]]:
    """
    Applies all non-None actions from a CoachChatResponse to a CoachState object and returns the updated state.
    Each action is represented as an optional field on the response model.
    Uses the expected type for each action field for runtime type safety.
    Supported actions are defined in services.action_handler.actions and enums.action_type.

    Returns:
        Tuple of (updated_coach_state, actions_list, component_config)
        - component_config will be None unless an action handler returns a ComponentConfig
    """
    log.debug(f"Response: {response}")
    actions = []
    component_config = None

    for action_name, value in response.model_dump(exclude_none=True).items():
        # Skip the 'message' field, as it is not an action
        if action_name == "message":
            continue

        action = getattr(response, action_name, None)
        if action is None:
            log.warning(f"Action '{action_name}' is None, skipping.")
            continue

        params = getattr(action, "params", None)
        if params is not None and hasattr(params, "model_dump"):
            params = params.model_dump()

        # NOTE: the front end "Action" interface is dependent on this structure
        actions.append({"type": action_name, "params": params})

        # Get the handler function from the registry
        handler_func = ACTION_REGISTRY.get(action_name)

        if handler_func is None:
            log.warning(f"Action '{action_name}' is not implemented in apply_actions.")
            continue

        # Get the ActionType enum for consistent logging
        try:
            action_type = ActionType.from_string(action_name)
            log.action(action_type.label)
        except ValueError:
            # Fallback if we can't find the enum
            log.action(f"Executing {action_name}")

        # Execute the action handler
        if action_name in [
            ActionType.ADD_USER_NOTE.value,
            ActionType.UPDATE_USER_NOTE.value,
            ActionType.DELETE_USER_NOTE.value,
        ]:
            # These actions don't take coach_message as a parameter
            result = handler_func(coach_state, action.params)
        else:
            # All other actions take coach_message as a parameter
            result = handler_func(coach_state, action.params, coach_message)

        # Check if the action handler returned a ComponentConfig
        if isinstance(result, ComponentConfig):
            component_config = result
            log.debug(f"Action '{action_name}' returned ComponentConfig")

        log.action(f"PARAMS:\t  {action.params}")

    # Refresh from DB to ensure latest state
    coach_state.refresh_from_db()
    return coach_state, actions, component_config


def apply_component_actions(
    coach_state: CoachState,
    component_actions: List[ComponentAction],
    user_message: ChatMessage,
) -> Tuple[CoachState, List[str], Optional[ComponentConfig]]:
    """
    Applies actions from component interactions (e.g., button clicks) to a CoachState object.
    This is similar to apply_actions but handles the different input format from component interactions.

    Args:
        coach_state: The current coach state
        component_actions: List of ComponentAction objects from component interactions
        user_message: The user chat message that triggered the component interaction

    Returns:
        Tuple of (updated_coach_state, actions_list, component_config)
        - component_config will be None unless an action handler returns a ComponentConfig
    """
    log.debug(f"Component actions: {component_actions}")
    actions = []
    component_config = None

    for component_action in component_actions:
        action_type = component_action.action
        action_params = component_action.params

        if not action_type:
            log.warning(f"Component action missing 'action' field: {component_action}")
            continue

        # Add to actions list for logging/tracking
        actions.append({"type": action_type, "params": action_params})

        # Get the handler function from the registry
        handler_func = ACTION_REGISTRY.get(action_type)

        if handler_func is None:
            log.warning(
                f"Component action '{action_type}' is not implemented in apply_component_actions."
            )
            continue

        # Get the ActionType enum for consistent logging
        try:
            action_type_enum = ActionType.from_string(action_type)
            log.action(f"Component Action: {action_type_enum.label}")
        except ValueError:
            # Fallback if we can't find the enum
            log.action(f"Executing component action: {action_type}")

        # Execute the action handler
        if action_type in [
            ActionType.ADD_USER_NOTE.value,
            ActionType.UPDATE_USER_NOTE.value,
            ActionType.DELETE_USER_NOTE.value,
        ]:
            # These actions don't take user_message as a parameter
            result = handler_func(coach_state, action_params)
        else:
            # All other actions take user_message as a parameter
            result = handler_func(coach_state, action_params, user_message)

        # Check if the action handler returned a ComponentConfig
        if isinstance(result, ComponentConfig):
            component_config = result
            log.debug(f"Component action '{action_type}' returned ComponentConfig")

        log.action(f"COMPONENT PARAMS:\t  {action_params}")

    # Refresh from DB to ensure latest state
    coach_state.refresh_from_db()
    return coach_state, actions, component_config
