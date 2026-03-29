"""
Django admin configuration for the test_scenario app.

Exports:
    TestScenarioAdmin: Admin interface for managing test scenarios.
"""

from apps.test_scenario.admin.test_scenario_admin import TestScenarioAdmin

__all__ = ["TestScenarioAdmin"]
