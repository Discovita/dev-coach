from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from apps.identities.models import Identity
from enums.action_type import ActionType
from services.action_handler.models.params import (
    ShowNestIdentitiesParams,
)
from models.components.ComponentConfig import (
    ComponentConfig,
    ComponentButton,
    ComponentAction,
    ComponentIdentity,
)
from enums.component_type import ComponentType
from typing import List
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def show_nest_identities(
    coach_state: CoachState,
    params: ShowNestIdentitiesParams,
    coach_message: ChatMessage,
):
    """
    Show a component that displays two identities and offers Yes/No buttons to nest one under the other.
    The Yes button will trigger the NEST_IDENTITY action with both identity IDs.
    """

    identity_ids = [params.nested_identity_id, params.parent_identity_id]

    # Fetch both identities and construct display objects
    identities = Identity.objects.filter(user=coach_state.user, id__in=identity_ids)
    id_to_identity = {str(i.id): i for i in identities}

    component_identities: List[ComponentIdentity] = []
    for identity_id in identity_ids:
        identity = id_to_identity.get(identity_id)
        if identity is None:
            log.warning(
                f"Identity {identity_id} not found for user {coach_state.user.id}"
            )
            continue
        component_identities.append(
            ComponentIdentity(
                id=str(identity.id),
                name=identity.name,
                category=identity.category,
            )
        )

    buttons = [
        ComponentButton(
            label="Yes",
            # NOTE: It is imperative that the PERSIST_NEST_IDENTITIES action is first in the list of actions.
            # This is because the NEST_IDENTITY action will modify notes and archive the nested identity.
            # So we need to capture the data for the two identities before the NEST_IDENTITY action is executed.
            actions=[
                ComponentAction(
                    action=ActionType.PERSIST_NEST_IDENTITIES.value,
                    params={
                        "nested_identity_id": params.nested_identity_id,
                        "parent_identity_id": params.parent_identity_id,
                        "coach_message_id": str(coach_message.id),
                    },
                ),
                ComponentAction(
                    action=ActionType.NEST_IDENTITY.value,
                    params={
                        "nested_identity_id": params.nested_identity_id,
                        "parent_identity_id": params.parent_identity_id,
                    },
                ),
            ],
        ),
        ComponentButton(label="No"),
    ]

    component = ComponentConfig(
        component_type=ComponentType.NEST_IDENTITIES.value,
        identities=component_identities,
        buttons=buttons,
    )

    # Log the action
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.SHOW_NEST_IDENTITIES.value,
        parameters=params.model_dump(),
        result_summary=(
            f"Showed nest identities component for nested identity {params.nested_identity_id} "
            f"and parent identity {params.parent_identity_id}"
        ),
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    log.info("Successfully built nest identities component")

    return component

