"""
Core app viewsets.
"""

from apps.core.views.coaching_phase_videos_view_set import (
    CoachingPhaseVideosViewSet,
)
from apps.core.views.core_view_set import CoreViewSet

__all__ = ["CoachingPhaseVideosViewSet", "CoreViewSet"]
