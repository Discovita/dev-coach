"""
BreakAdmin

Admin configuration for the Break model in Django Admin Panel.
"""

from django.contrib import admin

from apps.coach_states.models import Break


class BreakAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Break model.

    Provides list view, filtering, and search for the soft-blocking pauses
    that open between coaching sessions.
    """

    list_display = (
        "id",
        "user",
        "triggered_by_session",
        "started_at",
        "ended_at",
        "is_open",
    )
    list_filter = ("triggered_by_session", "started_at", "ended_at")
    search_fields = ("user__email", "triggered_by_session")
    readonly_fields = ("started_at",)

    def is_open(self, obj: Break) -> bool:
        """True iff the break has not been closed (no `ended_at`)."""
        return obj.ended_at is None

    is_open.boolean = True
    is_open.short_description = "Open?"


def register_break_admin() -> None:
    """Register Break in Django Admin."""
    try:
        admin.site.register(Break, BreakAdmin)
    except admin.sites.AlreadyRegistered:
        pass  # Safe for dev reload
