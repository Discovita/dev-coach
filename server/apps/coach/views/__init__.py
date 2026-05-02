"""
Coach views.

Exports:
    CoachViewSet: Public endpoint for authenticated users to send messages.
    AdminCoachViewSet: Admin endpoint to process messages on behalf of any user.
"""

from .admin_coach_view_set import AdminCoachViewSet
from .coach_view_set import CoachViewSet

__all__ = ["CoachViewSet", "AdminCoachViewSet"]
