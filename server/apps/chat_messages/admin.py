from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ChatMessage model.
    """
    list_display = ("id", "user", "role", "content", "test_scenario_display", "timestamp")
    list_filter = ("role", "test_scenario", "timestamp")
    search_fields = ("content", "user__email", "test_scenario__name")
    readonly_fields = ("timestamp",)

    def test_scenario_display(self, obj):
        """Display the name of the associated test scenario, if any."""
        return obj.test_scenario.name if obj.test_scenario else None
    test_scenario_display.short_description = "Test Scenario"
    test_scenario_display.admin_order_field = "test_scenario__name"
