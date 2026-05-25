"""
Utilities for the `coach_states` app.

Currently exports the session-video helpers used by the
`transition_phase` action handler (PR 13) and the `end_break` action
handler (PR 14) when the Coaching Phase Videos feature is enabled.
"""

from apps.coach_states.utils.session_video_helpers import (
    intro_component_for,
    outro_component_for,
    should_emit_intro,
    should_emit_outro,
)

__all__ = [
    "should_emit_outro",
    "should_emit_intro",
    "outro_component_for",
    "intro_component_for",
]
