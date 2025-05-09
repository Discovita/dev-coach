"""Handler for executing coach actions."""

from uuid import uuid4

from enums.action_type import ActionType
from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from enums.identity_state import IdentityState

from .models import (
    AcceptIdentityParams,
    AcceptIdentityRefinementParams,
    AddIdentityNoteParams,
    CreateIdentityParams,
    SelectIdentityFocusParams,
    TransitionStateParams,
    UpdateIdentityParams,
)
from models.CoachChatResponse import CoachChatResponse

# TODO: Review the actions performed here and ensure they are correct. IDENTITES are wrong right now. 
def apply_actions(state: CoachState, response: CoachChatResponse) -> CoachState:
    """
    Apply actions from a CoachChatResponse to modify the coaching state.
    For each field in the response (except 'message'), if it is not None, treat it as an action and apply it.
    Args:
        state: The current CoachState instance.
        response: The CoachChatResponse object containing possible actions.
    Returns:
        The updated CoachState instance.
    """
    # Create a deep copy of the state to modify
    new_state: CoachState = (
        state.model_copy(deep=True) if hasattr(state, "model_copy") else state
    )

    # Step-by-step: Iterate over all fields except 'message'
    for field_name, value in response.__dict__.items():
        if field_name == "message" or value is None:
            continue
        # Determine the action type from the field name
        try:
            action_type = ActionType(field_name)
        except ValueError:
            # Skip unknown action types
            continue
        # Extract params from the action object
        params_dict = value.params if hasattr(value, "params") else {}
        # Apply the action based on its type
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
            new_state.current_identity_id = params.id
    return new_state
