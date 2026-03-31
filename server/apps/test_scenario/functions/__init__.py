"""
Business logic functions for the test_scenario app.

Exports:
    instantiate_test_scenario: Creates all DB objects from a scenario template.
    freeze_user_session: Captures a live user session as a new test scenario.
"""

from apps.test_scenario.functions.freeze_user_session import freeze_user_session
from apps.test_scenario.functions.instantiate_test_scenario import (
    instantiate_test_scenario,
)

__all__ = [
    "instantiate_test_scenario",
    "freeze_user_session",
]
