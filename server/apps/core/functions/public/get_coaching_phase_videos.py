"""
get_coaching_phase_videos — returns the current Coaching Phase Videos config.

Reads from Django settings. The return shape is the API contract.

Used by:
- apps/core/views/coaching_phase_videos_view_set.py
  (GET /api/v1/core/public/coaching-phase-videos)
"""

from typing import TypedDict

from django.conf import settings


class CoachingPhaseVideosConfig(TypedDict):
    enabled: bool


def get_coaching_phase_videos() -> CoachingPhaseVideosConfig:
    """
    Return the Coaching Phase Videos config as a JSON-serializable dict.

    Always returns the full shape regardless of whether the feature is
    enabled — the frontend decides what to render based on `enabled`.
    """
    return {
        "enabled": settings.COACHING_PHASE_VIDEOS_ENABLED,
    }
