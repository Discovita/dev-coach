from django.contrib import admin
from .models import CoachState


@admin.register(CoachState)
class CoachStateAdmin(admin.ModelAdmin):
    """
    Admin configuration for the CoachState model.
    """

    list_display = (
        "id",
        "user",
        "current_phase",
        "current_identity",
        "proposed_identity",
        "identity_focus",
        "skipped_identity_categories",
        "test_scenario_display",
        "updated_at",
    )
    list_filter = ("current_phase", "updated_at", "test_scenario")
    search_fields = ("user__email", "test_scenario__name")
    readonly_fields = ("updated_at",)

    def test_scenario_display(self, obj):
        """Display the name of the associated test scenario, if any."""
        return obj.test_scenario.name if obj.test_scenario else None

    test_scenario_display.short_description = "Test Scenario"
    test_scenario_display.admin_order_field = "test_scenario__name"
