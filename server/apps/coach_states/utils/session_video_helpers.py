"""
Helpers for emitting SESSION_VIDEO `ComponentConfig`s at session boundaries.

Used by:
  - `services.action_handler.actions.transition_phase` (PR 13) — attach an
    outro or intro card to the LLM's transition coach message.
  - `services.action_handler.actions.end_break` (PR 14) — return the next
    session's intro card after closing a break.

Decision logic lives here (`should_emit_*` predicates + `*_component_for`
builders). The caller owns the feature-flag check and the "outro wins over
intro" precedence. Keeping the helpers small and side-effect-free means
PR 13 and PR 14 share one source of truth for what a video card looks like.
"""

from typing import Iterable, Optional

from apps.coach_states.constants.session_videos import get_video, get_video_url
from enums.action_type import ActionType
from enums.coaching_phase import (
    CoachingPhase,
    SESSIONS,
    is_first_phase_of_session,
    is_last_phase_of_session,
    session_of,
)
from enums.component_type import ComponentType
from models.components.ComponentConfig import (
    ComponentAction,
    ComponentButton,
    ComponentConfig,
)


def _try_session_of(phase: Optional[CoachingPhase]) -> Optional[str]:
    """`session_of()` that returns None for phases outside the SESSIONS map.

    `SYSTEM_CONTEXT` is a meta-phase that doesn't belong to any session;
    callers shouldn't crash when they happen to see it.
    """
    if phase is None:
        return None
    try:
        return session_of(phase)
    except ValueError:
        return None


def should_emit_outro(old_phase: Optional[CoachingPhase]) -> bool:
    """True iff leaving `old_phase` triggers an outro video.

    The boundary is "last phase of a session that has an outro configured."
    Outros are not idempotency-checked: each session's outro fires the one
    time the user leaves that session (a re-transition into and back out of
    the same session is not a flow the runtime produces today).
    """
    leaving_session = _try_session_of(old_phase)
    if leaving_session is None:
        return False
    if not is_last_phase_of_session(old_phase):
        return False
    return SESSIONS[leaving_session]["outro"] is not None


def should_emit_intro(
    new_phase: Optional[CoachingPhase],
    shown_videos: Iterable[str],
) -> bool:
    """True iff entering `new_phase` triggers an unacknowledged intro video.

    Intros are idempotency-checked against `shown_videos` so the same intro
    can't be re-emitted if the user transitions back into the first phase
    of a session whose intro they've already watched.
    """
    entering_session = _try_session_of(new_phase)
    if entering_session is None:
        return False
    if not is_first_phase_of_session(new_phase):
        return False
    intro_key = SESSIONS[entering_session]["intro"]
    if intro_key is None:
        return False
    return intro_key not in set(shown_videos or [])


def outro_component_for(leaving_session: str) -> ComponentConfig:
    """Build the SESSION_VIDEO `ComponentConfig` for `leaving_session`'s outro.

    The Continue button carries
    `[ACKNOWLEDGE_SESSION_VIDEO(outro_key), START_BREAK(leaving_session)]`.
    `session_key` on `START_BREAK` is the session being LEFT — by the time
    the user clicks Continue on this card, `current_phase` has already
    advanced into the next session, so deriving the session_key from current
    state would name the wrong one.
    """
    outro_key = SESSIONS[leaving_session]["outro"]
    if outro_key is None:
        raise ValueError(
            f"Session '{leaving_session}' has no outro video configured."
        )
    return ComponentConfig(
        component_type=ComponentType.SESSION_VIDEO.value,
        video_key=outro_key,
        video_name=get_video(outro_key)["name"],
        video_url=get_video_url(outro_key),
        buttons=[
            ComponentButton(
                label="Continue",
                actions=[
                    ComponentAction(
                        action=ActionType.ACKNOWLEDGE_SESSION_VIDEO.value,
                        params={"video_key": outro_key},
                    ),
                    ComponentAction(
                        action=ActionType.START_BREAK.value,
                        params={"session_key": leaving_session},
                    ),
                ],
            ),
        ],
    )


def intro_component_for(entering_session: str) -> ComponentConfig:
    """Build the SESSION_VIDEO `ComponentConfig` for `entering_session`'s intro.

    The Continue button carries only `[ACKNOWLEDGE_SESSION_VIDEO(intro_key)]`.
    There is no break after an intro — the user watches, ACKs, then the LLM
    speaks the session's first prompt on the next turn.
    """
    intro_key = SESSIONS[entering_session]["intro"]
    if intro_key is None:
        raise ValueError(
            f"Session '{entering_session}' has no intro video configured."
        )
    return ComponentConfig(
        component_type=ComponentType.SESSION_VIDEO.value,
        video_key=intro_key,
        video_name=get_video(intro_key)["name"],
        video_url=get_video_url(intro_key),
        buttons=[
            ComponentButton(
                label="Continue",
                actions=[
                    ComponentAction(
                        action=ActionType.ACKNOWLEDGE_SESSION_VIDEO.value,
                        params={"video_key": intro_key},
                    ),
                ],
            ),
        ],
    )
