from django.db import transaction
from enums.action_type import ActionType
from apps.coach_states.models import CoachState
from services.action_handler.actions import (
    create_identity,
    update_identity,
    accept_identity,
    accept_identity_refinement,
    add_identity_note,
    transition_state,
    select_identity_focus,
)

# Mapping of ActionType to handler function
ACTION_HANDLERS = {
    ActionType.CREATE_IDENTITY: create_identity,
    ActionType.UPDATE_IDENTITY: update_identity,
    ActionType.ACCEPT_IDENTITY: accept_identity,
    ActionType.ACCEPT_IDENTITY_REFINEMENT: accept_identity_refinement,
    ActionType.ADD_IDENTITY_NOTE: add_identity_note,
    ActionType.TRANSITION_STATE: transition_state,
    ActionType.SELECT_IDENTITY_FOCUS: select_identity_focus,
}


def apply_actions(coach_state: CoachState, actions: list) -> CoachState:
    """
    Apply a list of actions to the given CoachState instance.
    Each action is a dict with at least a 'type' key and a 'params' dict.
    All changes are persisted to the database.
    """
    with transaction.atomic():
        for action in actions:
            action_type = ActionType.from_string(action["type"])
            params = action.get("params", {})
            handler = ACTION_HANDLERS.get(action_type)
            if handler:
                handler(coach_state, params)
            else:
                # Optionally: log or raise for unknown action
                pass

    # Refresh from DB to ensure latest state
    coach_state.refresh_from_db()
    return coach_state
