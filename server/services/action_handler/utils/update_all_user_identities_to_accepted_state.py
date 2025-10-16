from typing import Optional

from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from enums.identity_state import IdentityState


def update_all_user_identities_to_accepted_state(coach_state: CoachState) -> int:
    """
    Set all identities for the user associated with the provided CoachState to the
    ACCEPTED state. Returns the number of identities updated.

    This utility is intended to be used during a phase transition when the
    application needs to mark all current identities as accepted.
    """
    user = coach_state.user
    return Identity.objects.filter(user=user).update(state=IdentityState.ACCEPTED)


