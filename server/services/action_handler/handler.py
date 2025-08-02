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
    transition_phase,
    select_identity_focus,
    set_current_identity,
    skip_identity_category,
    unskip_identity_category,
    update_who_you_are,
    update_who_you_want_to_be,
    add_user_note,
    update_user_note,
    delete_user_note,
)
from services.logger import configure_logging

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
            log.info("\033[94mACTION:\t  Creating identity\033[0m")
            create_identity(coach_state, action.params)
        elif action_name == ActionType.UPDATE_IDENTITY.value:
            log.info("\033[94mACTION:\t  Updating identity\033[0m")
            update_identity(coach_state, action.params)
        elif action_name == ActionType.ACCEPT_IDENTITY.value:
            log.info("\033[94mACTION:\t  Accepting identity\033[0m")
            accept_identity(coach_state, action.params)
        elif action_name == ActionType.ACCEPT_IDENTITY_REFINEMENT.value:
            log.info("\033[94mACTION:\t  Accepting identity refinement\033[0m")
            accept_identity_refinement(coach_state, action.params)
        elif action_name == ActionType.ADD_IDENTITY_NOTE.value:
            log.info("\033[94mACTION:\t  Adding identity note\033[0m")
            add_identity_note(coach_state, action.params)
        elif action_name == ActionType.TRANSITION_PHASE.value:
            log.info("\033[94mACTION:\t  Transitioning state\033[0m")
            transition_phase(coach_state, action.params)
        elif action_name == ActionType.SELECT_IDENTITY_FOCUS.value:
            log.info("\033[94mACTION:\t  Selecting identity focus\033[0m")
            select_identity_focus(coach_state, action.params)
        elif action_name == ActionType.SET_CURRENT_IDENTITY.value:
            log.info("\033[94mACTION:\t  Setting current identity\033[0m")
            set_current_identity(coach_state, action.params)
        elif action_name == ActionType.SKIP_IDENTITY_CATEGORY.value:
            log.info("\033[94mACTION:\t  Skipping identity category\033[0m")
            skip_identity_category(coach_state, action.params)
        elif action_name == ActionType.UNSKIP_IDENTITY_CATEGORY.value:
            log.info("\033[94mACTION:\t  Unskipping identity category\033[0m")
            unskip_identity_category(coach_state, action.params)
        elif action_name == ActionType.UPDATE_WHO_YOU_ARE.value:
            log.info("\033[94mACTION:\t  Updating who you are\033[0m")
            update_who_you_are(coach_state, action.params)
        elif action_name == ActionType.UPDATE_WHO_YOU_WANT_TO_BE.value:
            log.info("\033[94mACTION:\t  Updating who you want to be\033[0m")
            update_who_you_want_to_be(coach_state, action.params)
        elif action_name == ActionType.ADD_USER_NOTE.value:
            log.info("\033[94mACTION:\t  Adding user note\033[0m")
            add_user_note(coach_state, action.params)
        elif action_name == ActionType.UPDATE_USER_NOTE.value:
            log.info("\033[94mACTION:\t  Updating user note\033[0m")
            update_user_note(coach_state, action.params)
        elif action_name == ActionType.DELETE_USER_NOTE.value:
            log.info("\033[94mACTION:\t  Deleting user note\033[0m")
            delete_user_note(coach_state, action.params)
        else:
            log.warning(f"Action '{action_name}' is not implemented in apply_actions.")
            continue
        log.info(f"\033[94mPARAMS:\t  {action.params}\033[0m")

    # Refresh from DB to ensure latest state
    coach_state.refresh_from_db()
    return coach_state, actions
