from typing import List, Tuple
from enums.action_type import ActionType
from apps.coach_states.models import CoachState
from models.CoachChatResponse import CoachChatResponse
from services.action_handler.actions import (
    create_identity,
    update_identity,
    accept_identity,
    accept_identity_refinement,
    add_identity_note,
    transition_state,
    select_identity_focus,
    skip_identity_category,
    update_who_you_are,
    update_who_you_want_to_be,
)
from services.logger import configure_logging

# Mapping of ActionType to handler function
ACTION_HANDLERS = {
    ActionType.CREATE_IDENTITY: create_identity,
    ActionType.UPDATE_IDENTITY: update_identity,
    ActionType.ACCEPT_IDENTITY: accept_identity,
    ActionType.ACCEPT_IDENTITY_REFINEMENT: accept_identity_refinement,
    ActionType.ADD_IDENTITY_NOTE: add_identity_note,
    ActionType.TRANSITION_STATE: transition_state,
    ActionType.SELECT_IDENTITY_FOCUS: select_identity_focus,
    ActionType.SKIP_IDENTITY_CATEGORY: skip_identity_category,
    ActionType.UPDATE_WHO_YOU_ARE: update_who_you_are,
    ActionType.UPDATE_WHO_YOU_WANT_TO_BE: update_who_you_want_to_be,
}

log = configure_logging(__name__, log_level="DEBUG")


def apply_actions(
    coach_state: CoachState, response: CoachChatResponse
) -> Tuple[CoachState, List[str]]:
    """
    Applies all non-None actions from a CoachChatResponse to a CoachState object and returns the updated state.
    Each action is represented as an optional field on the response model.
    Uses the expected type for each action field for runtime type safety.
    Supported actions are defined in services.action_handler.actions and enums.action_type.
    """
    log.fine(f"Applying actions to coach state: {coach_state.id}")
    log.debug(f"Response: {response}")
    actions = []
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
        # Example: handle each action type explicitly
        if action_name == ActionType.CREATE_IDENTITY.value:
            # log.info("\033[94mACTION:\t  Creating identity\033[0m")
            log.info("ACTION: Creating identity")
            create_identity(coach_state, action.params)
        elif action_name == ActionType.UPDATE_IDENTITY.value:
            log.info("ACTION: Updating identity")
            update_identity(coach_state, action.params)
        elif action_name == ActionType.ACCEPT_IDENTITY.value:
            log.info("ACTION: Accepting identity")
            accept_identity(coach_state, action.params)
        elif action_name == ActionType.ACCEPT_IDENTITY_REFINEMENT.value:
            log.info("ACTION: Accepting identity refinement")
            accept_identity_refinement(coach_state, action.params)
        elif action_name == ActionType.ADD_IDENTITY_NOTE.value:
            log.info("ACTION: Adding identity note")
            add_identity_note(coach_state, action.params)
        elif action_name == ActionType.TRANSITION_STATE.value:
            log.info("ACTION: Transitioning state")
            transition_state(coach_state, action.params)
        elif action_name == ActionType.SELECT_IDENTITY_FOCUS.value:
            log.info("ACTION: Selecting identity focus")
            select_identity_focus(coach_state, action.params)
        elif action_name == ActionType.SKIP_IDENTITY_CATEGORY.value:
            log.info("ACTION: Skipping identity category")
            skip_identity_category(coach_state, action.params)
        elif action_name == ActionType.UPDATE_WHO_YOU_ARE.value:
            log.info("ACTION: Updating who you are")
            update_who_you_are(coach_state, action.params)
        elif action_name == ActionType.UPDATE_WHO_YOU_WANT_TO_BE.value:
            log.info("ACTION: Updating who you want to be")
            update_who_you_want_to_be(coach_state, action.params)
        else:
            log.warning(f"Action '{action_name}' is not implemented in apply_actions.")
            continue

    # Refresh from DB to ensure latest state
    coach_state.refresh_from_db()
    return coach_state, actions
