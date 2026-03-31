"""
Django AppConfig for the test_scenario app.
"""

from django.apps import AppConfig


class TestScenarioConfig(AppConfig):
    """Configuration for the test_scenario app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.test_scenario"
    verbose_name = "Test Scenarios"
