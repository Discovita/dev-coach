"""
Admin registration for the UserNote model.

See: apps/user_notes/admin/__init__.py
"""

from django.contrib import admin

from apps.user_notes.models import UserNote


@admin.register(UserNote)
class UserNoteAdmin(admin.ModelAdmin):
    """Admin interface for managing user notes."""

    list_display = ("user", "note", "created_at", "test_scenario_display")
    list_filter = ("test_scenario", "created_at")
    search_fields = ("user__email", "note", "test_scenario__name")
    readonly_fields = ("created_at",)

    def test_scenario_display(self, obj):
        """Display the name of the associated test scenario, if any."""
        return obj.test_scenario.name if obj.test_scenario else None

    test_scenario_display.short_description = "Test Scenario"
    test_scenario_display.admin_order_field = "test_scenario__name"
