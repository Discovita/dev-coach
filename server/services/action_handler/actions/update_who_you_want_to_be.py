from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import UpdateWhoYouWantToBeParams
from enums.action_type import ActionType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

def update_who_you_want_to_be(
    coach_state: CoachState, params: UpdateWhoYouWantToBeParams, coach_message: ChatMessage
) -> None:
    """
    Update the who_you_want_to_be attribute of the CoachState.
    """
    coach_state.who_you_want_to_be = params.who_you_want_to_be
    coach_state.save()
    
    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.UPDATE_WHO_YOU_WANT_TO_BE.value,
        parameters=params.model_dump(),
        result_summary=f"Updated 'who you want to be' list",
        coach_message=coach_message,
        test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
    )
