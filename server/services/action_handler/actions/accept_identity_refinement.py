from apps.identities.models import Identity
from apps.coach_states.models import CoachState
from enums.identity_state import IdentityState
from services.action_handler.models import AcceptIdentityRefinementParams


def accept_identity_refinement(
    coach_state: CoachState, params: AcceptIdentityRefinementParams
):
    """
    Set the state of the specified Identity to 'refinement_complete'.
    """
    Identity.objects.filter(id=params.id, user=coach_state.user).update(
        state=IdentityState.REFINEMENT_COMPLETE
    )
