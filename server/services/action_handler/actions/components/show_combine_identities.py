from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from apps.identities.models import Identity
from enums.action_type import ActionType
from services.action_handler.models.params import (
    ShowCombineIdentitiesParams,
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


def show_combine_identities(
    coach_state: CoachState,
    params: ShowCombineIdentitiesParams,
    coach_message: ChatMessage,
):
    """
    Show a component that displays two identities and offers Yes/No buttons to combine them.
    The Yes button will trigger the COMBINE_IDENTITIES action with both identity IDs.
    """

    identity_ids = [params.identity_id_a, params.identity_id_b]

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
            # NOTE: It is imperitive that the PERSIST_COMBINE_IDENTITIES action is first in the list of actions.
            # This is because the COMBINE_IDENTITIES action will actually delete one of the identities and change
            # the name of the other identity. So we need to capture the data for the two identities before the
            # COMBINE_IDENTITIES action is executed.
            actions=[
                ComponentAction(
                    action=ActionType.PERSIST_COMBINE_IDENTITIES.value,
                    params={
                        "identity_id_a": params.identity_id_a,
                        "identity_id_b": params.identity_id_b,
                        "coach_message_id": str(coach_message.id),
                    },
                ),
                ComponentAction(
                    action=ActionType.COMBINE_IDENTITIES.value,
                    params={
                        "identity_id_a": params.identity_id_a,
                        "identity_id_b": params.identity_id_b,
                    },
                ),
            ],
        ),
        ComponentButton(label="No"),
    ]

    component = ComponentConfig(
        component_type=ComponentType.COMBINE_IDENTITIES.value,
        identities=component_identities,
        buttons=buttons,
    )

    # Log the action
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.SHOW_COMBINE_IDENTITIES.value,
        parameters=params.model_dump(),
        result_summary=(
            f"Showed combine identities component for identities {params.identity_id_a} and {params.identity_id_b}"
        ),
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    log.info("Successfully built combine identities component")

    return component
