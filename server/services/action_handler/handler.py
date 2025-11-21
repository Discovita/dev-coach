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
ACTION_REGISTRY = {
    ActionType.CREATE_IDENTITY.value: create_identity,
    ActionType.CREATE_MULTIPLE_IDENTITIES.value: create_multiple_identities,
    ActionType.UPDATE_IDENTITY.value: update_identity,
    ActionType.UPDATE_IDENTITY_NAME.value: update_identity_name,
    ActionType.UPDATE_I_AM_STATEMENT.value: update_i_am_statement,
    ActionType.UPDATE_IDENTITY_VISUALIZATION.value: update_identity_visualization,
    ActionType.ACCEPT_IDENTITY.value: accept_identity,
    ActionType.ACCEPT_IDENTITY_REFINEMENT.value: accept_identity_refinement,
    ActionType.ACCEPT_IDENTITY_COMMITMENT.value: accept_identity_commitment,
    ActionType.ACCEPT_I_AM_STATEMENT.value: accept_i_am_statement,
    ActionType.ACCEPT_IDENTITY_VISUALIZATION.value: accept_identity_visualization,
    ActionType.ARCHIVE_IDENTITY.value: archive_identity,
    ActionType.NEST_IDENTITY.value: nest_identity,
    ActionType.ADD_IDENTITY_NOTE.value: add_identity_note,
    ActionType.TRANSITION_PHASE.value: transition_phase,
    ActionType.SELECT_IDENTITY_FOCUS.value: select_identity_focus,
    ActionType.SET_CURRENT_IDENTITY.value: set_current_identity,
    ActionType.SKIP_IDENTITY_CATEGORY.value: skip_identity_category,
    ActionType.UNSKIP_IDENTITY_CATEGORY.value: unskip_identity_category,
    ActionType.UPDATE_WHO_YOU_ARE.value: update_who_you_are,
    ActionType.UPDATE_WHO_YOU_WANT_TO_BE.value: update_who_you_want_to_be,
    ActionType.UPDATE_ASKED_QUESTIONS.value: update_asked_questions,
    ActionType.COMBINE_IDENTITIES.value: combine_identities,
    # Sentinel actions (not logged in the Action Table)
    ActionType.ADD_USER_NOTE.value: add_user_note,
    ActionType.UPDATE_USER_NOTE.value: update_user_note,
    ActionType.DELETE_USER_NOTE.value: delete_user_note,
    # Component actions (return ComponentConfig)
    ActionType.SHOW_INTRODUCTION_CANNED_RESPONSE_COMPONENT.value: show_introduction_canned_response_component,
    ActionType.SHOW_ACCEPT_I_AM_COMPONENT.value: show_accept_i_am_component,
    ActionType.SHOW_COMBINE_IDENTITIES.value: show_combine_identities,
    ActionType.SHOW_NEST_IDENTITIES.value: show_nest_identities,
    # Persistent component actions (return ComponentConfig)
    ActionType.PERSIST_COMBINE_IDENTITIES.value: persist_combine_identities,
    ActionType.PERSIST_NEST_IDENTITIES.value: persist_nest_identities,
}


def apply_coach_actions(
    coach_state: CoachState, response: CoachChatResponse, coach_message: ChatMessage
) -> Tuple[CoachState, Optional[ComponentConfig]]:
    """
    Applies all non-None actions from a CoachChatResponse to a CoachState object and returns the updated state.
    Each action is represented as an optional field on the response model.
    Uses the expected type for each action field for runtime type safety.
    Supported actions are defined in services.action_handler.actions and enums.action_type.

    Returns:
        Tuple of (updated_coach_state, component_config)
        - component_config will be None unless an action handler returns a ComponentConfig
    """
    log.debug(f"Response: {response}")
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
            log.action(f"Executing {action_name}")

        # Execute the action handler
        if action_name in [
            ActionType.ADD_USER_NOTE.value,
            ActionType.UPDATE_USER_NOTE.value,
            ActionType.DELETE_USER_NOTE.value,
        ]:
            # These Sentinel actions don't take coach_message as a parameter because they are not logged in the Action table
            result = handler_func(coach_state, action.params)
        else:
            # All other actions take coach_message as a parameter because they are tied to the ChatMessage by foreign key in the Action table
            result = handler_func(coach_state, action.params, coach_message)

        # Check if the action handler returned a ComponentConfig
        if isinstance(result, ComponentConfig):
            component_config = result
            log.debug(f"Action '{action_name}' returned ComponentConfig")

        log.action(f"PARAMS:\t  {action.params}")

    # Refresh from DB to ensure latest state
    coach_state.refresh_from_db()
    log.debug(f"Coach state after actions: {coach_state}")
    log.debug(f"Component config after actions: {component_config}")
    return coach_state, component_config


def apply_component_actions(
    coach_state: CoachState,
    component_actions: List[ComponentAction],
    user_message: ChatMessage,
) -> Tuple[CoachState, Optional[ComponentConfig]]:
    """
    Applies actions from component interactions (e.g., button clicks) to a CoachState object.
    This is similar to apply_actions but handles the different input format from component interactions.
    It is not currently programatically controlled, but it is the intention of this program to only perform actions that perform database updates. Sentinel actions and any actions that return ComponentConfig are not handled here.

    Args:
        coach_state: The current coach state
        component_actions: List of ComponentAction objects from component interactions
        user_message: The user chat message that triggered the component interaction

    Returns:
        updated_coach_state
    """
    log.debug(f"Component actions: {component_actions}")

    for component_action in component_actions:
        action_type = component_action.action
        action_params = component_action.params

        if not action_type:
            log.warning(f"Component action missing 'action' field: {component_action}")
            continue

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

        # Convert dictionary params to appropriate Pydantic model
        # Get the parameter model class from the action handler's signature
        import inspect
        sig = inspect.signature(handler_func)
        param_annotations = list(sig.parameters.values())
        if len(param_annotations) >= 2:  # coach_state, params, [user_message]
            params_param = param_annotations[1]  # Second parameter is params
            if params_param.annotation != inspect.Parameter.empty:
                # It's a Pydantic model, convert the dict to the model
                try:
                    action_params = params_param.annotation(**action_params)
                except Exception as e:
                    log.error(f"Failed to convert params to {params_param.annotation}: {e}")
                    continue

        # Execute the action handler
        if action_type in [
            ActionType.ADD_USER_NOTE.value,
            ActionType.UPDATE_USER_NOTE.value,
            ActionType.DELETE_USER_NOTE.value,
        ]:
            # These Sentinel actions don't take user_message as a parameter because they are not logged in the Action table
            result = handler_func(coach_state, action_params)
        else:
            # All other actions take user_message as a parameter because they get logged in the Action table
            result = handler_func(coach_state, action_params, user_message)

        log.action(f"COMPONENT PARAMS:\t  {action_params}")

    # Refresh from DB to ensure latest state
    coach_state.refresh_from_db()

    # Returning the updated coach state however, it is not currently used in the process_message endpoints.
    return coach_state
