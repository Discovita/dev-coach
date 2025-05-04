"""Handler for executing coach actions."""

from typing import Dict, List
from uuid import uuid4

from ..models.action import Action, ActionType, Param
from ..models.state import CoachState, Identity, IdentityState
from .models import (
    AcceptIdentityParams,
    AcceptIdentityRefinementParams,
    AddIdentityNoteParams,
    CreateIdentityParams,
    SelectIdentityFocusParams,
    TransitionStateParams,
    UpdateIdentityParams,
)


def _params_to_dict(params: List[Param]) -> Dict:
    """Convert a list of Param objects to a dictionary."""
    return {param.name: param.value for param in params}


def apply_actions(state: CoachState, actions: List[Action] = None) -> CoachState:
    """Apply actions to modify the coaching state."""
    new_state = state.model_copy(deep=True)
    if not actions:
        return new_state

    for action in actions:
        # Convert string action type to enum
        action_type = action.type
        if isinstance(action_type, str):
            action_type = ActionType(action_type)

        params_dict = (
            _params_to_dict(action.params)
            if isinstance(action.params, list)
            else action.params
        )

        if action_type == ActionType.CREATE_IDENTITY:
            params = CreateIdentityParams(**params_dict)
            identity_id = str(uuid4())
            new_state.identities.append(
                Identity(
                    id=identity_id,
                    description=params.description,
                    state=IdentityState.PROPOSED,
                    notes=[params.note],
                    category=params.category,
                )
            )

        elif action_type == ActionType.UPDATE_IDENTITY:
            params = UpdateIdentityParams(**params_dict)
            for identity in new_state.identities:
                if identity.id == params.id:
                    identity.description = params.description
                    break

        elif action_type == ActionType.ACCEPT_IDENTITY:
            params = AcceptIdentityParams(**params_dict)
            for identity in new_state.identities:
                if identity.id == params.id:
                    identity.state = IdentityState.ACCEPTED
                    break

        elif action_type == ActionType.ACCEPT_IDENTITY_REFINEMENT:
            params = AcceptIdentityRefinementParams(**params_dict)
            for identity in new_state.identities:
                if identity.id == params.id:
                    identity.state = IdentityState.REFINEMENT_COMPLETE
                    break

        elif action_type == ActionType.ADD_IDENTITY_NOTE:
            params = AddIdentityNoteParams(**params_dict)
            for identity in new_state.identities:
                if identity.id == params.id:
                    identity.notes.append(params.note)
                    break

        elif action_type == ActionType.TRANSITION_STATE:
            params = TransitionStateParams(**params_dict)
            new_state.current_state = params.to_state

        elif action_type == ActionType.SELECT_IDENTITY_FOCUS:
            params = SelectIdentityFocusParams(**params_dict)
            # Set the current identity ID directly
            new_state.current_identity_id = params.id

    return new_state
