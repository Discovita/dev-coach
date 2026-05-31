from typing import Optional

from django.conf import settings
from django.utils import timezone

from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from apps.coach_states.models import Break, CoachState
from apps.coach_states.utils.session_video_helpers import (
    intro_component_for,
    should_emit_intro,
)
from enums.action_type import ActionType
from enums.coaching_phase import session_of
from enums.component_type import ComponentType
from enums.message_role import MessageRole
from models.components.ComponentConfig import ComponentConfig
from services.action_handler.models import EndBreakParams
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def end_break(
    coach_state: CoachState,
    params: EndBreakParams,
    coach_message: ChatMessage,
) -> Optional[ComponentConfig]:
    """
    Close the user's single open `Break` by stamping `ended_at = now()`,
    and (PR 14) optionally return the SESSION_VIDEO intro for the new
    session when the user has just returned from a between-session break.

    User-button-only action — fires on the break card's "I'm Ready" button.
    PR 7's START_BREAK enforces at-most-one-open-break-per-user, so this
    handler safely uses `.filter().first()` and handles the no-open-break
    case as a no-op (defensive: a duplicate click on a stale break card
    shouldn't raise).

    Intro-emission (flag-gated by `settings.COACHING_PHASE_VIDEOS_ENABLED`):
    after stamping `ended_at`, if `current_phase` is the first phase of a
    session whose intro hasn't been acked yet, return a `SESSION_VIDEO`
    `ComponentConfig` for that intro. The orchestrator's skip-LLM-on-
    component rule then fires — the LLM doesn't run this turn. The
    orchestrator (`apps/coach/functions/public/process_message.py`) is
    responsible for creating the coach `ChatMessage` and persisting the
    returned component_config on it; this handler does NOT touch
    `coach_message.component_config` (the `coach_message` param here is
    the USER's "I'm ready" message, not a coach message).
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

    # Mutate the original SESSION_BREAK message's component_config so the
    # historical card renders as a compact "Took a break · {duration}" line
    # instead of the full active-break UI. Strip `buttons` so the closed
    # card can't redispatch END_BREAK (mirrors the standard
    # makeComponentDisplayOnly convention for persistent components).
    #
    # Primary lookup: `Break.coach_message` FK. Fallback: walk back to the
    # most recent SESSION_BREAK card that isn't already closed. The
    # fallback exists because START_BREAK runs BEFORE the orchestrator's
    # skip-LLM rule creates the SESSION_BREAK coach message — so
    # `Break.coach_message` is `None` for Breaks created before
    # process_message.py was taught to link them retroactively. PR 7's
    # one-open-break-per-user invariant means at most one SESSION_BREAK
    # card with `closed != True` exists at any time, so the fallback is
    # unambiguous.
    break_msg: Optional[ChatMessage] = None
    if open_break.coach_message_id:
        break_msg = open_break.coach_message
    else:
        candidate = (
            ChatMessage.objects.filter(
                user=coach_state.user,
                role=MessageRole.COACH,
                component_config__component_type=ComponentType.SESSION_BREAK.value,
            )
            .order_by("-timestamp")
            .first()
        )
        if (
            candidate is not None
            and (candidate.component_config or {}).get("closed") is not True
        ):
            break_msg = candidate

    if break_msg is not None:
        existing = break_msg.component_config or {}
        break_msg.component_config = {
            **existing,
            "closed": True,
            "started_at": open_break.started_at.isoformat(),
            "ended_at": open_break.ended_at.isoformat(),
            "buttons": None,
        }
        break_msg.save(update_fields=["component_config"])

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

    if not settings.COACHING_PHASE_VIDEOS_ENABLED:
        return None

    if not should_emit_intro(
        coach_state.current_phase, coach_state.shown_videos or []
    ):
        return None

    component = intro_component_for(session_of(coach_state.current_phase))
    log.debug(
        f"Returning {component.component_type}({component.video_key}) after "
        f"end_break for user {coach_state.user.id} at phase "
        f"{coach_state.current_phase}"
    )
    return component
