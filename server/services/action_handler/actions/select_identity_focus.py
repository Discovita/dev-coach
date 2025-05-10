from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from services.action_handler.models import SelectIdentityFocusParams


def select_identity_focus(coach_state: CoachState, params: SelectIdentityFocusParams):
    """
    Update the current_identity field of the CoachState to the specified Identity.
    """
    try:
        identity = Identity.objects.get(id=params.id, user=coach_state.user)
        coach_state.current_identity = identity
        coach_state.save()
    except Identity.DoesNotExist:
        # Optionally: log or handle missing identity
        pass
