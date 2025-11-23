from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from apps.identities.models import Identity
from enums.action_type import ActionType
from services.action_handler.models.params import (
    PersistArchiveIdentityParams,
)
from models.components.ComponentConfig import (
    ComponentConfig,
    ComponentIdentity,
)
from enums.component_type import ComponentType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def persist_archive_identity(
    coach_state: CoachState,
    params: PersistArchiveIdentityParams,
    user_message: ChatMessage,
):
    """
    Persist the archive identity component configuration to the coach message for historical display.
    This creates a display-only version of the component without interactive buttons.
    """

    # Fetch the identity and construct display object
    try:
        identity = Identity.objects.get(
            id=params.identity_id, user=coach_state.user
        )
    except Identity.DoesNotExist:
        log.warning(f"Identity {params.identity_id} not found for user {coach_state.user.id}")
        return None

    component_identities = [
        ComponentIdentity(
            id=str(identity.id),
            name=identity.name,
            category=identity.category,
        )
    ]

    display_component = ComponentConfig(
        component_type=ComponentType.ARCHIVE_IDENTITY.value,
        identities=component_identities,
    )

    # Get the coach message from the parameters
    try:
        coach_message = ChatMessage.objects.get(
            id=params.coach_message_id,
            user=coach_state.user,
            role="coach"
        )
        # Update the coach message with persistent component
        coach_message.component_config = display_component.model_dump()
        coach_message.save(update_fields=['component_config'])
        log.info(f"Persisted archive identity component to message {coach_message.id}")
    except ChatMessage.DoesNotExist:
        log.warning(f"Coach message {params.coach_message_id} not found for user {coach_state.user.id}")

    # Log the action
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.PERSIST_ARCHIVE_IDENTITY.value,
        parameters=params.model_dump(),
        result_summary=(
            f"Persisted archive identity component for identity {params.identity_id}"
        ),
        coach_message=user_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    log.info("Successfully persisted archive identity component")

    return None

