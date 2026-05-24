from django.core.exceptions import ValidationError

from apps.actions.models import Action
from apps.chat_messages.models import ChatMessage
from apps.coach_states.constants.session_videos import SESSION_VIDEOS
from apps.coach_states.models import CoachState
from enums.action_type import ActionType
from services.action_handler.models import AcknowledgeSessionVideoParams
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def acknowledge_session_video(
    coach_state: CoachState,
    params: AcknowledgeSessionVideoParams,
    coach_message: ChatMessage,
) -> None:
    """
    Append `params.video_key` to `coach_state.shown_videos` after a user
    clicks Continue on a session video card.

    User-button-only action — the LLM never emits it. The frontend bakes the
    video_key into the Continue button when constructing the SESSION_VIDEO
    card, so an unknown key here means a registry/component drift bug rather
    than user input — raise immediately so it surfaces in logs.
    """
    video_key = params.video_key

    if video_key not in SESSION_VIDEOS:
        raise ValidationError(
            f"Unknown session video key: '{video_key}'. "
            f"Must be one of: {sorted(SESSION_VIDEOS.keys())}"
        )

    existing = set(coach_state.shown_videos or [])
    if video_key in existing:
        log.debug(
            f"Video '{video_key}' already in shown_videos for user "
            f"{coach_state.user.id}, skipping (idempotency protection)"
        )
        return

    coach_state.shown_videos = list(coach_state.shown_videos or []) + [video_key]
    coach_state.save()

    Action.objects.create(
        user=coach_state.user,
        action_type=ActionType.ACKNOWLEDGE_SESSION_VIDEO.value,
        parameters=params.model_dump(),
        result_summary=f"Acknowledged session video '{video_key}'",
        coach_message=coach_message,
        test_scenario=(
            coach_state.user.test_scenario
            if hasattr(coach_state.user, "test_scenario")
            else None
        ),
    )
    log.debug(f"Appended '{video_key}' to shown_videos for user {coach_state.user.id}")
