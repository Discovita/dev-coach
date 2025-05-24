from apps.coach_states.models import CoachState
from services.action_handler.models import UpdateWhoYouWantToBeParams


def update_who_you_want_to_be(
    coach_state: CoachState, params: UpdateWhoYouWantToBeParams
) -> None:
    """
    Update the who_you_want_to_be attribute of the CoachState.
    """
    coach_state.who_you_want_to_be = params.who_you_want_to_be
    coach_state.save()
