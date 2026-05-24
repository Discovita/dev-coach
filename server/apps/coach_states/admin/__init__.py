"""
Coach States - Admin Package

IMPORTANT: Django admin autodiscover imports `apps.<app>.admin`.
Because this app has an `admin/` package (directory), Django imports
THIS package. We register the ModelAdmins at import time.
"""

from .break_admin import register_break_admin
from .coach_state_admin import register_coach_state_admin

# Register immediately on import
register_coach_state_admin()
register_break_admin()

__all__ = ["register_break_admin", "register_coach_state_admin"]
