from typing import List
from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from apps.identities.models import Identity
from enums.action_type import ActionType
from services.action_handler.models.params import (
    PersistSuggestIAMStatementComponentParams,
)
from models.components.ComponentConfig import (
    ComponentConfig,
    ComponentIdentity,
    ComponentText,
)
from enums.component_type import ComponentType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def persist_suggest_i_am_statement_component(
    coach_state: CoachState,
    params: PersistSuggestIAMStatementComponentParams,
    user_message: ChatMessage,
):
    """
    Persist the suggest I Am statement component configuration to the coach message for historical display.
    This creates a display-only version of the component without interactive buttons.
    """

    identity = Identity.objects.filter(
        user=coach_state.user, id=params.identity_id
    ).first()

    component_identities: List[ComponentIdentity] = []
    if identity:
        component_identities.append(
            ComponentIdentity(
                id=str(identity.id),
                name=identity.name,
                category=identity.category,
            )
        )

    display_component = ComponentConfig(
        component_type=ComponentType.SUGGEST_I_AM_STATEMENT.value,
        texts=[
            ComponentText(
                text=params.i_am_statement,
                location="after",
                source="i_am_suggestion",
            )
        ],
        identities=component_identities if component_identities else None,
    )

    try:
        coach_message = ChatMessage.objects.get(
            id=params.coach_message_id, user=coach_state.user, role="coach"
        )
        coach_message.component_config = display_component.model_dump()
        coach_message.save(update_fields=["component_config"])
        log.info(
            f"Persisted Suggest I Am Statement component to message {coach_message.id}"
        )
    except ChatMessage.DoesNotExist:
        log.warning(
            f"Coach message {params.coach_message_id} not found for user {coach_state.user.id}"
        )

    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.PERSIST_SUGGEST_I_AM_STATEMENT_COMPONENT.value,
        parameters=params.model_dump(),
        result_summary=(
            f"Persisted Suggest I Am Statement component for identity {params.identity_id}"
        ),
        coach_message=user_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    log.info("Successfully persisted Suggest I Am Statement component")

    return None
