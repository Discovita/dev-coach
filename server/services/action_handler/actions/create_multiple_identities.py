from apps.identities.models import Identity
from apps.coach_states.models import CoachState
from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from services.action_handler.models import CreateMultipleIdentitiesParams
from enums.action_type import ActionType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def create_multiple_identities(
    coach_state: CoachState, params: CreateMultipleIdentitiesParams, coach_message: ChatMessage
):
    """
    Create multiple new Identities and link them to the user.
    Step-by-step:
    1. For each identity in the list, check if an identity with the same name already exists for this user (case-insensitive)
    2. If it exists, log a message and skip that identity
    3. If it doesn't exist, create the new identity
    4. Log a single action with summary of all identities created
    """
    created_identities = []
    skipped_identities = []
    
    for identity_data in params.identities:
        # Check if identity with same name already exists (case-insensitive)
        existing_identity = Identity.objects.filter(
            user=coach_state.user, name__iexact=identity_data.name
        ).first()

        if existing_identity:
            log.warning(
                f"Identity with name '{identity_data.name}' already exists for user {coach_state.user.id}. Skipping creation."
            )
            skipped_identities.append(identity_data.name)
            continue

        # Create new identity if it doesn't exist
        identity = Identity.objects.create(
            user=coach_state.user,
            name=identity_data.name,
            notes=[identity_data.note],
            category=identity_data.category,
        )
        created_identities.append(identity)

    # Log the action with rich context
    result_summary = f"Created {len(created_identities)} identities"
    if created_identities:
        identity_names = [identity.name for identity in created_identities]
        result_summary += f": {', '.join(identity_names)}"
    if skipped_identities:
        result_summary += f". Skipped {len(skipped_identities)} duplicates: {', '.join(skipped_identities)}"

    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.CREATE_MULTIPLE_IDENTITIES.value,
        parameters=params.model_dump(),
        result_summary=result_summary,
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    return created_identities
