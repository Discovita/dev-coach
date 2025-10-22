from django.contrib import admin
from .models import Identity


@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Identity model.
    """

    list_display = (
        "id",
        "user",
        "name",
        "i_am_statement",
        "visualization",
        "state",
        "notes",
        "category",
        "test_scenario_display",
        "created_at",
        "updated_at",
    )
    list_filter = ("state", "category", "created_at", "test_scenario")
    search_fields = ("user__email", "name", "test_scenario__name")
    readonly_fields = ("created_at", "updated_at")

    def test_scenario_display(self, obj):
        """Display the name of the associated test scenario, if any."""
        return obj.test_scenario.name if obj.test_scenario else None
    test_scenario_display.short_description = "Test Scenario"
    test_scenario_display.admin_order_field = "test_scenario__name"
