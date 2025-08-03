from apps.identities.models import Identity
from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import CreateIdentityParams
from enums.action_type import ActionType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")

def create_identity(coach_state: CoachState, params: CreateIdentityParams, coach_message: ChatMessage):
    """
    Create a new Identity and link it to the user.
    Step-by-step:
    1. Check if an identity with the same name already exists for this user (case-insensitive)
    2. If it exists, log a message and return None
    3. If it doesn't exist, create the new identity and return it
    """
    # Check if identity with same name already exists (case-insensitive)
    existing_identity = Identity.objects.filter(
        user=coach_state.user,
        name__iexact=params.name
    ).first()
    
    if existing_identity:
        log.info(f"Identity with name '{params.name}' already exists for user {coach_state.user.id}. Skipping creation.")
        return None
    
    # Create new identity if it doesn't exist
    identity = Identity.objects.create(
        user=coach_state.user,
        name=params.name,
        notes=[params.note],
        category=params.category,
    )
    
    # Log the action with rich context
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.CREATE_IDENTITY.value,
        parameters=params.model_dump(),
        result_summary=f"Created identity '{identity.name}' in category '{identity.category}'",
        coach_message=coach_message,
        test_scenario=coach_state.user.test_scenario if hasattr(coach_state.user, 'test_scenario') else None
    )
    
    return identity
