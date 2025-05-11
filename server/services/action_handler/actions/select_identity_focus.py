from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from services.action_handler.models import SelectIdentityFocusParams


def select_identity_focus(coach_state: CoachState, params: SelectIdentityFocusParams):
    """
    Update the identity_focus field of the CoachState to the specified IdentityCategory.
    """
    new_focus = params.new_focus
    coach_state.identity_focus = new_focus
    coach_state.save()
