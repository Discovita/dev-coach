"""
Django Admin configuration for the Action model.
"""

from django.contrib import admin

from apps.actions.models import Action


class ActionAdmin(admin.ModelAdmin):
    """
    Read-focused admin for Action audit rows (no manual add/change).
    """

    list_display = [
        "action_type",
        "user",
        "timestamp",
        "updated_at",
        "result_summary",
        "test_scenario",
        "coach_message_preview",
    ]

    list_filter = [
        "action_type",
        "timestamp",
        "updated_at",
        "test_scenario",
        "user",
    ]

    search_fields = [
        "user__email",
        "action_type",
        "parameters",
    ]

    readonly_fields = [
        "id",
        "timestamp",
        "updated_at",
    ]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "id",
                    "user",
                    "action_type",
                    "timestamp",
                    "updated_at",
                )
            },
        ),
        (
            "Action Details",
            {"fields": ("parameters", "result_summary", "coach_message")},
        ),
        ("Test Scenario", {"fields": ("test_scenario",), "classes": ("collapse",)}),
    )

    def coach_message_preview(self, obj: Action) -> str:
        if obj.coach_message:
            content = obj.coach_message.content
            return content[:50] + "..." if len(content) > 50 else content
        return "No message"

    coach_message_preview.short_description = "Coach Message Preview"

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


def register_action_admin() -> None:
    """Register Action in Django Admin."""
    try:
        admin.site.register(Action, ActionAdmin)
    except admin.sites.AlreadyRegistered:
        pass
