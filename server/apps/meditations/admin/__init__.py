"""
Django admin configuration for the meditations app.
"""

from apps.meditations.admin.meditation_admin import (
    MeditationAdmin,
    MeditationAssetAdmin,
    MeditationSegmentAdmin,
)

__all__ = ["MeditationAdmin", "MeditationSegmentAdmin", "MeditationAssetAdmin"]
