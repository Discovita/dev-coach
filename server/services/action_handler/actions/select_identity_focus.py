from apps.coach_states.models import CoachState
from apps.identities.models import Identity
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import SelectIdentityFocusParams
from enums.action_type import ActionType
from enums.identity_category import IdentityCategory
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
    
    # Get human-readable labels for the categories
    old_focus_label = IdentityCategory(old_focus).label if old_focus else "None"
    new_focus_label = IdentityCategory(new_focus).label
    
    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.SELECT_IDENTITY_FOCUS.value,
        parameters=params.model_dump(),
        result_summary=f"Changed identity category focus from '{old_focus_label}' to '{new_focus_label}'",
        coach_message=coach_message,
        test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
    )
