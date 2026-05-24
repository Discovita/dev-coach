from django.utils import timezone

from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from apps.coach_states.models import Break, CoachState
from enums.action_type import ActionType
from services.action_handler.models import EndBreakParams
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def end_break(
    coach_state: CoachState,
    params: EndBreakParams,
    coach_message: ChatMessage,
) -> None:
    """
    Close the user's single open `Break` by stamping `ended_at = now()`.

    User-button-only action — fires on the break card's "I'm Ready" button.
    PR 7's START_BREAK enforces at-most-one-open-break-per-user, so this
    handler safely uses `.filter().first()` and handles the no-open-break
    case as a no-op (defensive: a duplicate click on a stale break card
    shouldn't raise).

    Intro-emission logic (returning a SESSION_VIDEO ComponentConfig when
    `current_phase` is the first phase of a session with an unacked intro)
    is **PR 14's** responsibility — this PR keeps the handler scope to the
    basic close. Returns None so the skip-LLM rule does not fire from this
    action alone.
    """
    open_break = Break.objects.filter(
        user=coach_state.user, ended_at__isnull=True
    ).first()

    if open_break is None:
        log.debug(
            f"end_break called for user {coach_state.user.id} but no open "
            f"break exists — no-op"
        )
        return None

    open_break.ended_at = timezone.now()
    open_break.save(update_fields=["ended_at"])

    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.END_BREAK.value,
        parameters=params.model_dump(),
        result_summary=(
            f"Closed break {open_break.id} "
            f"(triggered_by_session='{open_break.triggered_by_session}')"
        ),
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )
    log.debug(
        f"Closed break {open_break.id} for user {coach_state.user.id} "
        f"(triggered_by_session={open_break.triggered_by_session})"
    )
    return None
