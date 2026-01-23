"""
Signal handlers for the CoachStates app.

This module imports all signal handlers to ensure they are registered
when the app is ready.

Signals:
- create_coach_state_for_new_user: Auto-creates CoachState for new users
"""

# Import all signal handlers to register them
from apps.coach_states.signals.create_coach_state_for_new_user import (
    create_coach_state_for_new_user,
)

__all__ = ["create_coach_state_for_new_user"]
