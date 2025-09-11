from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from enums.action_type import ActionType
from services.action_handler.models.params import ShowIntroductionCannedResponseComponentParams
from models.components.ComponentConfig import ComponentConfig, ComponentButton
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def show_introduction_canned_response_component(
    coach_state: CoachState,
    params: ShowIntroductionCannedResponseComponentParams,
    coach_message: ChatMessage,
):
    """
    Show introduction canned response component to the user.

    This action builds a component configuration that will be rendered
    on the frontend, providing pre-written response buttons for user convenience
    during the introduction phase.
    """
    log.info(f"Showing canned response component for user {coach_state.user.id}")

    # Build the component configuration
    # For now, we'll create some basic canned response buttons
    # In the future, these could be customized based on the current phase or context
    buttons = [
        ComponentButton(label="Yes"),
        ComponentButton(label="No"),
        ComponentButton(label="Tell me more"),
    ]

    component = ComponentConfig(buttons=buttons)

    # Log the action
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.SHOW_INTRODUCTION_CANNED_RESPONSE_COMPONENT.value,
        parameters=params.model_dump(),
        result_summary=f"Showed canned response component with {len(buttons)} buttons",
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    log.info(
        f"Successfully showed canned response component with {len(buttons)} buttons"
    )
    
    return component
