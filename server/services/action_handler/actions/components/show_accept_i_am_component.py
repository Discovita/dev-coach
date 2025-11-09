from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from enums.action_type import ActionType
from services.action_handler.models.params import (
    ShowAcceptIAMComponentParams,
)
from models.components.ComponentConfig import (
    ComponentConfig,
    ComponentButton,
    ComponentAction,
)
from enums.component_type import ComponentType
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def show_accept_i_am_component(
    coach_state: CoachState,
    params: ShowAcceptIAMComponentParams,
    coach_message: ChatMessage,
):
    """
    Show the Accept I Am component to the user.

    Renders two choices:
    - "I love it!" which updates the identity i_am_statement and accepts the i_am_statement
    - "Let's keep working on it" which sends the label back as the user's message
    """
    log.info(f"Showing Accept I Am component for user {coach_state.user.id}")

    buttons = [
        ComponentButton(
            label="I love it!",
            actions=[
                ComponentAction(
                    action=ActionType.UPDATE_I_AM_STATEMENT.value,
                    params={"id": params.id, "i_am_statement": params.i_am_statement},
                ),
                ComponentAction(
                    action=ActionType.ACCEPT_I_AM_STATEMENT.value,
                    params={"id": params.id},
                ),
            ],
        ),
        ComponentButton(label="Let's keep working on it"),
    ]

    component = ComponentConfig(component_type=ComponentType.ACCEPT_I_AM, buttons=buttons)

    # Log the action
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.SHOW_ACCEPT_I_AM_COMPONENT.value,
        parameters=params.model_dump(),
        result_summary="Showed Accept I Am component",
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    log.info("Successfully showed Accept I Am component")

    return component


