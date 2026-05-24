"""
Coach States — constants.

Static, code-only data used by the coach_states app and downstream callers
(action handlers, serializers, prompts).
"""

from apps.coach_states.constants.session_videos import (
    SESSION_VIDEOS,
    get_video,
)

__all__ = ["SESSION_VIDEOS", "get_video"]
