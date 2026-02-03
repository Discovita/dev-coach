"""
Coach States - Admin Package

IMPORTANT: Django admin autodiscover imports `apps.<app>.admin`.
Because this app has an `admin/` package (directory), Django imports
THIS package. We register the ModelAdmin at import time.
"""

from .coach_state_admin import register_coach_state_admin

# Register immediately on import
register_coach_state_admin()

__all__ = ["register_coach_state_admin"]
