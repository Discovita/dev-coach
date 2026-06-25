"""
get_meditations — returns the current Meditations feature config.

Reads from Django settings (env-driven). The return shape is the API contract.

Used by:
- apps/core/views/meditations_view_set.py
  (GET /api/v1/core/public/meditations)
"""

from typing import TypedDict

from django.conf import settings


class MeditationsConfig(TypedDict):
    enabled: bool


def get_meditations() -> MeditationsConfig:
    """
    Return the Meditations config as a JSON-serializable dict.

    Always returns the full shape regardless of whether the feature is
    enabled — the frontend decides what to render based on `enabled`.
    """
    return {
        "enabled": settings.MEDITATIONS_ENABLED,
    }
