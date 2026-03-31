"""
Admin registration for the TestScenario model.

See: apps/test_scenario/admin/__init__.py
"""

from django.contrib import admin

from apps.test_scenario.models import TestScenario


@admin.register(TestScenario)
class TestScenarioAdmin(admin.ModelAdmin):
    """Admin interface for managing test scenarios."""

    list_display = (
        "name",
        "description",
        "created_by",
        "created_at",
        "updated_at",
        "id",
    )
    search_fields = ("name", "description", "created_by__email")
    list_filter = ("created_by", "created_at")
    ordering = ("-created_at",)
