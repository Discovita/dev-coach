from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from apps.identities.models import Identity
from enums.action_type import ActionType
from services.action_handler.models.params import (
    PersistNestIdentitiesParams,
)
from models.components.ComponentConfig import (
    ComponentConfig,
    ComponentIdentity,
)
from enums.component_type import ComponentType
from typing import List
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def persist_nest_identities(
    coach_state: CoachState,
    params: PersistNestIdentitiesParams,
    user_message: ChatMessage,
):
    """
    Persist the nest identities component configuration to the coach message for historical display.
    This creates a display-only version of the component without interactive buttons.
    """

    identity_ids = [params.nested_identity_id, params.parent_identity_id]

    # Fetch both identities and construct display objects
    identities = Identity.objects.filter(user=coach_state.user, id__in=identity_ids)
    id_to_identity = {str(i.id): i for i in identities}

    component_identities: List[ComponentIdentity] = []
    for identity_id in identity_ids:
        identity = id_to_identity.get(identity_id)
        if identity is None:
            log.warning(f"Identity {identity_id} not found for user {coach_state.user.id}")
            continue
        component_identities.append(
            ComponentIdentity(
                id=str(identity.id),
                name=identity.name,
                category=identity.category,
            )
        )

    display_component = ComponentConfig(
        component_type=ComponentType.NEST_IDENTITIES.value,
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
        log.info(f"Persisted nest identities component to message {coach_message.id}")
    except ChatMessage.DoesNotExist:
        log.warning(f"Coach message {params.coach_message_id} not found for user {coach_state.user.id}")

    # Log the action
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.PERSIST_NEST_IDENTITIES.value,
        parameters=params.model_dump(),
        result_summary=(
            f"Persisted nest identities component for nested identity {params.nested_identity_id} "
            f"and parent identity {params.parent_identity_id}"
        ),
        coach_message=user_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    log.info("Successfully persisted nest identities component")

    return None

