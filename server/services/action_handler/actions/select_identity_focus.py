from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import SelectIdentityFocusParams
from enums.action_type import ActionType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

def select_identity_focus(coach_state: CoachState, params: SelectIdentityFocusParams, coach_message: ChatMessage):
    """
    Update the identity_focus field of the CoachState to the specified IdentityCategory.
    """
    old_focus = coach_state.identity_focus
    new_focus = params.new_focus
    coach_state.identity_focus = new_focus
    coach_state.save()
    
    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.SELECT_IDENTITY_FOCUS.value,
        parameters=params.model_dump(),
        result_summary=f"Changed identity category focus from '{old_focus}' to '{new_focus}'",
        coach_message=coach_message,
        test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
    )
