from django.contrib import admin
from .models import CoachState

@admin.register(CoachState)
class CoachStateAdmin(admin.ModelAdmin):
    """
    Admin configuration for the CoachState model.
    """
    list_display = ("id", "user", "current_phase", "current_identity", "proposed_identity", "identity_focus", "skipped_identity_categories", "updated_at")
    list_filter = ("current_phase", "updated_at")
    search_fields = ("user__email",)
    readonly_fields = ("updated_at",)
