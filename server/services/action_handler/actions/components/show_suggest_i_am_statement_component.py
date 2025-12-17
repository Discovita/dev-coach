from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from apps.identities.models import Identity
from enums.action_type import ActionType
from services.action_handler.models.params import (
    ShowSuggestIAMStatementComponentParams,
)
from models.components.ComponentConfig import (
    ComponentConfig,
    ComponentButton,
    ComponentAction,
    ComponentIdentity,
    ComponentText,
)
from enums.component_type import ComponentType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def show_suggest_i_am_statement_component(
    coach_state: CoachState,
    params: ShowSuggestIAMStatementComponentParams,
    coach_message: ChatMessage,
):
    """
    Show the Suggest I Am Statement component to the user.

    Renders an editable suggested "I Am" statement with canned responses and
    an option for the user to submit their own text. Acceptance is handled
    separately via the Accept I Am component.
    """
    log.info(
        f"Showing Suggest I Am Statement component for user {coach_state.user.id} and identity {params.identity_id}"
    )

    identity = Identity.objects.filter(
        user=coach_state.user, id=params.identity_id
    ).first()

    component_identities = []
    if identity:
        component_identities.append(
            ComponentIdentity(
                id=str(identity.id),
                name=identity.name,
                category=identity.category,
            )
        )

    texts = [
        ComponentText(
            text=params.i_am_statement,
            location="after",
            source="i_am_suggestion",
        )
    ]

    persist_action_params = {
        "identity_id": params.identity_id,
        "i_am_statement": params.i_am_statement,
        "coach_message_id": str(coach_message.id),
    }

    update_action_params = {
        "id": params.identity_id,
        "i_am_statement": params.i_am_statement,
    }

    buttons = [
        ComponentButton(
            label="I love it",
            actions=[
                ComponentAction(
                    action=ActionType.PERSIST_SUGGEST_I_AM_STATEMENT_COMPONENT.value,
                    params=persist_action_params,
                ),
                ComponentAction(
                    action=ActionType.UPDATE_I_AM_STATEMENT.value,
                    params=update_action_params,
                ),
            ],
        ),
        ComponentButton(
            label="This needs more work",
            actions=[
                ComponentAction(
                    action=ActionType.PERSIST_SUGGEST_I_AM_STATEMENT_COMPONENT.value,
                    params=persist_action_params,
                ),
            ],
        ),
        ComponentButton(
            label="I came up with my own",
            actions=[
                ComponentAction(
                    action=ActionType.PERSIST_SUGGEST_I_AM_STATEMENT_COMPONENT.value,
                    params=persist_action_params,
                ),
                ComponentAction(
                    action=ActionType.UPDATE_I_AM_STATEMENT.value,
                    params=update_action_params,
                ),
            ],
        ),
    ]

    component = ComponentConfig(
        component_type=ComponentType.SUGGEST_I_AM_STATEMENT.value,
        texts=texts,
        identities=component_identities if component_identities else None,
        buttons=buttons,
    )

    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.SHOW_SUGGEST_I_AM_STATEMENT_COMPONENT.value,
        parameters=params.model_dump(),
        result_summary=(
            f"Showed Suggest I Am Statement component for identity {params.identity_id}"
        ),
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    log.info("Successfully built Suggest I Am Statement component")

    return component
