from django.core.exceptions import ValidationError

from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from apps.coach_states.models import Break, CoachState
from enums.action_type import ActionType
from enums.coaching_phase import SESSIONS
from enums.component_type import ComponentType
from models.components.ComponentConfig import (
    ComponentAction,
    ComponentButton,
    ComponentConfig,
)
from services.action_handler.models import StartBreakParams
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def start_break(
    coach_state: CoachState,
    params: StartBreakParams,
    coach_message: ChatMessage,
) -> ComponentConfig:
    """
    Open a `Break` row for the user and return the SESSION_BREAK component
    that renders the break card with an "I'm Ready" button.

    User-button-only action — fires as the second action on the outro
    video's Continue button (after ACKNOWLEDGE_SESSION_VIDEO). The
    `session_key` parameter is the session being LEFT, not the user's
    current_phase session (which has already advanced by the time this
    handler runs).

    Hard invariant: at most one open `Break` per user at any time. If the
    user already has an open break, raises `ValidationError` rather than
    silently reusing or overlapping. The PR 8 / PR 14 `END_BREAK` handler
    is responsible for closing breaks.
    """
    session_key = params.session_key

    if session_key not in SESSIONS:
        raise ValidationError(
            f"Unknown session key: '{session_key}'. "
            f"Must be one of: {sorted(SESSIONS.keys())}"
        )

    if Break.objects.filter(user=coach_state.user, ended_at__isnull=True).exists():
        raise ValidationError(
            f"Cannot start a new break for user {coach_state.user.id}: "
            f"an open break already exists. Close it via END_BREAK first."
        )

    break_row = Break.objects.create(
        user=coach_state.user,
        triggered_by_session=session_key,
        coach_message=coach_message,
    )

    component_config = ComponentConfig(
        component_type=ComponentType.SESSION_BREAK.value,
        buttons=[
            ComponentButton(
                label="I'm Ready",
                actions=[
                    ComponentAction(
                        action=ActionType.END_BREAK.value,
                        params={},
                    ),
                ],
            ),
        ],
    )

    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.START_BREAK.value,
        parameters=params.model_dump(),
        result_summary=(
            f"Opened break {break_row.id} after session '{session_key}'"
        ),
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )
    log.debug(
        f"Opened break {break_row.id} (triggered_by_session={session_key}) "
        f"for user {coach_state.user.id}"
    )
    return component_config
