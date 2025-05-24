from apps.coach_states.models import CoachState
from services.action_handler.models import UpdateWhoYouAreParams


def update_who_you_are(coach_state: CoachState, params: UpdateWhoYouAreParams) -> None:
    """
    Update the who_you_are attribute of the CoachState.
    """
    coach_state.who_you_are = params.who_you_are
    coach_state.save()
