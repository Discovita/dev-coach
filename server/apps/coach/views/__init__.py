"""
Coach views.

Exports:
    CoachViewSet: Public endpoint for authenticated users to send messages.
    AdminCoachViewSet: Admin endpoint to process messages on behalf of any user.
    EvalViewSet: Runs the automated coach eval harness (POST /api/v1/eval/run).
"""

from .admin_coach_view_set import AdminCoachViewSet
from .coach_view_set import CoachViewSet
from .eval_view_set import EvalViewSet

__all__ = ["CoachViewSet", "AdminCoachViewSet", "EvalViewSet"]
