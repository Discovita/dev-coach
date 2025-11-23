from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from apps.identities.models import Identity
from enums.action_type import ActionType
from services.action_handler.models.params import (
    ShowArchiveIdentityParams,
)
from models.components.ComponentConfig import (
    ComponentConfig,
    ComponentButton,
    ComponentAction,
    ComponentIdentity,
)
from enums.component_type import ComponentType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def show_archive_identity(
    coach_state: CoachState,
    params: ShowArchiveIdentityParams,
    coach_message: ChatMessage,
):
    """
    Show a component that displays an identity and offers Yes/No buttons to archive it.
    The Yes button will trigger the ARCHIVE_IDENTITY action with the identity ID.
    """

    # Fetch the identity and construct display object
    try:
        identity = Identity.objects.get(
            id=params.identity_id, user=coach_state.user
        )
    except Identity.DoesNotExist:
        log.warning(
            f"Identity {params.identity_id} not found for user {coach_state.user.id}"
        )
        return None

    component_identities = [
        ComponentIdentity(
            id=str(identity.id),
            name=identity.name,
            category=identity.category,
        )
    ]

    buttons = [
        ComponentButton(
            label="Yes",
            # NOTE: It is imperative that the PERSIST_ARCHIVE_IDENTITY action is first in the list of actions.
            # This is because the ARCHIVE_IDENTITY action will modify the identity state.
            # So we need to capture the data for the identity before the ARCHIVE_IDENTITY action is executed.
            actions=[
                ComponentAction(
                    action=ActionType.PERSIST_ARCHIVE_IDENTITY.value,
                    params={
                        "identity_id": params.identity_id,
                        "coach_message_id": str(coach_message.id),
                    },
                ),
                ComponentAction(
                    action=ActionType.ARCHIVE_IDENTITY.value,
                    params={
                        "id": params.identity_id,
                    },
                ),
            ],
        ),
        ComponentButton(label="No"),
    ]

    component = ComponentConfig(
        component_type=ComponentType.ARCHIVE_IDENTITY.value,
        identities=component_identities,
        buttons=buttons,
    )

    # Log the action
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.SHOW_ARCHIVE_IDENTITY.value,
        parameters=params.model_dump(),
        result_summary=(
            f"Showed archive identity component for identity {params.identity_id}"
        ),
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    log.info("Successfully built archive identity component")

    return component

