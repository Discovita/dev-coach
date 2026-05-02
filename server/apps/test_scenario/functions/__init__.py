"""
Business logic functions for the test_scenario app.

All test scenario operations are admin-only; there are no public functions.

Exports:
    instantiate_test_scenario: Creates all DB objects from a scenario template.
    freeze_user_session: Captures a live user session as a new test scenario.
    FreezeSessionError: Domain exception raised when session freezing fails.
"""

from apps.test_scenario.functions.admin import (
    FreezeSessionError,
    freeze_user_session,
    instantiate_test_scenario,
)

__all__ = [
    "instantiate_test_scenario",
    "freeze_user_session",
    "FreezeSessionError",
]
