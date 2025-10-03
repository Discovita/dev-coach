from apps.coach_states.models import CoachState
from apps.chat_messages.models import ChatMessage
from apps.actions.models import Action
from enums.action_type import ActionType
from services.action_handler.models.params import (
    ShowWarmupTextComponentParams,
)
from models.components.ComponentConfig import ComponentConfig, ComponentText
from services.logger import configure_logging

log = configure_logging(__name__, log_level="DEBUG")


def show_warmup_text_component(
    coach_state: CoachState,
    params: ShowWarmupTextComponentParams,
    coach_message: ChatMessage,
):
    """
    Show a warmup text component that injects markdown before/after the coach message.

    This builds a ComponentConfig with a single text block sourced from the user's
    coach state (who_you_are and who_you_want_to_be) to provide context.
    """

    if not params.enabled:
        log.info(
            "Warmup text component disabled by params; returning empty buttons config"
        )
        return ComponentConfig(buttons=[])

    log.info(f"Building warmup text for user {coach_state.user.id}")

    who_you_are = coach_state.who_you_are or []
    who_you_want_to_be = coach_state.who_you_want_to_be or []

    sections: list[str] = ["Here's what we've got so far:"]

    if who_you_are:
        who_you_are_md = ", ".join([f"{item}" for item in who_you_are])
        sections.append("\n**Who you are:** " + who_you_are_md)

    if who_you_want_to_be:
        who_you_want_to_be_md = ", ".join([f"{item}" for item in who_you_want_to_be])
        sections.append("\n**Who you want to be:** " + who_you_want_to_be_md)

    sections.append("\n---")

    # If no sections beyond the title, do not include any text blocks
    if len(sections) == 1:
        return ComponentConfig(buttons=[])

    markdown = "\n\n".join(sections)

    component = ComponentConfig(
        texts=[ComponentText(text=markdown, location="before", source="warmup")],
        buttons=[],
    )

    # Log the action
    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.SHOW_WARMUP_TEXT_COMPONENT.value,
        parameters=params.model_dump(),
        result_summary=(f"Showed warmup text component"),
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )

    log.info("Successfully built warmup text component")

    return component
