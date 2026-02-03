"""
CoachStateAdmin

Admin configuration for CoachState model in Django Admin Panel.
"""

from django.contrib import admin

from apps.coach_states.models import CoachState


class CoachStateAdmin(admin.ModelAdmin):
    """
    Admin configuration for the CoachState model.

    Provides list view, filtering, and search capabilities for coach states
    in the Django Admin Panel.
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
    list_filter = ("current_phase", "identity_focus", "updated_at", "test_scenario")
    search_fields = ("user__email", "test_scenario__name")
    readonly_fields = ("updated_at",)

    def test_scenario_display(self, obj: CoachState) -> str | None:
        """
        Display the name of the associated test scenario, if any.

        Args:
            obj: The CoachState instance

        Returns:
            Test scenario name or None
        """
        return obj.test_scenario.name if obj.test_scenario else None

    test_scenario_display.short_description = "Test Scenario"
    test_scenario_display.admin_order_field = "test_scenario__name"


def register_coach_state_admin() -> None:
    """Register CoachState in Django Admin."""
    try:
        admin.site.register(CoachState, CoachStateAdmin)
    except admin.sites.AlreadyRegistered:
        pass  # Safe for dev reload
