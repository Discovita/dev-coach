from typing import List
from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from apps.identities.models import Identity
from enums.action_type import ActionType
from enums.identity_state import IdentityState
from services.action_handler.models.params import (
    PersistIAmStatementsSummaryComponentParams,
)
from models.components.ComponentConfig import (
    ComponentConfig,
    ComponentIdentity,
)
from enums.component_type import ComponentType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def persist_i_am_statements_summary_component(
    coach_state: CoachState,
    params: PersistIAmStatementsSummaryComponentParams,
    user_message: ChatMessage,
):
    """
    Persist the I Am Statements Summary component configuration to the coach message for historical display.
    This creates a display-only version of the component without interactive buttons.
    """
    log.info(
        f"Persisting I Am Statements Summary component for user {coach_state.user.id}"
    )

    # Fetch all identities that have completed their I Am statements
    identities = Identity.objects.filter(
        user=coach_state.user,
        state=IdentityState.I_AM_COMPLETE,
    ).exclude(
        state=IdentityState.ARCHIVED
    ).order_by("created_at")

    component_identities: List[ComponentIdentity] = []
    for identity in identities:
        component_identities.append(
            ComponentIdentity(
                id=str(identity.id),
                name=identity.name,
                category=identity.category,
                i_am_statement=identity.i_am_statement,
            )
        )

    display_component = ComponentConfig(
        component_type=ComponentType.I_AM_STATEMENTS_SUMMARY.value,
        identities=component_identities if component_identities else None,
    )

    try:
        coach_message = ChatMessage.objects.get(
            id=params.coach_message_id, user=coach_state.user, role="coach"
        )
        coach_message.component_config = display_component.model_dump()
        coach_message.save(update_fields=["component_config"])
        log.info(
            f"Persisted I Am Statements Summary component to message {coach_message.id}"
        )
    except ChatMessage.DoesNotExist:
        log.warning(
            f"Coach message {params.coach_message_id} not found for user {coach_state.user.id}"
        )

    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.PERSIST_I_AM_STATEMENTS_SUMMARY_COMPONENT.value,
        parameters=params.model_dump(),
        result_summary="Persisted I Am Statements Summary component",
        coach_message=user_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    log.info("Successfully persisted I Am Statements Summary component")

    return None
