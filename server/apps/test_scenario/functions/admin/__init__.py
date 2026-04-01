"""
test_scenario app admin functions.

Exports:
    freeze_user_session: Captures a live user session as a new test scenario.
    FreezeSessionError: Domain exception raised when session freezing fails.
    instantiate_test_scenario: Creates all DB objects from a scenario template.
"""

from apps.test_scenario.functions.admin.freeze_user_session import (
    FreezeSessionError,
    freeze_user_session,
)
from apps.test_scenario.functions.admin.instantiate_test_scenario import (
    instantiate_test_scenario,
)

__all__ = [
    "FreezeSessionError",
    "freeze_user_session",
    "instantiate_test_scenario",
]
